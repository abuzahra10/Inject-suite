from __future__ import annotations

from pydantic import BaseModel


class AttackRecipeOut(BaseModel):
    id: str
    label: str
    description: str


class AttackResponse(BaseModel):
    filename: str
    detail: str
