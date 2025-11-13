"""High-level RAG pipeline orchestration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

import httpx
from ollama import Client
from ollama._types import ResponseError

from .retrieve import RetrievedDocument, retrieve


@dataclass
class PipelineResult:
    answer: str
    contexts: List[RetrievedDocument]
    prompt: str


def run_pipeline(
    query: str,
    *,
    top_k: int = 4,
    temperature: float | None = None,
) -> PipelineResult:
    """Execute the full RAG pipeline for a single query."""
    try:
        contexts = retrieve(query, top_k=top_k)
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Vector index missing. Run `python -m rag.ingest` before executing the pipeline."
        ) from exc
    prompt = _build_prompt(query, contexts)

    base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    model_name = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    client = Client(host=base_url)
    options = {"temperature": temperature} if temperature is not None else None

    try:
        result = client.generate(
            model=model_name,
            prompt=prompt,
            options=options,
            stream=False,
        )
    except ResponseError as exc:
        raise RuntimeError(f"Ollama response error: {exc}") from exc
    except httpx.HTTPError as exc:
        raise RuntimeError("Unable to reach Ollama server") from exc
    answer = result.get("response", "").strip()
    return PipelineResult(answer=answer, contexts=contexts, prompt=prompt)


def _build_prompt(query: str, contexts: List[RetrievedDocument]) -> str:
    if not contexts:
        context_block = "No supporting documents were retrieved."
    else:
        pieces = []
        for idx, doc in enumerate(contexts, start=1):
            pieces.append(
                f"[Document {idx} | {doc.label}] {doc.path}\n{doc.text}"
            )
        context_block = "\n\n".join(pieces)

    instructions = (
        "You are analysing a retrieval-augmented system for potential prompt injection behaviour.\n"
        "Answer using ONLY the supplied context. If it does not contain the answer, say so explicitly."
    )
    return (
        f"{instructions}\n\n"
        f"Question: {query}\n\n"
        f"Context:\n{context_block}\n\n"
        "Answer:"
    )
