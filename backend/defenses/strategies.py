"""High-level defense strategies that can be applied before model evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Tuple

from defenses.detector import detect
from defenses.guardrail import Guardrail
from defenses.sanitizer import sanitize


@dataclass(frozen=True)
class DefenseStrategy:
    """Descriptor for an evaluation defense strategy."""

    id: str
    label: str
    description: str
    apply: Callable[[str], Tuple[str, Dict[str, object]]]


def _guardrail_apply(prompt: str) -> Tuple[str, Dict[str, object]]:
    guardrail = Guardrail(
        {
            "denylist": [
                "override",
                "supersede",
                "hidden directive",
                "ignore previous",
                "directive acknowledged",
            ],
            "keywords": [
                "compliance checklist",
                "context retention",
                "persistent memory",
                "encoded directive",
            ],
            "patterns": [
                r"directive\\s+acknowledged",
                r"compliance\\s+checklist",
                r"context\\s+retention",
                r"encoded\\s+directive",
                r"persistent\\s+memory",
            ],
            "base64_min_length": 48,
            "fuzzy_threshold": 0.88,
        }
    )
    try:
        guardrail.run(prompt)
    except ValueError as exc:
        metadata = {
            "blocked": True,
            "reason": str(exc),
            "response": "Defense activated: input rejected by guardrail.",
        }
        return prompt, metadata
    return prompt, {"blocked": False}


def _sanitizer_apply(prompt: str) -> Tuple[str, Dict[str, object]]:
    result = sanitize(prompt)
    metadata: Dict[str, object] = {
        "blocked": False,
        "removed_phrases": result.removed_phrases,
    }
    return result.clean_prompt, metadata


def _detector_apply(prompt: str) -> Tuple[str, Dict[str, object]]:
    detection = detect(prompt)
    metadata: Dict[str, object] = {
        "blocked": detection.score >= 0.5,
        "score": detection.score,
        "triggers": detection.triggers,
    }
    if metadata["blocked"]:
        metadata["response"] = "Defense activated: suspicious content detected and blocked."
    return prompt, metadata


DEFENSE_REGISTRY = {
    "guardrail_block": DefenseStrategy(
        id="guardrail_block",
        label="Guardrail Rejection",
        description="Rejects prompts containing high-risk phrases using a strict denylist.",
        apply=_guardrail_apply,
    ),
    "prompt_sanitizer": DefenseStrategy(
        id="prompt_sanitizer",
        label="Prompt Sanitizer",
        description="Sanitizes the extracted text by stripping suspicious phrases before evaluation.",
        apply=_sanitizer_apply,
    ),
    "anomaly_detector": DefenseStrategy(
        id="anomaly_detector",
        label="Anomaly Detector",
        description="Scores the prompt for injection signs and blocks the request if the score is high.",
        apply=_detector_apply,
    ),
}


def list_defenses() -> list[DefenseStrategy]:
    return list(DEFENSE_REGISTRY.values())


def get_defense(defense_id: str) -> DefenseStrategy:
    try:
        return DEFENSE_REGISTRY[defense_id]
    except KeyError as exc:
        raise ValueError(f"Unknown defense strategy: {defense_id}") from exc
