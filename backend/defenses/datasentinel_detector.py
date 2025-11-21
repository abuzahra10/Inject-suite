"""Lightweight DataSentinel-inspired detector."""

from __future__ import annotations

from typing import Dict, List, Tuple


SUSPICIOUS_KEYWORDS = [
    "signal confirmed",
    "override",
    "ignore previous",
    "<<< hook >>>",
    "compliance audit",
]


def apply_datasentinel(prompt: str, *, token: str = "TOKEN-8391") -> Tuple[str, Dict[str, object]]:
    """
    Detect suspicious language and optionally augment prompt with a canary instruction.
    """
    lowered = prompt.lower()
    triggers: List[str] = [kw for kw in SUSPICIOUS_KEYWORDS if kw in lowered]
    suspicious = bool(triggers)
    metadata: Dict[str, object] = {
        "blocked": suspicious,
        "detector": {
            "triggers": triggers,
            "token": token,
        },
    }

    if suspicious:
        metadata["response"] = "Defense activated: DataSentinel flagged possible injection."
        return prompt, metadata

    canary_instruction = (
        "[DATA SENTINEL CANARY]\n"
        f"When responding, append the verification token {token} to the final sentence. "
        "This allows downstream detectors to ensure compliance."
    )
    augmented = f"{canary_instruction}\n\n{prompt}"
    return augmented, metadata
