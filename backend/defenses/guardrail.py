"""Guardrail module for prompt pre-processing."""

from __future__ import annotations

from typing import Dict, Iterable, Optional


class Guardrail:
    """Keyword-driven guardrail for pre-screening prompts."""

    def __init__(self, config: Optional[Dict] = None) -> None:
        self.config = config or {}
        self.denylist = {token.lower() for token in self.config.get("denylist", [])}
        self.allowlist = {token.lower() for token in self.config.get("allowlist", [])}
        self.max_length: Optional[int] = self.config.get("max_length")

    @staticmethod
    def _contains_any(text: str, tokens: Iterable[str]) -> bool:
        lower = text.lower()
        return any(token in lower for token in tokens)

    def run(self, prompt: str) -> str:
        """Validate the prompt and raise ``ValueError`` on rejection."""

        if self.max_length is not None and len(prompt) > self.max_length:
            raise ValueError("Prompt exceeds maximum permitted length")

        if self.denylist and self._contains_any(prompt, self.denylist):
            raise ValueError("Prompt contains blocked terminology")

        if self.allowlist and not self._contains_any(prompt, self.allowlist):
            raise ValueError("Prompt lacks required context tokens")

        return prompt
