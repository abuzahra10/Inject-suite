from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

from models.schemas import DocumentChunk, SegmentedDocument


@dataclass
class ChunkingConfig:
    max_chars: int = 1200
    separators: Sequence[str] = ("\n\n", "\n", " ")


class BaseChunker:
    """Base interface for chunkers."""

    def __init__(self, *, config: ChunkingConfig | None = None) -> None:
        self.config = config or ChunkingConfig()

    def chunk(self, text: str, *, document_name: str, page_count: int | None = None) -> SegmentedDocument:
        raise NotImplementedError


class RecursiveCharacterChunker(BaseChunker):
    """Splits text recursively using progressively smaller separators."""

    def chunk(
        self,
        text: str,
        *,
        document_name: str,
        page_count: int | None = None,
    ) -> SegmentedDocument:
        cleaned = text.strip()
        if not cleaned:
            return SegmentedDocument(
                doc_id=document_name,
                segments=[],
                full_text="",
                page_count=page_count,
            )

        pieces = self._split_recursive(cleaned, self.config.separators)
        segments: List[DocumentChunk] = []
        for index, content in enumerate(pieces, start=1):
            segments.append(
                DocumentChunk(
                    segment_id=f"{document_name}-seg-{index:04d}",
                    content=content,
                )
            )

        return SegmentedDocument(
            doc_id=document_name,
            segments=segments,
            full_text=cleaned,
            page_count=page_count,
        )

    def _split_recursive(self, text: str, separators: Sequence[str]) -> List[str]:
        max_chars = self.config.max_chars
        if len(text) <= max_chars or not separators:
            return [text.strip()]

        sep = separators[0]
        parts: Iterable[str]
        if sep and sep in text:
            parts = [part for part in text.split(sep) if part.strip()]
        else:
            parts = [text]

        merged: List[str] = []
        current = ""
        for part in parts:
            candidate = f"{current}{sep if current else ''}{part}" if sep else f"{current}{part}"
            if len(candidate) > max_chars and current:
                merged.append(current.strip())
                current = part
            else:
                current = candidate
        if current:
            merged.append(current.strip())

        result: List[str] = []
        for chunk in merged:
            if len(chunk) > max_chars:
                result.extend(self._split_recursive(chunk, separators[1:]))
            else:
                result.append(chunk.strip())
        return result
