#!/usr/bin/env python3
"""
Forensic Agent Real Benchmark Runner - Version 2
Analyzes real AI incidents from the AIAAIC Repository with ground truth evaluation.

Key improvements over v1:
- Ground truth mapping from AIAAIC taxonomy to EU AI Act
- Strict and flexible accuracy metrics for incident type classification
- Risk level validation against expected values
- Multi-label handling for AIAAIC Issue(s) field

Version 2.1 improvements:
- Incremental saving: results saved after each incident
- Resume capability: can continue from where it left off
- Checkpoint file tracks progress

Version 2.2 improvements:
- Batch processing with automatic Ollama restart every N cases
- Prevents memory/timeout issues on long runs

Data source: AIAAIC Repository (https://www.aiaaic.org/aiaaic-repository)
License: CC BY-SA 4.0
"""

import json
import time
import requests
import sys
import csv
import random
import hashlib
import subprocess
from typing import Dict, List, Optional, Set
from datetime import datetime
from pathlib import Path
import statistics

# Batch configuration
BATCH_SIZE = 15  # Restart Ollama every N cases
OLLAMA_RESTART_WAIT = 20  # Seconds to wait after restart
MAX_HEALTH_RETRIES = 30  # Max retries waiting for service health


def restart_ollama() -> bool:
    """
    Restart Ollama container using docker restart.
    Uses the full container name for more reliable restart.
    Returns True if restart was successful.
    """
    try:
        print("\n" + "="*50)
        print("🔄 Restarting Ollama (batch maintenance)...")
        print("="*50)

        # Use docker restart with full container name (more reliable than docker-compose)
        result = subprocess.run(
            ["docker", "restart", "ai_act_project-ollama-1"],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            print(f"✓ Ollama container restarted")
            return True
        else:
            print(f"✗ Failed to restart Ollama: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("✗ Ollama restart timed out")
        return False
    except Exception as e:
        print(f"✗ Error restarting Ollama: {e}")
        return False


def wait_for_service_health(forensic_url: str, max_retries: int = MAX_HEALTH_RETRIES) -> bool:
    """
    Wait for forensic service to be healthy after Ollama restart.
    Returns True if service is healthy.
    """
    print(f"⏳ Waiting for service to be ready...", end="", flush=True)

    for i in range(max_retries):
        try:
            response = requests.get(f"{forensic_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Check if all services are operational
                if data.get("status") == "healthy":
                    print(f" ready! ({i+1}s)")
                    return True
        except:
            pass

        print(".", end="", flush=True)
        time.sleep(1)

    print(" timeout!")
    return False


# Import ground truth mapper
from ground_truth_mapper import (
    map_issues_to_ground_truth,
    map_sector_to_context,
    map_technology_to_system_type,
    map_harms_to_risk_indicators,
    create_full_ground_truth,
    evaluate_incident_type,
    evaluate_risk_level
)

# Local CSV file path
AIAAIC_CSV_FILE = Path(__file__).parent / "data" / "AIAAIC Repository - Incidents.csv"

# AIAAIC Attribution (CC BY-SA 4.0)
AIAAIC_ATTRIBUTION = {
    "source": "AIAAIC Repository",
    "url": "https://www.aiaaic.org/aiaaic-repository",
    "license": "CC BY-SA 4.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
    "version": "December 2025",
    "terms": "https://www.aiaaic.org/terms",
    "citation": "Data provided by AIAAIC (https://www.aiaaic.org/aiaaic-repository) under CC BY-SA 4.0 license."
}


class AIAAICDataLoaderV2:
    """Loads real incident data from AIAAIC Repository CSV with ground truth"""

    def __init__(self, csv_path: Path = AIAAIC_CSV_FILE):
        self.csv_path = csv_path

    def load_incidents(self) -> List[Dict]:
        """
        Load incidents from local AIAAIC CSV file with ground truth mapping.

        CSV Structure (AIAAIC Repository export):
        - Row 1: Title row (skip)
        - Row 2: Headers
        - Row 3: Sub-headers for harms (skip)
        - Row 4+: Data
        """
        if not self.csv_path.exists():
            raise FileNotFoundError(
                f"AIAAIC CSV not found: {self.csv_path}\n"
                f"Download from: https://docs.google.com/spreadsheets/d/1Bn55B4xz21-_Rgdr8BBb2lt0n_4rzLGxFADMlVW0PYI/"
            )

        print(f"Loading AIAAIC incidents from: {self.csv_path}")

        incidents = []
        with open(self.csv_path, 'r', encoding='utf-8') as f:
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
                incident = self._parse_row_with_ground_truth(row_dict, row)
                if incident:
                    incidents.append(incident)

        print(f"Loaded {len(incidents)} real incidents from AIAAIC")
        return incidents

    def _parse_row_with_ground_truth(self, row_dict: Dict, raw_row: List) -> Optional[Dict]:
        """
        Parse a CSV row into incident format with ground truth.
        """
        headline = row_dict.get('Headline', '').strip()
        if not headline:
            return None

        aiaaic_id = row_dict.get('AIAAIC ID#', '').strip()
        if not aiaaic_id:
            return None

        # Build comprehensive narrative
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

        if len(narrative) < 50:
            return None

        # Extract harms from raw row (columns 12-14 for external harms)
        individual_harms = raw_row[12] if len(raw_row) > 12 else ""
        societal_harms = raw_row[13] if len(raw_row) > 13 else ""

        # Create ground truth structure
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

        summary_links = row_dict.get('Summary/links', '').strip()

        return {
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
                "societal_harms": societal_harms,
                "original_url": summary_links
            },
            "ground_truth": ground_truth
        }


class RealBenchmarkV2:
    """Benchmark runner for real AIAAIC incidents with ground truth evaluation"""

    def __init__(self, forensic_url: str = "http://localhost:8002", output_dir: Path = None):
        self.forensic_url = forensic_url
        self.output_dir = output_dir or Path(__file__).parent / "results"
        self.output_dir.mkdir(exist_ok=True)

        # Session ID for this run
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Checkpoint and results files
        self.checkpoint_file = self.output_dir / f"checkpoint_{self.session_id}.json"
        self.results_file = self.output_dir / f"real_benchmark_results_v2_{self.session_id}.json"
        self.evaluations_file = self.output_dir / f"real_benchmark_evaluations_v2_{self.session_id}.json"

        self.results = []
        self.processed_ids: Set[str] = set()
        self.metrics = {
            "total_incidents": 0,
            "successful": 0,
            "failed": 0,
            "low_confidence": 0,
            "processing_times": [],
            "confidence_scores": [],
            "risk_levels": {},
            "incident_types": {},
            "errors": [],
            # Ground truth evaluation metrics
            "incident_type_strict_matches": 0,
            "incident_type_flexible_matches": 0,
            "risk_level_matches": 0,
            "evaluation_details": []
        }

    def check_health(self) -> bool:
        """Check if forensic agent is available"""
        try:
            response = requests.get(f"{self.forensic_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Forensic agent not available: {e}")
            return False

    def _save_checkpoint(self, selected_ids: List[str] = None):
        """Save current progress to checkpoint file"""
        checkpoint = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "processed_ids": list(self.processed_ids),
            "metrics": {
                k: v if not isinstance(v, list) else len(v)
                for k, v in self.metrics.items()
            }
        }
        # Save selected IDs for reproducibility on resume
        if selected_ids:
            checkpoint["selected_ids"] = selected_ids
        elif hasattr(self, '_current_selected_ids'):
            checkpoint["selected_ids"] = self._current_selected_ids

        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

    def _save_result_incremental(self, result: Dict, evaluation: Dict = None):
        """Append a single result to the results file"""
        # Append to results list
        self.results.append(result)

        # Write all results to file (overwrite for consistency)
        with open(self.results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        # Save evaluation if present
        if evaluation:
            with open(self.evaluations_file, 'w') as f:
                json.dump(self.metrics["evaluation_details"], f, indent=2)

    def load_checkpoint(self, checkpoint_path: Path) -> bool:
        """
        Load a previous checkpoint to resume from.
        Returns True if checkpoint was loaded successfully.
        """
        if not checkpoint_path.exists():
            return False

        try:
            with open(checkpoint_path, 'r') as f:
                checkpoint = json.load(f)

            # Extract session ID from checkpoint
            old_session_id = checkpoint.get("session_id", "")
            self.processed_ids = set(checkpoint.get("processed_ids", []))

            # Load selected_ids to maintain same sample
            self.resume_selected_ids = checkpoint.get("selected_ids", None)

            # Load existing results if available
            old_results_file = self.output_dir / f"real_benchmark_results_v2_{old_session_id}.json"
            if old_results_file.exists():
                with open(old_results_file, 'r') as f:
                    self.results = json.load(f)

            # Load existing evaluations
            old_evals_file = self.output_dir / f"real_benchmark_evaluations_v2_{old_session_id}.json"
            if old_evals_file.exists():
                with open(old_evals_file, 'r') as f:
                    self.metrics["evaluation_details"] = json.load(f)

            # Recalculate metrics from loaded results
            self._recalculate_metrics_from_results()

            # Use the old session ID to continue appending to same files
            self.session_id = old_session_id
            self.checkpoint_file = self.output_dir / f"checkpoint_{self.session_id}.json"
            self.results_file = self.output_dir / f"real_benchmark_results_v2_{self.session_id}.json"
            self.evaluations_file = self.output_dir / f"real_benchmark_evaluations_v2_{self.session_id}.json"

            print(f"Resumed from checkpoint: {len(self.processed_ids)} incidents already processed")
            return True

        except Exception as e:
            print(f"Failed to load checkpoint: {e}")
            return False

    def _recalculate_metrics_from_results(self):
        """Recalculate metrics from loaded results"""
        for result in self.results:
            status = result.get("status", "UNKNOWN")
            proc_time = result.get("processing_time", 0)

            if status == "COMPLETED":
                self.metrics["successful"] += 1
                self.metrics["processing_times"].append(proc_time)

                confidence = result.get("extraction", {}).get("confidence", {}).get("overall", 0)
                self.metrics["confidence_scores"].append(confidence)

                risk_level = result.get("eu_ai_act", {}).get("risk_level", "Unknown")
                self.metrics["risk_levels"][risk_level] = self.metrics["risk_levels"].get(risk_level, 0) + 1

                incident_type = result.get("extraction", {}).get("incident", {}).get("incident_type", "unknown")
                self.metrics["incident_types"][incident_type] = self.metrics["incident_types"].get(incident_type, 0) + 1

            elif status == "LOW_CONFIDENCE":
                self.metrics["low_confidence"] += 1
                self.metrics["processing_times"].append(proc_time)
                confidence = result.get("extraction", {}).get("confidence", {}).get("overall", 0)
                self.metrics["confidence_scores"].append(confidence)

            elif status == "ERROR":
                self.metrics["failed"] += 1
                error = result.get("error", "Unknown")
                self.metrics["errors"].append(f"{result.get('incident_id', '?')}: {error}")

        # Recalculate evaluation metrics
        for eval_detail in self.metrics["evaluation_details"]:
            if eval_detail.get("incident_type", {}).get("strict_match"):
                self.metrics["incident_type_strict_matches"] += 1
            if eval_detail.get("incident_type", {}).get("flexible_match"):
                self.metrics["incident_type_flexible_matches"] += 1
            if eval_detail.get("risk_level", {}).get("match"):
                self.metrics["risk_level_matches"] += 1

    def analyze_incident(self, incident: Dict) -> Dict:
        """Analyze a single incident"""
        start_time = time.time()

        try:
            response = requests.post(
                f"{self.forensic_url}/forensic/analyze",
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

    def _evaluate_result(self, result: Dict) -> Dict:
        """Evaluate a single result against ground truth"""
        ground_truth = result.get("ground_truth", {})

        # Get predicted values
        predicted_incident_type = result.get("extraction", {}).get("incident", {}).get("incident_type", "unknown")
        predicted_risk_level = result.get("eu_ai_act", {}).get("risk_level", "Unknown")

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
            "risk_level": risk_level_eval
        }

    def run_benchmark(self, incidents: List[Dict], num_cases: int = None, randomize: bool = True,
                      batch_size: int = BATCH_SIZE):
        """
        Run benchmark on selected incidents with ground truth evaluation.

        Args:
            incidents: All available incidents
            num_cases: Number of cases to analyze (None = all)
            randomize: If True, randomly select incidents
            batch_size: Number of cases between Ollama restarts
        """

        # Check if resuming with saved IDs
        if hasattr(self, 'resume_selected_ids') and self.resume_selected_ids:
            id_set = set(self.resume_selected_ids)
            selected_incidents = [i for i in incidents if i['id'] in id_set]
            # Maintain original order
            id_order = {id: idx for idx, id in enumerate(self.resume_selected_ids)}
            selected_incidents.sort(key=lambda x: id_order.get(x['id'], 999999))
            self._current_selected_ids = self.resume_selected_ids
        elif num_cases and num_cases < len(incidents):
            if randomize:
                random.seed(42)  # Fixed seed for reproducibility
                selected_incidents = random.sample(incidents, num_cases)
            else:
                selected_incidents = incidents[:num_cases]
            # Store selected IDs for checkpoint
            self._current_selected_ids = [i['id'] for i in selected_incidents]
        else:
            selected_incidents = incidents
            num_cases = len(incidents)
            self._current_selected_ids = [i['id'] for i in selected_incidents]

        self.metrics["total_incidents"] = len(selected_incidents)

        # Count how many are already processed
        already_processed = sum(1 for i in selected_incidents if i['id'] in self.processed_ids)
        remaining = len(selected_incidents) - already_processed

        # Calculate batches
        num_batches = (remaining + batch_size - 1) // batch_size if remaining > 0 else 0

        print(f"\n{'='*70}")
        print(f"FORENSIC AGENT REAL BENCHMARK V2.2 (Batch Processing)")
        print(f"{'='*70}")
        print(f"Session ID: {self.session_id}")
        print(f"Total incidents: {len(selected_incidents)}")
        print(f"Already processed: {already_processed}")
        print(f"Remaining: {remaining}")
        print(f"Batch size: {batch_size} (Ollama restart every {batch_size} cases)")
        print(f"Estimated batches: {num_batches}")
        print(f"Results file: {self.results_file.name}")
        print(f"Data source: AIAAIC Repository")
        print(f"Target: {self.forensic_url}")
        print(f"{'='*70}\n")

        if remaining == 0:
            print("All incidents already processed!")
            return

        processed_count = already_processed
        batch_counter = 0  # Counter within current batch

        for idx, incident in enumerate(selected_incidents, 1):
            incident_id = incident['id']

            # Skip already processed
            if incident_id in self.processed_ids:
                continue

            # Check if we need to restart Ollama (every batch_size cases)
            if batch_counter > 0 and batch_counter % batch_size == 0:
                current_batch = (processed_count // batch_size) + 1
                print(f"\n[Batch {current_batch} complete - {batch_counter} cases in this session]")

                if restart_ollama():
                    time.sleep(OLLAMA_RESTART_WAIT)
                    if not wait_for_service_health(self.forensic_url):
                        print("⚠ Service not responding after restart, continuing anyway...")
                else:
                    print("⚠ Ollama restart failed, continuing anyway...")

                print()  # Empty line before continuing

            processed_count += 1
            batch_counter += 1

            title = incident['metadata'].get('aiaaic_title', incident_id)[:45]
            print(f"[{processed_count}/{len(selected_incidents)}] {title}...", end=" ", flush=True)

            result = self.analyze_incident(incident)
            evaluation = None

            status = result.get("status", "UNKNOWN")
            proc_time = result.get("processing_time", 0)

            if status == "COMPLETED":
                self.metrics["successful"] += 1
                self.metrics["processing_times"].append(proc_time)

                confidence = result.get("extraction", {}).get("confidence", {}).get("overall", 0)
                self.metrics["confidence_scores"].append(confidence)

                risk_level = result.get("eu_ai_act", {}).get("risk_level", "Unknown")
                self.metrics["risk_levels"][risk_level] = self.metrics["risk_levels"].get(risk_level, 0) + 1

                incident_type = result.get("extraction", {}).get("incident", {}).get("incident_type", "unknown")
                self.metrics["incident_types"][incident_type] = self.metrics["incident_types"].get(incident_type, 0) + 1

                # Evaluate against ground truth
                evaluation = self._evaluate_result(result)
                self.metrics["evaluation_details"].append(evaluation)

                if evaluation["incident_type"]["strict_match"]:
                    self.metrics["incident_type_strict_matches"] += 1
                if evaluation["incident_type"]["flexible_match"]:
                    self.metrics["incident_type_flexible_matches"] += 1
                if evaluation["risk_level"]["match"]:
                    self.metrics["risk_level_matches"] += 1

                # Display result with ground truth comparison
                gt_primary = evaluation["incident_type"]["expected_primary"] or "?"
                match_symbol = "=" if evaluation["incident_type"]["flexible_match"] else "!"
                print(f"OK {proc_time:.1f}s | {incident_type} {match_symbol} {gt_primary} | {risk_level}")

            elif status == "LOW_CONFIDENCE":
                self.metrics["low_confidence"] += 1
                self.metrics["processing_times"].append(proc_time)
                confidence = result.get("extraction", {}).get("confidence", {}).get("overall", 0)
                self.metrics["confidence_scores"].append(confidence)
                print(f"LOW_CONF ({confidence:.2f})")

            elif status == "ERROR":
                self.metrics["failed"] += 1
                error = result.get("error", "Unknown")[:50]
                self.metrics["errors"].append(f"{incident_id}: {error}")
                print(f"ERROR: {error}")

            else:
                self.metrics["failed"] += 1
                print(f"Unknown status: {status}")

            # Mark as processed and save incrementally
            self.processed_ids.add(incident_id)
            self._save_result_incremental(result, evaluation)
            self._save_checkpoint()

            time.sleep(0.5)

        print(f"\n✓ Benchmark complete. Results saved to: {self.results_file}")

    def compute_statistics(self) -> Dict:
        """Compute benchmark statistics including ground truth accuracy"""

        successful = self.metrics["successful"]

        stats = {
            "benchmark_type": "REAL",
            "benchmark_version": "v2",
            "data_source": AIAAIC_ATTRIBUTION,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_incidents": self.metrics["total_incidents"],
                "successful": successful,
                "low_confidence": self.metrics["low_confidence"],
                "failed": self.metrics["failed"],
                "success_rate": successful / self.metrics["total_incidents"] * 100 if self.metrics["total_incidents"] > 0 else 0
            },
            "performance": {},
            "quality": {},
            "ground_truth_accuracy": {},
            "risk_distribution": self.metrics["risk_levels"],
            "incident_distribution": self.metrics["incident_types"],
            "errors": self.metrics["errors"]
        }

        # Performance statistics
        if self.metrics["processing_times"]:
            stats["performance"] = {
                "mean_time": statistics.mean(self.metrics["processing_times"]),
                "median_time": statistics.median(self.metrics["processing_times"]),
                "min_time": min(self.metrics["processing_times"]),
                "max_time": max(self.metrics["processing_times"]),
                "stdev_time": statistics.stdev(self.metrics["processing_times"]) if len(self.metrics["processing_times"]) > 1 else 0
            }

        # Quality statistics
        if self.metrics["confidence_scores"]:
            stats["quality"] = {
                "mean_confidence": statistics.mean(self.metrics["confidence_scores"]),
                "median_confidence": statistics.median(self.metrics["confidence_scores"]),
                "min_confidence": min(self.metrics["confidence_scores"]),
                "max_confidence": max(self.metrics["confidence_scores"]),
                "stdev_confidence": statistics.stdev(self.metrics["confidence_scores"]) if len(self.metrics["confidence_scores"]) > 1 else 0
            }

        # Ground truth accuracy
        if successful > 0:
            stats["ground_truth_accuracy"] = {
                "incident_type_strict_accuracy": self.metrics["incident_type_strict_matches"] / successful * 100,
                "incident_type_flexible_accuracy": self.metrics["incident_type_flexible_matches"] / successful * 100,
                "risk_level_accuracy": self.metrics["risk_level_matches"] / successful * 100,
                "incident_type_strict_matches": self.metrics["incident_type_strict_matches"],
                "incident_type_flexible_matches": self.metrics["incident_type_flexible_matches"],
                "risk_level_matches": self.metrics["risk_level_matches"],
                "total_evaluated": successful
            }

        return stats

    def save_results(self):
        """Save final benchmark results and statistics"""

        # Results are already saved incrementally, just save final stats
        stats = self.compute_statistics()
        stats_file = self.output_dir / f"real_benchmark_stats_v2_{self.session_id}.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"\nFinal results: {self.results_file}")
        print(f"Statistics: {stats_file}")
        print(f"Evaluations: {self.evaluations_file}")

        # Clean up checkpoint file on successful completion
        if self.checkpoint_file.exists():
            # Keep checkpoint for reference but mark as complete
            with open(self.checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
            checkpoint["status"] = "COMPLETED"
            checkpoint["completed_at"] = datetime.now().isoformat()
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint, f, indent=2)

        return self.results_file, stats_file, stats

    def print_report(self, stats: Dict):
        """Print benchmark report with ground truth accuracy"""

        print(f"\n{'='*70}")
        print(f"REAL BENCHMARK REPORT V2 (AIAAIC + Ground Truth)")
        print(f"{'='*70}\n")

        # Summary
        summary = stats["summary"]
        print(f"Summary:")
        print(f"  Total real incidents: {summary['total_incidents']}")
        print(f"  Successful: {summary['successful']} ({summary['success_rate']:.1f}%)")
        print(f"  Low confidence: {summary['low_confidence']}")
        print(f"  Failed: {summary['failed']}")
        print()

        # Ground Truth Accuracy (NEW)
        if stats.get("ground_truth_accuracy"):
            gt = stats["ground_truth_accuracy"]
            print(f"Ground Truth Accuracy:")
            print(f"  Incident Type (Strict):   {gt['incident_type_strict_accuracy']:.1f}% ({gt['incident_type_strict_matches']}/{gt['total_evaluated']})")
            print(f"  Incident Type (Flexible): {gt['incident_type_flexible_accuracy']:.1f}% ({gt['incident_type_flexible_matches']}/{gt['total_evaluated']})")
            print(f"  Risk Level:               {gt['risk_level_accuracy']:.1f}% ({gt['risk_level_matches']}/{gt['total_evaluated']})")
            print()
            print(f"  Note: Strict = matches primary type only")
            print(f"        Flexible = matches any of the ground truth types")
            print()

        # Performance
        if stats.get("performance"):
            perf = stats["performance"]
            print(f"Performance:")
            print(f"  Mean time: {perf['mean_time']:.2f}s")
            print(f"  Median time: {perf['median_time']:.2f}s")
            print(f"  Min time: {perf['min_time']:.2f}s")
            print(f"  Max time: {perf['max_time']:.2f}s")
            print()

        # Quality
        if stats.get("quality"):
            qual = stats["quality"]
            print(f"Extraction Quality:")
            print(f"  Mean confidence: {qual['mean_confidence']:.3f}")
            print(f"  Median confidence: {qual['median_confidence']:.3f}")
            print(f"  Min confidence: {qual['min_confidence']:.3f}")
            print(f"  Max confidence: {qual['max_confidence']:.3f}")
            print()

        # Risk distribution
        if stats.get("risk_distribution"):
            print(f"EU AI Act Risk Level Distribution:")
            for risk, count in sorted(stats["risk_distribution"].items()):
                pct = count / summary['successful'] * 100 if summary['successful'] > 0 else 0
                print(f"  {risk}: {count} ({pct:.1f}%)")
            print()

        # Incident type distribution
        if stats.get("incident_distribution"):
            print(f"Incident Type Distribution (Top 10):")
            sorted_types = sorted(stats["incident_distribution"].items(), key=lambda x: x[1], reverse=True)
            for incident_type, count in sorted_types[:10]:
                pct = count / summary['successful'] * 100 if summary['successful'] > 0 else 0
                print(f"  {incident_type}: {count} ({pct:.1f}%)")
            print()

        # Errors
        if stats.get("errors"):
            print(f"Errors ({len(stats['errors'])}):")
            for error in stats["errors"][:5]:
                print(f"  {error}")
            if len(stats["errors"]) > 5:
                print(f"  ... and {len(stats['errors']) - 5} more")
            print()

        # Attribution
        print(f"Data Attribution:")
        print(f"  {AIAAIC_ATTRIBUTION['citation']}")
        print(f"  License: {AIAAIC_ATTRIBUTION['license']}")
        print()

        print(f"{'='*70}\n")


def find_latest_checkpoint(output_dir: Path) -> Optional[Path]:
    """Find the most recent incomplete checkpoint file"""
    checkpoints = list(output_dir.glob("checkpoint_*.json"))
    if not checkpoints:
        return None

    # Sort by modification time, newest first
    checkpoints.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    for cp in checkpoints:
        try:
            with open(cp, 'r') as f:
                data = json.load(f)
            # Skip completed checkpoints
            if data.get("status") == "COMPLETED":
                continue
            return cp
        except:
            continue

    return None


def main():
    """Main entry point"""

    print("="*70)
    print("AIAAIC Real Incident Benchmark V2.2 (Batch Processing)")
    print("="*70)
    print(f"Batch size: {BATCH_SIZE} cases (Ollama restart between batches)")
    print()

    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)

    # Load AIAAIC data with ground truth
    loader = AIAAICDataLoaderV2()
    try:
        all_incidents = loader.load_incidents()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to load AIAAIC data: {e}")
        sys.exit(1)

    if not all_incidents:
        print("No incidents found in AIAAIC data")
        sys.exit(1)

    print(f"\nTotal available incidents: {len(all_incidents)}")

    # Check for resume option
    resume_checkpoint = None
    selected_ids = None

    if len(sys.argv) > 1 and sys.argv[1].lower() == 'resume':
        # Find latest checkpoint
        resume_checkpoint = find_latest_checkpoint(output_dir)
        if resume_checkpoint:
            print(f"\nFound checkpoint: {resume_checkpoint.name}")
            with open(resume_checkpoint, 'r') as f:
                cp_data = json.load(f)
            print(f"  Processed: {len(cp_data.get('processed_ids', []))} incidents")
        else:
            print("\nNo checkpoint found to resume from. Starting fresh.")
    print()

    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip().lower()
        if arg == 'resume':
            # Resume mode - use checkpoint's num_cases or ask
            if resume_checkpoint:
                with open(resume_checkpoint, 'r') as f:
                    cp_data = json.load(f)
                # Get original target from checkpoint metrics
                num_cases = cp_data.get("metrics", {}).get("total_incidents", 385)
            else:
                num_cases = 385  # Default
        elif arg == 'all':
            num_cases = len(all_incidents)
        else:
            try:
                num_cases = int(arg)
                if not (1 <= num_cases <= len(all_incidents)):
                    print(f"Error: Number must be between 1 and {len(all_incidents)}")
                    sys.exit(1)
            except ValueError:
                print(f"Usage: {sys.argv[0]} [NUM_CASES|all|resume]")
                print(f"  NUM_CASES: Number of incidents to analyze (1-{len(all_incidents)})")
                print(f"  all: Analyze all {len(all_incidents)} incidents")
                print(f"  resume: Resume from last checkpoint")
                sys.exit(1)
    else:
        while True:
            try:
                user_input = input(f"Number of cases (1-{len(all_incidents)}, 'all', or 'resume'): ").strip()

                if user_input.lower() == 'resume':
                    resume_checkpoint = find_latest_checkpoint(output_dir)
                    if resume_checkpoint:
                        with open(resume_checkpoint, 'r') as f:
                            cp_data = json.load(f)
                        num_cases = cp_data.get("metrics", {}).get("total_incidents", 385)
                    else:
                        print("No checkpoint found. Enter a number instead.")
                        continue
                    break
                elif user_input.lower() == 'all':
                    num_cases = len(all_incidents)
                    break
                else:
                    num_cases = int(user_input)
                    if 1 <= num_cases <= len(all_incidents):
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(all_incidents)}")
            except ValueError:
                print("Invalid input. Enter a number, 'all', or 'resume'")
            except KeyboardInterrupt:
                print("\nCancelled")
                sys.exit(0)

    print(f"\nTarget: {num_cases} incidents")

    # Create benchmark runner
    benchmark = RealBenchmarkV2(output_dir=output_dir)

    # Load checkpoint if resuming
    if resume_checkpoint:
        benchmark.load_checkpoint(resume_checkpoint)

    # Check service health
    print("\nChecking forensic agent health...", end=" ")
    if not benchmark.check_health():
        print("Forensic agent not available!")
        sys.exit(1)
    print("OK")

    # Run benchmark
    try:
        benchmark.run_benchmark(all_incidents, num_cases=num_cases, randomize=True)
    except KeyboardInterrupt:
        print(f"\n\nInterrupted! Progress saved to: {benchmark.results_file}")
        print(f"Resume with: python3 {sys.argv[0]} resume")
        sys.exit(0)

    # Save and print results
    results_file, stats_file, stats = benchmark.save_results()
    benchmark.print_report(stats)

    return results_file, stats_file


if __name__ == "__main__":
    main()
