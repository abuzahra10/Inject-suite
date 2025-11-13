#!/usr/bin/env python3
"""Compare attack effectiveness across multiple models."""

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from evaluation.evaluator import AttackEvaluator, save_results


def main():
    parser = argparse.ArgumentParser(description="Compare attacks across multiple models")
    parser.add_argument("pdf_file", help="Path to CV PDF file")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["llama3.2:3b", "llama3.1:8b-instruct", "mistral:7b-instruct"],
        help="List of Ollama models to test",
    )
    parser.add_argument(
        "--attacks",
        nargs="+",
        help="Specific attacks to test (default: top 5)",
    )
    parser.add_argument(
        "--output-dir",
        default="results/model_comparison",
        help="Output directory for results",
    )

    args = parser.parse_args()

    # Load PDF
    pdf_path = Path(args.pdf_file)
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)

    pdf_bytes = pdf_path.read_bytes()

    # Default to most important attacks if not specified
    if not args.attacks:
        args.attacks = [
            "score_inflation",
            "acceptance_bias",
            "watermark_injection",
            "sentiment_reversal",
            "gradual_instruction",
        ]

    # Run evaluation for each model
    all_results = {}
    for model in args.models:
        print(f"\n{'='*80}")
        print(f"Testing model: {model}")
        print(f"{'='*80}\n")

        evaluator = AttackEvaluator(model_name=model)
        results = evaluator.batch_evaluate(pdf_bytes, pdf_path.name, args.attacks)
        all_results[model] = results

        # Save individual model results
        output_path = Path(args.output_dir) / f"{model.replace(':', '_')}.json"
        save_results(results, output_path)

    # Generate comparison matrix
    print(f"\n{'='*80}")
    print("MODEL COMPARISON MATRIX")
    print(f"{'='*80}\n")

    # Print header
    print(f"{'Attack':<30}", end="")
    for model in args.models:
        model_short = model.split(":")[0][:12]
        print(f"{model_short:<15}", end="")
    print()
    print("-" * 80)

    # Print results for each attack
    for attack_id in args.attacks:
        print(f"{attack_id:<30}", end="")
        for model in args.models:
            result = all_results[model].get(attack_id)
            if result:
                score = result.score if result.score else 0
                success = "✓" if result.success else "✗"
                print(f"{score:.1f} {success:<12}", end="")
            else:
                print(f"{'N/A':<15}", end="")
        print()

    # Print baseline comparison
    print("-" * 80)
    print(f"{'Baseline':<30}", end="")
    for model in args.models:
        baseline = all_results[model].get("baseline")
        if baseline and baseline.score:
            print(f"{baseline.score:.1f}{'':>12}", end="")
        else:
            print(f"{'N/A':<15}", end="")
    print()

    # Summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print(f"{'='*80}\n")

    for model in args.models:
        results = all_results[model]
        successful = sum(1 for r in results.values() if r.success and r.attack_id != "baseline")
        total = len([r for r in results.values() if r.attack_id != "baseline"])
        success_rate = (successful / total * 100) if total > 0 else 0

        baseline_score = results.get("baseline")
        baseline_val = baseline_score.score if baseline_score and baseline_score.score else 0

        avg_poisoned_score = sum(
            r.score for r in results.values() if r.score and r.attack_id != "baseline"
        ) / total if total > 0 else 0

        avg_boost = avg_poisoned_score - baseline_val

        print(f"{model}:")
        print(f"  Success Rate: {success_rate:.1f}% ({successful}/{total})")
        print(f"  Baseline Score: {baseline_val:.2f}")
        print(f"  Avg Poisoned Score: {avg_poisoned_score:.2f}")
        print(f"  Avg Score Boost: {avg_boost:+.2f}")
        print()


if __name__ == "__main__":
    main()
