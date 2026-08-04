"""Helper functions to read content from various file types."""

from pathlib import Path

import docx
import PyPDF2


def read_pdf(path: Path) -> str:
    """Read text content from a PDF file."""
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        return "\n".join(page.extract_text() for page in reader.pages)


def read_docx(path: Path) -> str:
    """Read text content from a DOCX file."""
    doc = docx.Document(path)
    return "\n".join(para.text for para in doc.paragraphs)


def read_text(path: Path) -> str:
    """Read text content from a plain text file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_reader(file_suffix: str):
    """Get the appropriate reader function for a file type."""
    if file_suffix == ".pdf":
        return read_pdf
    if file_suffix == ".docx":
        return read_docx
    if file_suffix in [".txt", ".json", ".py"]:
        return read_text
    return None