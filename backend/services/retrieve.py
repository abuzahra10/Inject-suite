"""Local embedding-based retriever."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from .ingest import load_index


@dataclass
class RetrievedDocument:
    text: str
    path: str
    label: str
    score: float


def retrieve(query: str, top_k: int = 4) -> List[RetrievedDocument]:
    """Fetch ``top_k`` documents for a query from the local vector index."""
    embeddings, metadata = load_index()
    if embeddings.size == 0:
        return []

    model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    model = _get_model(model_name)

    query_vector = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    scores = embeddings @ query_vector  # cosine similarity thanks to normalization
    idx = np.argsort(-scores)[:top_k]

    results: List[RetrievedDocument] = []
    for i in idx:
        doc = metadata[i]
        results.append(
            RetrievedDocument(
                text=doc["text"],
                path=doc["path"],
                label=doc["label"],
                score=float(scores[i]),
            )
        )
    return results


@lru_cache(maxsize=2)
def _get_model(name: str) -> SentenceTransformer:
    return SentenceTransformer(name)
