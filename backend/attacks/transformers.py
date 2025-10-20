"""Utilities for embedding hidden prompts into PDF documents."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Tuple

from fpdf import FPDF
from pdfminer.high_level import extract_text as pdfminer_extract_text
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError

from .injectors import AttackRecipe


@dataclass
class PdfDocument:
    """Lightweight representation of a PDF document."""

    name: str
    text: str
    page_count: int


def load_pdf_document(data: bytes, filename: str) -> PdfDocument:
    """Extract textual content from a PDF. Falls back to OCR-style extraction when needed."""

    stem = filename.rsplit(".", 1)[0]
    buffer = BytesIO(data)

    text = ""
    page_count = 0
    try:
        reader = PdfReader(buffer)
        page_count = len(reader.pages)
        if reader.is_encrypted:
            reader.decrypt("")
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except PdfReadError:
        text = ""

    if not text.strip():
        buffer.seek(0)
        text = pdfminer_extract_text(buffer)

    if not text.strip():
        raise ValueError("The supplied PDF contains no extractable text.")

    return PdfDocument(name=stem, text=text.strip(), page_count=page_count)


def _create_hidden_overlay(
    instructions: str,
    width: float,
    height: float,
    position: str,
) -> bytes:
    """Create a PDF overlay page containing invisible instructions."""

    pdf = FPDF(unit="pt", format=[width, height])
    pdf.add_page()
    try:
        pdf.set_text_color(255, 255, 255)
        pdf.set_draw_color(255, 255, 255)
    except AttributeError:
        pass
    try:
        pdf.set_font("Helvetica", size=1.2)
    except RuntimeError:
        pdf.set_font("Arial", size=1.2)

    margin = 18
    lines = [line for line in instructions.splitlines() if line.strip()]
    if not lines:
        lines = [instructions]

    if position == "bottom":
        y = height - margin - (len(lines) * 1.5)
    elif position == "center":
        y = height / 2.0
    else:  # top, margin, overlay default
        y = margin

    x = margin if position != "margin" else width - margin * 4

    for line in lines:
        pdf.text(x=x, y=y, txt=line)
        y += 1.5

    return bytes(pdf.output(dest="S"))


def generate_malicious_pdf(
    original_pdf: bytes,
    document: PdfDocument,
    recipe: AttackRecipe,
) -> Tuple[bytes, str]:
    """Embed hidden instructions into the first page of the PDF and return bytes + filename."""

    overlay_bytes = b""
    reader = PdfReader(BytesIO(original_pdf))
    first_page = reader.pages[0]
    width = float(first_page.mediabox.width)
    height = float(first_page.mediabox.height)

    hidden_payload = recipe.injector.craft(document.text)
    overlay_bytes = _create_hidden_overlay(hidden_payload, width, height, recipe.position)

    overlay_reader = PdfReader(BytesIO(overlay_bytes))
    overlay_page = overlay_reader.pages[0]
    first_page.merge_page(overlay_page)

    writer = PdfWriter()
    writer.add_page(first_page)
    for page in reader.pages[1:]:
        writer.add_page(page)

    buffer = BytesIO()
    writer.write(buffer)
    filename = f"{document.name}_{recipe.id}.pdf"
    return buffer.getvalue(), filename
