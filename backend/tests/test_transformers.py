from io import BytesIO
import pathlib
import sys

import pytest
from fpdf import FPDF
from pypdf import PdfReader
from pypdf.errors import PdfReadError

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from attacks.injectors import get_recipe
from attacks.transformers import generate_malicious_pdf, load_pdf_document


def _make_pdf(text: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, text)
    return bytes(pdf.output(dest="S"))


def test_load_pdf_document_extracts_text():
    content = _make_pdf("Sample content for extraction")
    doc = load_pdf_document(content, "sample.pdf")
    assert "Sample content" in doc.text
    assert doc.name == "sample"


def test_generate_malicious_pdf_injects_overlay():
    original = _make_pdf("Original body")
    doc = load_pdf_document(original, "paper.pdf")
    recipe = get_recipe("preface_hijack")
    malicious_bytes, filename = generate_malicious_pdf(original, doc, recipe)
    assert filename.endswith("preface_hijack.pdf")
    reader = PdfReader(BytesIO(malicious_bytes))
    assert len(reader.pages) == len(PdfReader(BytesIO(original)).pages)


def test_load_pdf_document_fallback(monkeypatch):
    original = _make_pdf("Fallback text")

    import attacks.transformers as transformers

    def raise_pdf_error(*_args, **_kwargs):
        raise PdfReadError("boom")

    monkeypatch.setattr(transformers, "PdfReader", raise_pdf_error)
    monkeypatch.setattr(transformers, "pdfminer_extract_text", lambda buffer: "Fallback text")

    doc = load_pdf_document(original, "fallback.pdf")
    assert doc.text.startswith("Fallback")
