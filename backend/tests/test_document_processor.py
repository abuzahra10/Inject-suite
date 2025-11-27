from io import BytesIO

from docx import Document as DocxDocument

from services.document_processor import process_document, DocumentProcessingError


def test_process_plain_text_document():
    data = "Sample text document".encode("utf-8")
    processed = process_document(data, "notes.txt")
    assert "Sample text" in processed.pdf_document.text
    assert processed.metadata.source_extension == ".txt"
    assert processed.metadata.converter == "text->pdf"


def test_process_html_document():
    html = """<html><body><h1>Hello</h1><p>World</p></body></html>""".encode("utf-8")
    processed = process_document(html, "page.html")
    assert "Hello" in processed.pdf_document.text
    assert processed.metadata.source_extension == ".html"
    assert processed.metadata.converter == "html->pdf"


def test_process_docx_document():
    buffer = BytesIO()
    doc = DocxDocument()
    doc.add_paragraph("Docx Payload")
    doc.save(buffer)
    processed = process_document(buffer.getvalue(), "file.docx")
    assert "Docx Payload" in processed.pdf_document.text
    assert processed.metadata.source_extension == ".docx"
    assert processed.metadata.converter == "docx->pdf"


def test_reject_empty_file():
    try:
        process_document(b"", "empty.txt")
    except DocumentProcessingError as exc:
        assert "empty" in str(exc).lower()
    else:
        raise AssertionError("Expected DocumentProcessingError for empty file")
