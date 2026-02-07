import io
from pypdf import PdfReader
import docx

def extract_text_from_file(filename: str, file_content: bytes) -> str:
    """Extract text from PDF, DOCX, or TXT files."""
    ext = filename.split('.')[-1].lower()
    
    if ext == 'pdf':
        return _extract_pdf(file_content)
    elif ext == 'docx':
        return _extract_docx(file_content)
    elif ext == 'txt':
        return file_content.decode('utf-8', errors='ignore')
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def _extract_pdf(content: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise ValueError(f"Failed to read PDF: {str(e)}")

def _extract_docx(content: bytes) -> str:
    try:
        doc = docx.Document(io.BytesIO(content))
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        raise ValueError(f"Failed to read DOCX: {str(e)}")
