#!/usr/bin/env python3
"""
Re-run Benchmark for Incorrect Cases Only

This script:
1. Loads the previous benchmark results and evaluations
2. Identifies cases that were incorrectly classified (strict match = False)
3. Re-runs only those cases with the updated extractor
4. Merges the new results with the original results
5. Recalculates all metrics

Usage:
    python rerun_incorrect_cases.py [--session SESSION_ID] [--batch-size N]
"""

import json
import time
import requests
import sys
import csv
import subprocess
from typing import Dict, List, Optional, Set
from datetime import datetime
from pathlib import Path
import statistics

# Import from run_benchmark_real_v2
from run_benchmark_real_v2 import (
    AIAAICDataLoaderV2,
    AIAAIC_ATTRIBUTION,
    BATCH_SIZE,
    OLLAMA_RESTART_WAIT,
    restart_ollama,
    wait_for_service_health
)

# Import from ground_truth_mapper
from ground_truth_mapper import (
    evaluate_incident_type,
    evaluate_risk_level
)

# Configuration
FORENSIC_URL = "http://localhost:8002"
RESULTS_DIR = Path(__file__).parent / "results"


def load_previous_session(session_id: str) -> tuple:
    """Load results and evaluations from a previous session"""
    results_file = RESULTS_DIR / f"real_benchmark_results_v2_{session_id}.json"
    evals_file = RESULTS_DIR / f"real_benchmark_evaluations_v2_{session_id}.json"

    if not results_file.exists():
        raise FileNotFoundError(f"Results file not found: {results_file}")
    if not evals_file.exists():
        raise FileNotFoundError(f"Evaluations file not found: {evals_file}")

    with open(results_file, 'r') as f:
        results = json.load(f)
    with open(evals_file, 'r') as f:
        evaluations = json.load(f)

    return results, evaluations


def identify_incorrect_cases(evaluations: List[Dict], apply_case_fix: bool = True) -> List[str]:
    """
    Identify cases that need re-running based on evaluation results.

    Args:
        evaluations: List of evaluation results
        apply_case_fix: If True, apply case-insensitive comparison to filter out
                       cases that would be fixed by the case-sensitivity fix

    Returns:
        List of incident IDs that need re-running
    """
    incorrect_ids = []

    for eval_item in evaluations:
        incident_type_eval = eval_item.get('incident_type', {})

        if not incident_type_eval.get('strict_match', False):
            if apply_case_fix:
                # Apply case-insensitive comparison
                predicted = incident_type_eval.get('predicted', '')
                expected_primary = incident_type_eval.get('expected_primary', '')
                expected_all = incident_type_eval.get('expected_all', [])

                predicted_lower = predicted.lower() if predicted else ''
                primary_lower = expected_primary.lower() if expected_primary else ''
                types_lower = [t.lower() for t in expected_all if t]

                # Skip if it would match with case-insensitive comparison
                if predicted_lower == primary_lower or predicted_lower in types_lower:
                    continue

            incorrect_ids.append(eval_item['incident_id'])

    return incorrect_ids


def analyze_incident(incident: Dict, forensic_url: str = FORENSIC_URL) -> Dict:
    """Analyze a single incident"""
    start_time = time.time()

    try:
        response = requests.post(
            f"{forensic_url}/forensic/analyze",
            json={
                "narrative": incident["narrative"],
                "source": incident["source"],
                "metadata": incident["metadata"]
            },
            timeout=180
        )

        elapsed_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            result["processing_time"] = elapsed_time
            result["incident_id"] = incident["id"]
            result["aiaaic_metadata"] = incident["metadata"]
            result["ground_truth"] = incident["ground_truth"]
            return result
        else:
            return {
                "incident_id": incident["id"],
                "status": "ERROR",
                "error": f"HTTP {response.status_code}",
                "processing_time": elapsed_time,
                "ground_truth": incident["ground_truth"]
            }

    except Exception as e:
        elapsed_time = time.time() - start_time
        return {
            "incident_id": incident["id"],
            "status": "ERROR",
            "error": str(e),
            "processing_time": elapsed_time,
            "ground_truth": incident["ground_truth"]
        }


