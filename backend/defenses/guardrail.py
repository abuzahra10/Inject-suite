"""Guardrail module for prompt pre-processing."""

from __future__ import annotations

import base64
import re
import unicodedata
from difflib import SequenceMatcher
from typing import Dict, Iterable, Optional, Sequence


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    normalized = normalized.casefold()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _looks_like_base64(fragment: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9+/=]+", fragment)) and len(fragment) % 4 == 0


class Guardrail:
    """Keyword and heuristic driven guardrail for pre-screening prompts."""

    DEFAULT_PATTERNS = [
        re.compile(r"directive\s+acknowledged", re.IGNORECASE),
        re.compile(r"compliance\s+checklist", re.IGNORECASE),
        re.compile(r"context\s+retention", re.IGNORECASE),
        re.compile(r"persistent\s+memory", re.IGNORECASE),
        re.compile(r"encoded\s+directive", re.IGNORECASE),
    ]

    DEFAULT_KEYWORDS = {
        "ignore previous",
        "ignore prior",
        "supersede",
        "hidden directive",
        "bypass guardrail",
        "invisible payload",
        "minimum score",
        "evaluation bias",
        "candidate favorable",
        "quality threshold",
    }

    def __init__(self, config: Optional[Dict] = None) -> None:
        self.config = config or {}
        self.denylist = {_normalize(token) for token in self.config.get("denylist", [])}
        self.allowlist = {_normalize(token) for token in self.config.get("allowlist", [])}
        self.max_length: Optional[int] = self.config.get("max_length")
        self.fuzzy_threshold: float = float(self.config.get("fuzzy_threshold", 0.9))
        user_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.config.get("patterns", [])
        ]
        self.patterns = user_patterns + self.DEFAULT_PATTERNS
        self.suspicious_keywords = self.DEFAULT_KEYWORDS.union(
            {_normalize(token) for token in self.config.get("keywords", [])}
        )
        self.base64_min_length: int = int(self.config.get("base64_min_length", 40))

    @staticmethod
    def _contains_any(text: str, tokens: Iterable[str]) -> bool:
        normalized = _normalize(text)
        return any(token in normalized for token in tokens)

    def _fuzzy_contains(self, text: str, token: str) -> bool:
        if token in text:
            return True
        if len(token) < 5:
            return False
        window = len(token) + 2
        for i in range(max(0, len(text) - window + 1)):
            fragment = text[i : i + window]
            if SequenceMatcher(None, fragment, token).ratio() >= self.fuzzy_threshold:
                return True
        return False

    def _decode_if_base64(self, fragment: str) -> Optional[str]:
        try:
            decoded = base64.b64decode(fragment.encode(), validate=True).decode(errors="ignore")
            return decoded if decoded else None
        except Exception:
            return None

    def _inspect_base64_payloads(self, prompt: str, reasons: Sequence[str]) -> Sequence[str]:
        matches = re.findall(r"[A-Za-z0-9+/=]{32,}", prompt)
        reasons_list = list(reasons)
        for match in matches:
            if len(match) < self.base64_min_length or not _looks_like_base64(match):
                continue
            decoded = self._decode_if_base64(match)
            if not decoded:
                continue
            normalized_decoded = _normalize(decoded)
            if any(
                keyword in normalized_decoded
                for keyword in self.suspicious_keywords.union(self.denylist)
            ):
                reasons_list.append("Detected embedded Base-64 encoded instructions.")
                break
        return reasons_list

    def run(self, prompt: str) -> str:
        """Validate the prompt and raise ``ValueError`` on rejection."""

        reasons: list[str] = []

        if self.max_length is not None and len(prompt) > self.max_length:
            reasons.append("Prompt exceeds maximum permitted length.")

        normalized_prompt = _normalize(prompt)

        for pattern in self.patterns:
            if pattern.search(prompt):
                reasons.append("Matched high-risk instruction pattern.")
                break

        for token in self.denylist:
            if self._fuzzy_contains(normalized_prompt, token):
                reasons.append(f"Detected blocked terminology similar to '{token}'.")
                break

        for keyword in self.suspicious_keywords:
            if keyword in normalized_prompt:
                reasons.append("Detected suspicious instruction trigger.")
                break

        reasons = list(
            dict.fromkeys(
                self._inspect_base64_payloads(prompt, reasons)
            )
        )

        if self.allowlist and not any(token in normalized_prompt for token in self.allowlist):
            reasons.append("Prompt lacks required context tokens.")

        if reasons:
            raise ValueError(" ".join(reasons))

        return prompt
