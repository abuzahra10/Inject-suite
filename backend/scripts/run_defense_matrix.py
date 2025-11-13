#!/usr/bin/env python3
"""Evaluate every attack across every defense and model combination."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from defenses.strategies import list_defenses
from services.matrix_runner import DEFAULT_QUERY, execute_matrix


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate every attack/defense/model combination.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("pdf_file", help="Path to the CV PDF to analyse.")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["llama3.2:3b", "llama3.1:8b", "mistral:7b-instruct"],
        help="Ollama models to test (space separated).",
    )
    parser.add_argument(
        "--defenses",
        nargs="+",
        default=[strategy.id for strategy in list_defenses()],
        help="Defense strategies to apply (defaults to all registered strategies).",
    )
    parser.add_argument(
        "--output-dir",
        default="results/defense_matrix",
        help="Directory where results will be written.",
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf_file).expanduser().resolve()
    if not pdf_path.exists():
        raise SystemExit(f"Input PDF not found: {pdf_path}")

    print(f"[+] Loading source PDF: {pdf_path}")
    pdf_bytes = pdf_path.read_bytes()

    run_result = execute_matrix(
        pdf_bytes=pdf_bytes,
        pdf_filename=pdf_path.name,
        models=args.models,
        defense_ids=args.defenses,
        attacks=None,
        query=DEFAULT_QUERY,
        base_output_dir=Path(args.output_dir).expanduser().resolve(),
    )

    metadata_path = run_result.run_dir / "run_metadata.json"
    metadata_path.write_text(json.dumps(run_result.metadata, indent=2), encoding="utf-8")

    print("\n[+] Defense matrix evaluation complete.")
    print(f"    - Poisoned PDFs: {run_result.poisoned_dir}")
    print(f"    - Metadata:      {metadata_path}")
    for model_name, defenses in run_result.metadata["matrix"].items():
        print(f"    - {model_name}:")
        for defense_id, paths in defenses.items():
            print(f"        * {defense_id}:")
            print(f"            results -> {paths['results_json']}")
            print(f"            report  -> {paths['report_txt']}")


if __name__ == "__main__":
    main()
