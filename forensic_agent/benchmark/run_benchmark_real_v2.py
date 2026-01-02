#!/usr/bin/env python3
"""
Forensic Agent Real Benchmark Runner - Version 2
Analyzes real AI incidents from the AIAAIC Repository with ground truth evaluation.

Key improvements over v1:
- Ground truth mapping from AIAAIC taxonomy to EU AI Act
- Strict and flexible accuracy metrics for incident type classification
- Risk level validation against expected values
- Multi-label handling for AIAAIC Issue(s) field

Data source: AIAAIC Repository (https://www.aiaaic.org/aiaaic-repository)
License: CC BY-SA 4.0
"""

import json
import time
import requests
import sys
import csv
import random
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import statistics

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

    def __init__(self, forensic_url: str = "http://localhost:8002"):
        self.forensic_url = forensic_url
        self.results = []
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

    def run_benchmark(self, incidents: List[Dict], num_cases: int = None, randomize: bool = True):
        """Run benchmark on selected incidents with ground truth evaluation"""

        if num_cases and num_cases < len(incidents):
            if randomize:
                selected_incidents = random.sample(incidents, num_cases)
            else:
                selected_incidents = incidents[:num_cases]
        else:
            selected_incidents = incidents
            num_cases = len(incidents)

        self.metrics["total_incidents"] = len(selected_incidents)

        print(f"\n{'='*70}")
        print(f"FORENSIC AGENT REAL BENCHMARK V2 (AIAAIC + Ground Truth)")
        print(f"{'='*70}")
        print(f"Selected incidents: {len(selected_incidents)} out of {len(incidents)} available")
        print(f"Data source: AIAAIC Repository")
        print(f"Ground truth: AIAAIC -> EU AI Act mapping enabled")
        print(f"Target: {self.forensic_url}")
        print(f"{'='*70}\n")

        for idx, incident in enumerate(selected_incidents, 1):
            incident_id = incident['id']
            title = incident['metadata'].get('aiaaic_title', incident_id)[:45]
            print(f"[{idx}/{len(selected_incidents)}] {title}...", end=" ", flush=True)

            result = self.analyze_incident(incident)
            self.results.append(result)

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

            time.sleep(0.5)

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

    def save_results(self, output_dir: Path):
        """Save benchmark results"""

        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save full results
        results_file = output_dir / f"real_benchmark_results_v2_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\nFull results saved: {results_file}")

        # Save statistics
        stats = self.compute_statistics()
        stats_file = output_dir / f"real_benchmark_stats_v2_{timestamp}.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"Statistics saved: {stats_file}")

        # Save evaluation details separately
        eval_file = output_dir / f"real_benchmark_evaluations_v2_{timestamp}.json"
        with open(eval_file, 'w') as f:
            json.dump(self.metrics["evaluation_details"], f, indent=2)

        print(f"Evaluations saved: {eval_file}")

        return results_file, stats_file, stats

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


def main():
    """Main entry point"""

    print("="*70)
    print("AIAAIC Real Incident Benchmark V2 (with Ground Truth)")
    print("="*70)
    print()

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
    print()

    # Check for command line argument
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip()
        if arg.lower() == 'all':
            num_cases = len(all_incidents)
        else:
            try:
                num_cases = int(arg)
                if not (1 <= num_cases <= len(all_incidents)):
                    print(f"Error: Number must be between 1 and {len(all_incidents)}")
                    sys.exit(1)
            except ValueError:
                print(f"Error: Invalid argument '{arg}'. Use a number or 'all'")
                sys.exit(1)
    else:
        while True:
            try:
                user_input = input(f"Number of cases to analyze (1-{len(all_incidents)}, or 'all'): ").strip()

                if user_input.lower() == 'all':
                    num_cases = len(all_incidents)
                    break
                else:
                    num_cases = int(user_input)
                    if 1 <= num_cases <= len(all_incidents):
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(all_incidents)}")
            except ValueError:
                print("Invalid input. Enter a number or 'all'")
            except KeyboardInterrupt:
                print("\nCancelled")
                sys.exit(0)

    print(f"\nSelected {num_cases} incidents for analysis")

    # Create benchmark runner
    benchmark = RealBenchmarkV2()

    # Check service health
    print("\nChecking forensic agent health...", end=" ")
    if not benchmark.check_health():
        print("Forensic agent not available!")
        sys.exit(1)
    print("OK")

    # Run benchmark
    benchmark.run_benchmark(all_incidents, num_cases=num_cases, randomize=True)

    # Save and print results
    output_dir = Path(__file__).parent / "results"
    results_file, stats_file, stats = benchmark.save_results(output_dir)
    benchmark.print_report(stats)

    return results_file, stats_file


if __name__ == "__main__":
    main()
