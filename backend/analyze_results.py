#!/usr/bin/env python3
"""Comprehensive analysis tool for evaluation results."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from evaluation.statistical_analysis import (
    perform_statistical_analysis,
    generate_statistical_report,
)
from evaluation.comparative_analysis import (
    load_all_results,
    generate_comparison_table,
    generate_category_comparison,
    generate_attack_ranking,
    generate_defense_effectiveness_report,
    save_comparison_data,
)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze evaluation results with statistical analysis",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "results_dir",
        help="Path to results directory (e.g., results/api_matrix_runs)",
    )
    parser.add_argument(
        "--output",
        default="results/comprehensive_analysis",
        help="Output directory for analysis reports",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "both"],
        default="both",
        help="Output format",
    )

    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}")
        sys.exit(1)

    print(f"\n🔍 Analyzing results from: {results_dir}")
    print("=" * 80)

    # Load all results
    print("\n📊 Loading evaluation results...")
    entries = load_all_results(results_dir)

    if not entries:
        print("❌ No evaluation results found in directory.")
        sys.exit(1)

    print(f"✓ Loaded {len(entries)} evaluation entries")
    print(f"  - {len(set(e.model for e in entries))} unique models")
    print(f"  - {len(set(e.defense for e in entries))} unique defenses")
    print(f"  - {len(set(e.attack for e in entries))} unique attacks")

    # Generate comprehensive reports
    print("\n📈 Generating comparative analysis...")
    comparison_table = generate_comparison_table(entries)
    category_comparison = generate_category_comparison(entries)
    attack_ranking = generate_attack_ranking(entries)
    defense_effectiveness = generate_defense_effectiveness_report(entries)

    # Combine all reports
    full_report = "\n\n".join([
        comparison_table,
        category_comparison,
        attack_ranking,
        defense_effectiveness,
    ])

    # Save text report
    if args.format in ["text", "both"]:
        report_path = output_dir / "comprehensive_analysis.txt"
        report_path.write_text(full_report, encoding="utf-8")
        print(f"✓ Text report saved: {report_path}")

    # Save JSON data
    if args.format in ["json", "both"]:
        json_path = output_dir / "comparison_data.json"
        save_comparison_data(entries, json_path)

    # Print summary to console
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(full_report)

    print(f"\n✅ Analysis complete! Reports saved to: {output_dir}")


if __name__ == "__main__":
    main()