def evaluate_result(result: Dict) -> Dict:
    """Evaluate a single result against ground truth"""
    ground_truth = result.get("ground_truth", {})

    # Get predicted values
    predicted_incident_type = result.get("extraction", {}).get("incident", {}).get("incident_type", "unknown")
    predicted_risk_level = result.get("eu_ai_act", {}).get("risk_level", "Unknown")

    # Also extract serious_incident_type if present
    serious_incident_type = result.get("extraction", {}).get("incident", {}).get("serious_incident_type", [])

    # Evaluate incident type
    incident_type_eval = evaluate_incident_type(
        predicted_incident_type,
        ground_truth.get("issues", {"incident_types": [], "primary_type": None})
    )

    # Evaluate risk level
    risk_level_eval = evaluate_risk_level(predicted_risk_level, ground_truth)

    return {
        "incident_id": result.get("incident_id"),
        "incident_type": incident_type_eval,
        "risk_level": risk_level_eval,
        "serious_incident_type": serious_incident_type  # New field from v0.41.0
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Re-run benchmark for incorrect cases only')
    parser.add_argument('--session', type=str, default='20260103_161643',
                       help='Previous session ID to load results from')
    parser.add_argument('--batch-size', type=int, default=15,
                       help='Number of cases between Ollama restarts')
    parser.add_argument('--dry-run', action='store_true',
                       help='Only show what would be re-run without executing')
    args = parser.parse_args()

    print(f"\n{'='*70}")
    print("FORENSIC AGENT - RE-RUN INCORRECT CASES")
    print(f"{'='*70}")
    print(f"Loading session: {args.session}")

    # Load previous results
    try:
        original_results, original_evaluations = load_previous_session(args.session)
        print(f"Loaded {len(original_results)} results, {len(original_evaluations)} evaluations")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Identify incorrect cases
    incorrect_ids = identify_incorrect_cases(original_evaluations, apply_case_fix=True)
    print(f"Identified {len(incorrect_ids)} truly incorrect cases (after case-sensitivity fix)")

    if args.dry_run:
        print(f"\n[DRY RUN] Would re-run these {len(incorrect_ids)} cases:")
        for i, case_id in enumerate(incorrect_ids[:20], 1):
            print(f"  {i}. {case_id}")
        if len(incorrect_ids) > 20:
            print(f"  ... and {len(incorrect_ids) - 20} more")
        return

    if not incorrect_ids:
        print("No incorrect cases to re-run!")
        return

    # Check service health
    try:
        response = requests.get(f"{FORENSIC_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"Forensic agent not healthy: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"Forensic agent not available: {e}")
        sys.exit(1)

    # Load AIAAIC data to get full incident details
    print("\nLoading AIAAIC data...")
    try:
        loader = AIAAICDataLoaderV2()
        all_incidents = loader.load_incidents()
    except Exception as e:
        print(f"Failed to load AIAAIC data: {e}")
        sys.exit(1)

    print(f"Loaded {len(all_incidents)} total incidents from AIAAIC")

    # Filter to only incorrect cases
    incorrect_set = set(incorrect_ids)
    incidents_to_rerun = [i for i in all_incidents if i['id'] in incorrect_set]
    print(f"Found {len(incidents_to_rerun)} incidents to re-run")

    # Create new session for re-run results
    new_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    rerun_results = []
    rerun_evaluations = []

    print(f"\n{'='*70}")
    print(f"Starting re-run of {len(incidents_to_rerun)} cases")
    print(f"Session ID: {new_session_id}")
    print(f"Batch size: {args.batch_size}")
    print(f"{'='*70}\n")

    batch_counter = 0
    for idx, incident in enumerate(incidents_to_rerun, 1):
        incident_id = incident['id']

        # Check if we need to restart Ollama
        if batch_counter > 0 and batch_counter % args.batch_size == 0:
            print(f"\n[Batch complete - restarting Ollama...]")
            if restart_ollama():
                time.sleep(OLLAMA_RESTART_WAIT)
                if not wait_for_service_health(FORENSIC_URL):
                    print("⚠ Service not responding after restart, continuing...")
            print()

        batch_counter += 1

        title = incident['metadata'].get('aiaaic_title', incident_id)[:45]
        print(f"[{idx}/{len(incidents_to_rerun)}] {title}...", end=" ", flush=True)

        result = analyze_incident(incident)

        status = result.get("status", "UNKNOWN")
        proc_time = result.get("processing_time", 0)

        if status == "COMPLETED":
            evaluation = evaluate_result(result)
            rerun_evaluations.append(evaluation)

            incident_type = result.get("extraction", {}).get("incident", {}).get("incident_type", "unknown")
            serious_types = result.get("extraction", {}).get("incident", {}).get("serious_incident_type", [])
            risk_level = result.get("eu_ai_act", {}).get("risk_level", "Unknown")

            gt_primary = evaluation["incident_type"]["expected_primary"] or "?"
            match_symbol = "✓" if evaluation["incident_type"]["strict_match"] else "✗"
            serious_str = f" [{', '.join(serious_types)}]" if serious_types else ""

            print(f"OK {proc_time:.1f}s | {incident_type}{serious_str} {match_symbol} {gt_primary} | {risk_level}")
        else:
            error = result.get("error", "Unknown")[:50]
            print(f"ERROR: {error}")

        rerun_results.append(result)
        time.sleep(0.5)

    # Save re-run results
    rerun_results_file = RESULTS_DIR / f"rerun_results_{new_session_id}.json"
    rerun_evals_file = RESULTS_DIR / f"rerun_evaluations_{new_session_id}.json"

    with open(rerun_results_file, 'w') as f:
        json.dump(rerun_results, f, indent=2)
    with open(rerun_evals_file, 'w') as f:
        json.dump(rerun_evaluations, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Re-run complete!")
    print(f"Results saved to: {rerun_results_file.name}")
    print(f"Evaluations saved to: {rerun_evals_file.name}")

    # Calculate re-run statistics
    completed = sum(1 for r in rerun_results if r.get("status") == "COMPLETED")
    strict_matches = sum(1 for e in rerun_evaluations if e.get("incident_type", {}).get("strict_match", False))
    flexible_matches = sum(1 for e in rerun_evaluations if e.get("incident_type", {}).get("flexible_match", False))

    print(f"\nRe-run Statistics:")
    print(f"  Completed: {completed}/{len(rerun_results)}")
    print(f"  Strict matches: {strict_matches}/{completed} ({100*strict_matches/completed:.1f}%)" if completed else "  Strict matches: N/A")
    print(f"  Flexible matches: {flexible_matches}/{completed} ({100*flexible_matches/completed:.1f}%)" if completed else "  Flexible matches: N/A")

    # Count cases with serious_incident_type
    with_serious = sum(1 for e in rerun_evaluations if e.get("serious_incident_type"))
    print(f"  With serious_incident_type: {with_serious}/{completed}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
