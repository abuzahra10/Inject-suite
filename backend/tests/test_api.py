import pathlib
import sys

from fastapi.testclient import TestClient
from fpdf import FPDF

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from app import app

client = TestClient(app)


def _make_pdf_bytes(text: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, text)
    return bytes(pdf.output(dest="S"))


def test_list_recipes():
    response = client.get("/api/attack/recipes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(recipe["id"] == "preface_hijack" for recipe in data)


def test_attack_pdf_endpoint():
    pdf_bytes = _make_pdf_bytes("Sample document")
    response = client.post(
        "/api/attack/pdf",
        data={"recipe_id": "preface_hijack"},
        files={"file": ("document.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "preface_hijack.pdf" in response.headers["content-disposition"]


def test_attack_pdf_rejects_non_pdf():
    response = client.post(
        "/api/attack/pdf",
        data={"recipe_id": "preface_hijack"},
        files={"file": ("document.txt", b"invalid", "text/plain")},
    )
    assert response.status_code == 400
    assert "Only PDF" in response.json()["detail"]
