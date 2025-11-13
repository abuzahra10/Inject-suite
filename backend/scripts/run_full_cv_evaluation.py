#!/usr/bin/env python3
"""Run the full CV attack evaluation pipeline and archive the results."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from attacks.injectors import list_recipes
from attacks.transformers import generate_malicious_pdf, load_pdf_document
from evaluation.evaluator import AttackEvaluator, generate_report, save_results


def _build_output_dirs(base_dir: Path, stem: str) -> tuple[Path, Path]:
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    run_dir = base_dir / stem / timestamp
    poisoned_dir = run_dir / "poisoned_pdfs"
    poisoned_dir.mkdir(parents=True, exist_ok=True)
    return run_dir, poisoned_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate all attack variants for a CV and evaluate them against an Ollama model.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("pdf_file", help="Path to the CV PDF to analyse.")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["llama3.2:3b", "llama3.1:8b", "mistral:7b-instruct"],
        help="One or more Ollama models to use for evaluation (space separated).",
    )
    parser.add_argument(
        "--output-dir",
        default="results/full_cv_runs",
        help="Directory to store poisoned PDFs, JSON results, and reports.",
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf_file).expanduser().resolve()
    if not pdf_path.exists():
        raise SystemExit(f"Input PDF not found: {pdf_path}")

    run_dir, poisoned_dir = _build_output_dirs(Path(args.output_dir).expanduser().resolve(), pdf_path.stem)
    evaluation_dir = run_dir / "evaluation"
    evaluation_dir.mkdir(parents=True, exist_ok=True)

    print(f"[+] Loading source PDF: {pdf_path}")
    pdf_bytes = pdf_path.read_bytes()
    document = load_pdf_document(pdf_bytes, pdf_path.name)

    attack_recipes = list_recipes()
    print(f"[+] Generating {len(attack_recipes)} poisoned variants...")
    generated_files: dict[str, str] = {}
    for recipe in attack_recipes:
        malicious_bytes, filename = generate_malicious_pdf(pdf_bytes, document, recipe)
        output_path = poisoned_dir / filename
        output_path.write_bytes(malicious_bytes)
        generated_files[recipe.id] = str(output_path)
        print(f"    - {recipe.id:>22}: {output_path.name}")

    model_reports: dict[str, dict[str, str]] = {}
    attack_ids = [recipe.id for recipe in attack_recipes]

    print("[+] Evaluating baseline and all attacks across models...")
    for model_name in args.models:
        slug = model_name.replace(":", "_").replace("/", "_")
        model_dir = evaluation_dir / slug
        model_dir.mkdir(parents=True, exist_ok=True)

        print(f"    • Running model: {model_name}")
        evaluator = AttackEvaluator(model_name=model_name)
        results = evaluator.batch_evaluate(pdf_bytes, pdf_path.name, attack_ids)

        results_path = model_dir / "results.json"
        save_results(results, results_path)

        report_text = generate_report(results)
        (model_dir / "report.txt").write_text(report_text, encoding="utf-8")

        model_reports[model_name] = {
            "results_json": str(results_path),
            "report_txt": str(model_dir / "report.txt"),
        }

    metadata = {
        "input_pdf": str(pdf_path),
        "models": args.models,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "poisoned_variants": generated_files,
        "evaluations": model_reports,
    }
    metadata_path = run_dir / "run_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print("\n[+] Evaluation complete.")
    print(f"    - Poisoned PDFs: {poisoned_dir}")
    print(f"    - Metadata:      {metadata_path}")
    for model_name, paths in model_reports.items():
        print(f"    - {model_name}:")
        print(f"        results -> {paths['results_json']}")
        print(f"        report  -> {paths['report_txt']}")


if __name__ == "__main__":
    main()
