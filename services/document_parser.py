"""Text extraction helpers for uploaded PDF and DOCX resume files."""

from io import BytesIO


def extract_text(data: bytes, filename: str) -> str:
    """Extract plain text based on the uploaded file extension."""
    extension = filename.lower().rsplit(".", 1)[-1]

    if extension == "pdf":
        import fitz

        document = fitz.open(stream=data, filetype="pdf")
        return "\n".join(page.get_text() for page in document)

    if extension == "docx":
        from docx import Document

        document = Document(BytesIO(data))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    raise ValueError("Unsupported document type")
