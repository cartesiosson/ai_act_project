#!/usr/bin/env python3
"""
Run full benchmark for the 8 MinimalRisk→HighRisk cases.
Uses the complete forensic agent pipeline via API.
"""

import json
import time
import requests
import sys
import csv
from pathlib import Path
from datetime import datetime

# The 8 cases that were MinimalRisk→HighRisk
TARGET_CASE_IDS = [
    "AIAAIC2044",  # UK Post Office/Horizon
    "AIAAIC1497",  # Air Canada chatbot
    "AIAAIC1734",  # Deepfake robocall
    "AIAAIC1363",  # South Korea chatbot
    "AIAAIC0632",  # Zillow iBuying
    "AIAAIC1291",  # Clearview AI
    "AIAAIC1073",  # AI hiring tools
    "AIAAIC1495"   # OpenAI API
]

# CSV file path
CSV_FILE = Path(__file__).parent / "data" / "AIAAIC Repository - Incidents.csv"
FORENSIC_URL = "http://localhost:8002"

# Import ground truth mapper
sys.path.insert(0, str(Path(__file__).parent))
from ground_truth_mapper import create_full_ground_truth


def load_target_incidents():
    """Load only the 8 target incidents from CSV."""
    incidents = []

    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)

        # Skip title row (row 1)
        next(reader)

        # Read headers (row 2)
        headers = next(reader)

        # Skip sub-headers row (row 3)
        next(reader)

        # Process data rows
        for row in reader:
            if len(row) < 10:
                continue

            row_dict = dict(zip(headers, row))
            aiaaic_id = row_dict.get('AIAAIC ID#', '').strip()

            if aiaaic_id in TARGET_CASE_IDS:
                headline = row_dict.get('Headline', '').strip()

                # Build narrative
                narrative_parts = [headline]

                system_name = row_dict.get('System name(s)', '').strip()
                if system_name:
                    narrative_parts.append(f"The AI system involved is {system_name}.")

                technology = row_dict.get('Technology(ies)', '').strip()
                if technology:
                    narrative_parts.append(f"Technology type: {technology}.")

                purpose = row_dict.get('Purpose(s)', '').strip()
                if purpose:
                    narrative_parts.append(f"System purpose: {purpose}.")

                deployer = row_dict.get('Deployer(s)', '').strip()
                developer = row_dict.get('Developer(s)', '').strip()
                if deployer:
                    narrative_parts.append(f"Deployed by {deployer}.")
                if developer and developer != deployer:
                    narrative_parts.append(f"Developed by {developer}.")

                sector = row_dict.get('Sector(s)', '').strip()
                if sector:
                    narrative_parts.append(f"Sector: {sector}.")

                country = row_dict.get('Country(ies)', '').strip()
                if country:
                    narrative_parts.append(f"Location: {country}.")

                occurred = row_dict.get('Occurred', '').strip()
                if occurred:
                    narrative_parts.append(f"Year: {occurred}.")

                issues = row_dict.get('Issue(s)', '').strip()
                if issues:
                    narrative_parts.append(f"Issues identified: {issues}.")

                news_trigger = row_dict.get('News trigger(s)', '').strip()
                if news_trigger:
                    narrative_parts.append(f"News trigger: {news_trigger}.")

                narrative = " ".join(narrative_parts)

                # Extract harms
                individual_harms = row[12] if len(row) > 12 else ""
                societal_harms = row[13] if len(row) > 13 else ""

                # Ground truth
                ground_truth_input = {
                    "aiaaic_id": aiaaic_id,
                    "headline": headline,
                    "issues": issues,
                    "sector": sector,
                    "technology": technology,
                    "purpose": purpose,
                    "deployer": deployer,
                    "developer": developer,
                    "individual_harms": individual_harms,
                    "societal_harms": societal_harms
                }
                ground_truth = create_full_ground_truth(ground_truth_input)

                incidents.append({
                    "id": aiaaic_id,
                    "narrative": narrative,
                    "source": "AIAAIC Repository",
                    "metadata": {
                        "aiaaic_id": aiaaic_id,
                        "aiaaic_title": headline,
                        "system_name": system_name,
                        "technology": technology,
                        "purpose": purpose,
                        "deployer": deployer,
                        "developer": developer,
                        "sector": sector,
                        "country": country,
                        "occurred": occurred,
                        "issues": issues,
                        "news_trigger": news_trigger,
                        "individual_harms": individual_harms,
                        "societal_harms": societal_harms
                    },
                    "ground_truth": ground_truth
                })

    return incidents


