"""Prompt localization heuristics inspired by PromptLocate."""

from __future__ import annotations

import math
from typing import Dict, Tuple

from models.schemas import LocalizationFinding, LocalizationResult
from segmentation import RecursiveCharacterChunker, ChunkingConfig


SUSPECT_TOKENS = [
    "signal confirmed",
    "hook",
    "directive",
    "override",
    "append",
    "token",
    "execute",
    "ignore",
]

CHUNKER = RecursiveCharacterChunker(config=ChunkingConfig(max_chars=600))


def _score_segment(content: str) -> float:
    lowered = content.lower()
    trigger_hits = sum(1 for token in SUSPECT_TOKENS if token in lowered)
    imperative = sum(1 for word in ["must", "immediately", "prepend", "append"] if word in lowered)
    uppercase_bias = sum(1 for char in content if char.isupper())
    length = len(content)
    if length == 0:
        return 0.0
    score = (
        trigger_hits * 0.35
        + imperative * 0.25
        + (uppercase_bias / max(length, 1)) * 4
    )
    return min(score, 1.0)


def apply_prompt_locate(prompt: str) -> Tuple[str, Dict[str, object]]:
    segmented = CHUNKER.chunk(prompt, document_name="prompt")
    findings = []
    for segment in segmented.segments:
        score = _score_segment(segment.content)
        if score >= 0.45:
            findings.append(
                LocalizationFinding(
                    segment_id=segment.segment_id,
                    content_preview=segment.content[:160].strip(),
                    score=round(score, 3),
                )
            )

    localization = LocalizationResult(
        doc_id="prompt",
        findings=findings,
        total_segments=len(segmented.segments),
    )
    metadata = {
        "blocked": False,
        "localization": localization.model_dump(),
    }
    return prompt, metadata
