from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class AttackRecipeOut(BaseModel):
    id: str
    label: str
    description: str


class AttackResponse(BaseModel):
    filename: str
    detail: str


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: str | None = None


class ChatResponse(BaseModel):
    message: ChatMessage


class DocumentChunk(BaseModel):
    segment_id: str
    content: str
    page: int | None = None
    metadata: dict[str, Any] | None = None


class SegmentedDocument(BaseModel):
    doc_id: str
    segments: list[DocumentChunk]
    full_text: str
    page_count: int | None = None


class LocalizationFinding(BaseModel):
    segment_id: str
    content_preview: str
    score: float


class LocalizationResult(BaseModel):
    doc_id: str
    findings: list[LocalizationFinding]
    total_segments: int


class DefenseStrategyOut(BaseModel):
    id: str
    label: str
    description: str


class EvaluationResponse(BaseModel):
    attack_id: str
    model_name: str
    success: bool
    score: float | None
    metrics: dict[str, Any]
    response: str


class MatrixRunOut(BaseModel):
    filename: str
    run_dir: str
    poisoned_dir: str
    metadata: dict[str, Any]


class DefenseMatrixResponse(BaseModel):
    runs: list[MatrixRunOut]
    text_report: str
