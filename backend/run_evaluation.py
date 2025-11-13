#!/usr/bin/env python3
"""Run automated attack evaluations using Ollama."""

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from evaluation.evaluator import AttackEvaluator, generate_report, save_results


def main():
    parser = argparse.ArgumentParser(description="Evaluate prompt injection attacks")
    parser.add_argument("pdf_file", help="Path to CV PDF file")
    parser.add_argument(
        "--model",
        default="llama3.2:3b",
        help="Ollama model to use (default: llama3.2:3b)",
    )
    parser.add_argument(
        "--attacks",
        nargs="+",
        help="Specific attacks to test (default: all)",
    )
    parser.add_argument(
        "--output",
        default="results/evaluation_results.json",
        help="Output path for results JSON",
    )

    args = parser.parse_args()

    # Load PDF
    pdf_path = Path(args.pdf_file)
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)

    pdf_bytes = pdf_path.read_bytes()

    # Run evaluation
    print(f"\n🚀 Starting evaluation with {args.model}...\n")
    evaluator = AttackEvaluator(model_name=args.model)
    results = evaluator.batch_evaluate(pdf_bytes, pdf_path.name, args.attacks)

    # Generate report
    report = generate_report(results)
    print("\n" + report)

    # Save results
    output_path = Path(args.output)
    save_results(results, output_path)

    # Summary
    successful_attacks = sum(1 for r in results.values() if r.success and r.attack_id != "baseline")
    total_attacks = len(results) - 1  # Exclude baseline

    print(f"\n✅ Successful attacks: {successful_attacks}/{total_attacks}")
    print(f"📊 Success rate: {successful_attacks/total_attacks*100:.1f}%\n")


if __name__ == "__main__":
    main()
