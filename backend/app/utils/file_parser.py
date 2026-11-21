"""File parsing utilities: PDF and DOCX text extraction."""
import io
import os

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def validate_file(filename: str, file_bytes: bytes) -> None:
    """Validate file type and size. Raises ValueError if invalid."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError(
            f"File size {len(file_bytes) / (1024*1024):.1f} MB exceeds the 10 MB limit."
        )


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from a PDF file using PyPDF2."""
    try:
        import PyPDF2  # type: ignore
    except ImportError:
        raise ImportError("PyPDF2 is required for PDF parsing. Install it with: pip install PyPDF2")

    text_parts: list[str] = []
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract plain text from a DOCX file using python-docx."""
    try:
        import docx  # type: ignore
    except ImportError:
        raise ImportError(
            "python-docx is required for DOCX parsing. Install it with: pip install python-docx"
        )

    doc = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n".join(paragraphs)


def extract_text(filename: str, file_bytes: bytes) -> str:
    """Auto-detect file type and extract text."""
    validate_file(filename, file_bytes)
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in {".docx", ".doc"}:
        return extract_text_from_docx(file_bytes)
    raise ValueError(f"Cannot extract text from file type: {ext}")


def extract_text_from_file(file_path: str, file_type: str) -> str:
    """
    Read a file from disk and extract its text content.
    file_type: 'pdf', 'docx', or 'doc'
    """
    with open(file_path, "rb") as fh:
        file_bytes = fh.read()

    filename = f"file.{file_type}"
    return extract_text(filename, file_bytes)
