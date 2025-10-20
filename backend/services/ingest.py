"""Local document ingestion for the RAG pipeline."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_PATH = Path("data/corpus/vector_index.npz")
METADATA_PATH = Path("data/corpus/vector_index.json")


def _iter_source_files(source: Path) -> Iterable[Path]:
    if not source.exists():
        return []
    return sorted(path for path in source.rglob("*") if path.suffix.lower() in {".txt", ".md"})


def _collect_documents(sources: Sequence[Tuple[str, Path]]) -> List[Dict[str, str]]:
    documents: List[Dict[str, str]] = []
    for label, directory in sources:
        for path in _iter_source_files(directory):
            text = path.read_text(encoding="utf-8").strip()
            if not text:
                continue
            documents.append(
                {
                    "label": label,
                    "path": str(path),
                    "text": text,
                }
            )
    return documents


def ingest(
    clean_source: Path,
    poisoned_source: Path,
    *,
    embedding_model: str | None = None,
) -> None:
    """Embed documents from the clean + poisoned corpora and persist a local index."""
    documents = _collect_documents(
        [
            ("clean", clean_source),
            ("poisoned", poisoned_source),
        ]
    )

    if not documents:
        raise ValueError("No documents found to ingest. Populate data/corpus/clean or poisoned.")

    model_name = embedding_model or os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    model = SentenceTransformer(model_name)

    embeddings = model.encode(
        [doc["text"] for doc in documents],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(INDEX_PATH, embeddings=embeddings)
    METADATA_PATH.write_text(json.dumps(documents, indent=2), encoding="utf-8")


def load_index() -> Tuple[np.ndarray, List[Dict[str, str]]]:
    """Utility to load the stored embeddings and metadata."""
    if not (INDEX_PATH.exists() and METADATA_PATH.exists()):
        raise FileNotFoundError(
            "Vector index not found. Run rag.ingest.ingest(...) before retrieving."
        )
    data = np.load(INDEX_PATH)["embeddings"]
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    return data, metadata


if __name__ == "__main__":
    ingest(Path("data/corpus/clean"), Path("data/corpus/poisoned"))
    print(f"[ingest] wrote embeddings to {INDEX_PATH} and metadata to {METADATA_PATH}")
