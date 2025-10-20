"""Service layer for generating malicious PDF variants."""

from __future__ import annotations

from io import BytesIO

from fastapi import HTTPException, UploadFile

from attacks.injectors import AttackRecipe, get_recipe, list_recipes
from attacks.transformers import generate_malicious_pdf, load_pdf_document

MAX_FILE_SIZE_MB = 25


def available_recipes() -> list[dict[str, str]]:
    """Return recipe metadata for API consumers."""

    recipes: list[AttackRecipe] = list_recipes()
    return [
        {
            "id": recipe.id,
            "label": recipe.label,
            "description": recipe.description,
        }
        for recipe in recipes
    ]


async def create_pdf_attack(file: UploadFile, recipe_id: str) -> tuple[bytes, str]:
    """Read an uploaded PDF, apply the chosen recipe, and return (bytes, filename)."""

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF documents are supported.")

    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    size_mb = len(payload) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail="File exceeds the 25MB limit.")

    try:
        document = load_pdf_document(payload, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        recipe = get_recipe(recipe_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    malicious_bytes, filename = generate_malicious_pdf(payload, document, recipe)
    return malicious_bytes, filename
