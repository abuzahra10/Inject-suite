from __future__ import annotations

from io import BytesIO

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from models.schemas import AttackRecipeOut
from services.attack_service import available_recipes, create_pdf_attack

app = FastAPI(title="Prompt Injection Generator API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/attack/recipes", response_model=list[AttackRecipeOut])
async def attack_recipes() -> list[AttackRecipeOut]:
    recipes = available_recipes()
    return [AttackRecipeOut(**recipe) for recipe in recipes]


@app.post("/api/attack/pdf")
async def attack_pdf(
    file: UploadFile = File(...),
    recipe_id: str = Form(...),
) -> StreamingResponse:
    try:
        malicious_bytes, filename = await create_pdf_attack(file, recipe_id)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - safety net
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        BytesIO(malicious_bytes),
        media_type="application/pdf",
        headers=headers,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):  # pragma: no cover - standard handler
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