def analyze_incident(incident):
    """Analyze a single incident via full forensic API."""
    start_time = time.time()

    try:
        response = requests.post(
            f"{FORENSIC_URL}/forensic/analyze",
            json={
                "narrative": incident["narrative"],
                "source": incident["source"],
                "metadata": incident["metadata"]
            },
            timeout=300  # 5 minutes timeout
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            result["processing_time"] = elapsed
            result["incident_id"] = incident["id"]
            result["ground_truth"] = incident["ground_truth"]
            return result
        else:
            return {
                "incident_id": incident["id"],
                "status": "ERROR",
                "error": f"HTTP {response.status_code}: {response.text[:200]}",
                "processing_time": elapsed
            }

    except Exception as e:
        return {
            "incident_id": incident["id"],
            "status": "ERROR",
            "error": str(e),
            "processing_time": time.time() - start_time
        }


def check_service_health():
    """Check if forensic service is running."""
    try:
        response = requests.get(f"{FORENSIC_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    print("=" * 70)
    print("FULL BENCHMARK - 8 MinimalRisk→HighRisk Cases")
    print("=" * 70)
    print(f"Testing updated causes_death_or_injury prompt (Art. 3(49)(a))")
    print()

    # Check service
    print("Checking forensic service...", end=" ")
    if not check_service_health():
        print("ERROR - Service not available!")
        print("Make sure forensic_agent is running on http://localhost:8002")
        sys.exit(1)
    print("OK")

    # Load incidents
    print(f"\nLoading target incidents from CSV...")
    incidents = load_target_incidents()
    print(f"Loaded {len(incidents)} of {len(TARGET_CASE_IDS)} target cases")

    if not incidents:
        print("No incidents found!")
        sys.exit(1)

    # Show loaded cases
    print("\nCases to analyze:")
    for inc in incidents:
        title = inc["metadata"]["aiaaic_title"][:50]
        gt_risk = inc["ground_truth"].get("expected_risk", "?")
        print(f"  - {inc['id']}: {title}... (GT: {gt_risk})")

    print(f"\n{'=' * 70}")
    print("RUNNING FULL BENCHMARK")
    print(f"{'=' * 70}\n")

    results = []

    for idx, incident in enumerate(incidents, 1):
        incident_id = incident["id"]
        title = incident["metadata"]["aiaaic_title"][:40]
        gt_risk = incident["ground_truth"].get("expected_risk", "?")

        print(f"[{idx}/{len(incidents)}] {incident_id}: {title}...")
        print(f"    Ground Truth Risk: {gt_risk}")

        result = analyze_incident(incident)
        results.append(result)

        if result.get("status") == "ERROR":
            print(f"    ERROR: {result.get('error', 'Unknown')[:60]}")
        else:
            proc_time = result.get("processing_time", 0)
            status = result.get("status", "?")

            # Get extraction details
            extraction = result.get("extraction", {})
            incident_data = extraction.get("incident", {})
            causes_death = incident_data.get("causes_death_or_injury", "?")

            # Get EU AI Act classification
            eu_ai_act = result.get("eu_ai_act", {})
            risk_level = eu_ai_act.get("risk_level", "?")

            print(f"    Status: {status} ({proc_time:.1f}s)")
            print(f"    causes_death_or_injury: {causes_death}")
            print(f"    Predicted Risk: {risk_level}")
            print(f"    Match GT? {'✓' if risk_level == gt_risk else '✗ MISMATCH'}")

        print()
        time.sleep(1)  # Small delay between requests

    # Summary
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    correct = 0
    still_high = 0

    for result in results:
        if result.get("status") == "ERROR":
            continue

        incident_id = result.get("incident_id", "?")
        gt_risk = result.get("ground_truth", {}).get("expected_risk", "?")
        pred_risk = result.get("eu_ai_act", {}).get("risk_level", "?")
        causes_death = result.get("extraction", {}).get("incident", {}).get("causes_death_or_injury", "?")

        match = "✓" if pred_risk == gt_risk else "✗"
        print(f"{incident_id}: GT={gt_risk:12} Pred={pred_risk:12} death_injury={str(causes_death):5} {match}")

        if pred_risk == gt_risk:
            correct += 1
        if pred_risk == "HighRisk" and gt_risk != "HighRisk":
            still_high += 1

    print()
    total_valid = len([r for r in results if r.get("status") != "ERROR"])
    print(f"Correct classifications: {correct}/{total_valid}")
    print(f"Still incorrectly HighRisk: {still_high}/{total_valid}")

    # Save results
    output_file = Path(__file__).parent / "results" / f"8_cases_full_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
