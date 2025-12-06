#!/usr/bin/env python3
"""
Forensic Agent Benchmark Runner
Analyzes 100 synthetic incidents and collects performance metrics
"""

import json
import time
import requests
import sys
from typing import Dict, List
from datetime import datetime
from pathlib import Path
import statistics


class ForensicBenchmark:
    """Benchmark runner for forensic agent"""

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
            "errors": []
        }

    def check_health(self) -> bool:
        """Check if forensic agent is available"""
        try:
            response = requests.get(f"{self.forensic_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"✗ Forensic agent not available: {e}")
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
                timeout=180  # 3 minutes timeout
            )

            elapsed_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                result["processing_time"] = elapsed_time
                result["incident_id"] = incident["id"]
                return result
            else:
                return {
                    "incident_id": incident["id"],
                    "status": "ERROR",
                    "error": f"HTTP {response.status_code}",
                    "processing_time": elapsed_time
                }

        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                "incident_id": incident["id"],
                "status": "ERROR",
                "error": str(e),
                "processing_time": elapsed_time
            }

    def run_benchmark(self, incidents: List[Dict], max_incidents: int = None):
        """Run benchmark on all incidents"""

        if max_incidents:
            incidents = incidents[:max_incidents]

        self.metrics["total_incidents"] = len(incidents)

        print(f"\n{'='*70}")
        print(f"FORENSIC AGENT BENCHMARK")
        print(f"{'='*70}")
        print(f"Total incidents: {len(incidents)}")
        print(f"Target: {self.forensic_url}")
        print(f"{'='*70}\n")

        for idx, incident in enumerate(incidents, 1):
            print(f"[{idx}/{len(incidents)}] Analyzing {incident['id']}...", end=" ", flush=True)

            result = self.analyze_incident(incident)
            self.results.append(result)

            # Update metrics
            status = result.get("status", "UNKNOWN")
            proc_time = result.get("processing_time", 0)

            if status == "COMPLETED":
                self.metrics["successful"] += 1
                self.metrics["processing_times"].append(proc_time)

                # Extract confidence
                confidence = result.get("extraction", {}).get("confidence", {}).get("overall", 0)
                self.metrics["confidence_scores"].append(confidence)

                # Track risk levels
                risk_level = result.get("eu_ai_act", {}).get("risk_level", "Unknown")
                self.metrics["risk_levels"][risk_level] = self.metrics["risk_levels"].get(risk_level, 0) + 1

                # Track incident types
                incident_type = result.get("extraction", {}).get("incident", {}).get("incident_type", "unknown")
                self.metrics["incident_types"][incident_type] = self.metrics["incident_types"].get(incident_type, 0) + 1

                print(f"✓ {proc_time:.1f}s (confidence: {confidence:.2f})")

            elif status == "LOW_CONFIDENCE":
                self.metrics["low_confidence"] += 1
                self.metrics["processing_times"].append(proc_time)
                confidence = result.get("extraction", {}).get("confidence", {}).get("overall", 0)
                self.metrics["confidence_scores"].append(confidence)
                print(f"⚠ Low confidence ({confidence:.2f})")

            elif status == "ERROR":
                self.metrics["failed"] += 1
                error = result.get("error", "Unknown")
                self.metrics["errors"].append(f"{incident['id']}: {error}")
                print(f"✗ Error: {error}")

            else:
                print(f"✗ Unknown status: {status}")

            # Small delay to avoid overwhelming the service
            time.sleep(0.5)

    def compute_statistics(self) -> Dict:
        """Compute benchmark statistics"""

        stats = {
            "summary": {
                "total_incidents": self.metrics["total_incidents"],
                "successful": self.metrics["successful"],
                "low_confidence": self.metrics["low_confidence"],
                "failed": self.metrics["failed"],
                "success_rate": self.metrics["successful"] / self.metrics["total_incidents"] * 100 if self.metrics["total_incidents"] > 0 else 0
            },
            "performance": {},
            "quality": {},
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

        return stats

    def save_results(self, output_dir: Path):
        """Save benchmark results"""

        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save full results
        results_file = output_dir / f"benchmark_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n✓ Full results saved: {results_file}")

        # Save statistics
        stats = self.compute_statistics()
        stats_file = output_dir / f"benchmark_stats_{timestamp}.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"✓ Statistics saved: {stats_file}")

        return results_file, stats_file, stats

    def print_report(self, stats: Dict):
        """Print benchmark report"""

        print(f"\n{'='*70}")
        print(f"BENCHMARK REPORT")
        print(f"{'='*70}\n")

        # Summary
        summary = stats["summary"]
        print(f"Summary:")
        print(f"  Total incidents: {summary['total_incidents']}")
        print(f"  Successful: {summary['successful']} ({summary['success_rate']:.1f}%)")
        print(f"  Low confidence: {summary['low_confidence']}")
        print(f"  Failed: {summary['failed']}")
        print()

        # Performance
        if stats["performance"]:
            perf = stats["performance"]
            print(f"Performance:")
            print(f"  Mean time: {perf['mean_time']:.2f}s")
            print(f"  Median time: {perf['median_time']:.2f}s")
            print(f"  Min time: {perf['min_time']:.2f}s")
            print(f"  Max time: {perf['max_time']:.2f}s")
            print(f"  Std dev: {perf['stdev_time']:.2f}s")
            print()

        # Quality
        if stats["quality"]:
            qual = stats["quality"]
            print(f"Extraction Quality:")
            print(f"  Mean confidence: {qual['mean_confidence']:.3f}")
            print(f"  Median confidence: {qual['median_confidence']:.3f}")
            print(f"  Min confidence: {qual['min_confidence']:.3f}")
            print(f"  Max confidence: {qual['max_confidence']:.3f}")
            print(f"  Std dev: {qual['stdev_confidence']:.3f}")
            print()

        # Risk distribution
        if stats["risk_distribution"]:
            print(f"Risk Level Distribution:")
            for risk, count in sorted(stats["risk_distribution"].items()):
                pct = count / summary['successful'] * 100 if summary['successful'] > 0 else 0
                print(f"  {risk}: {count} ({pct:.1f}%)")
            print()

        # Incident type distribution
        if stats["incident_distribution"]:
            print(f"Incident Type Distribution (Top 10):")
            sorted_types = sorted(stats["incident_distribution"].items(), key=lambda x: x[1], reverse=True)
            for incident_type, count in sorted_types[:10]:
                pct = count / summary['successful'] * 100 if summary['successful'] > 0 else 0
                print(f"  {incident_type}: {count} ({pct:.1f}%)")
            print()

        # Errors
        if stats["errors"]:
            print(f"Errors ({len(stats['errors'])}):")
            for error in stats["errors"][:5]:
                print(f"  {error}")
            if len(stats["errors"]) > 5:
                print(f"  ... and {len(stats['errors']) - 5} more")
            print()

        print(f"{'='*70}\n")


def main():
    # Load incidents
    incidents_file = Path(__file__).parent / "benchmark_incidents.json"

    if not incidents_file.exists():
        print(f"✗ Incidents file not found: {incidents_file}")
        print("Run generate_incidents.py first")
        sys.exit(1)

    with open(incidents_file) as f:
        incidents = json.load(f)

    print(f"✓ Loaded {len(incidents)} incidents from {incidents_file}")

    # Create benchmark runner
    benchmark = ForensicBenchmark()

    # Check service health
    print("Checking forensic agent health...", end=" ")
    if not benchmark.check_health():
        sys.exit(1)
    print("✓")

    # Run benchmark
    benchmark.run_benchmark(incidents)

    # Save and print results
    output_dir = Path(__file__).parent / "results"
    results_file, stats_file, stats = benchmark.save_results(output_dir)
    benchmark.print_report(stats)

    return results_file, stats_file


if __name__ == "__main__":
    main()
