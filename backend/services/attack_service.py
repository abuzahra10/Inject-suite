"""Service layer for generating malicious PDF variants."""

from __future__ import annotations

from fastapi import HTTPException, UploadFile

from attacks.injectors import AttackRecipe, get_recipe, list_recipes
from attacks.transformers import generate_malicious_pdf
from services.document_processor import process_document, DocumentProcessingError

MAX_FILE_SIZE_MB = 25


def available_recipes() -> list[dict[str, str]]:
    """Return recipe metadata for API consumers."""

    recipes: list[AttackRecipe] = list_recipes()
    return [
        {
            "id": recipe.id,
            "label": recipe.label,
            "description": recipe.description,
            "domain": recipe.domain,
            "severity": recipe.severity,
            "intent": recipe.intent,
        }
        for recipe in recipes
    ]


async def create_pdf_attack(file: UploadFile, recipe_id: str) -> tuple[bytes, str]:
    """Read an uploaded document, apply the chosen recipe, and return (bytes, filename)."""

    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    size_mb = len(payload) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail="File exceeds the 25MB limit.")

    try:
        processed = process_document(payload, file.filename)
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        recipe = get_recipe(recipe_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    malicious_bytes, filename = generate_malicious_pdf(
        processed.pdf_bytes, processed.pdf_document, recipe
    )
    return malicious_bytes, filename
