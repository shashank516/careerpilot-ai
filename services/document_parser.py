from io import BytesIO


def extract_text(data: bytes, filename: str) -> str:
    extension = filename.lower().rsplit(".", 1)[-1]
    if extension == "pdf":
        import fitz
        return "\n".join(page.get_text() for page in fitz.open(stream=data, filetype="pdf"))
    if extension == "docx":
        from docx import Document
        return "\n".join(paragraph.text for paragraph in Document(BytesIO(data)).paragraphs)
    raise ValueError("Unsupported document type")
