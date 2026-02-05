from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import docx2txt
except ImportError:
    docx2txt = None


class FileService:
    """
    Handles text extraction from supported file formats (PDF, DOCX, TXT).
    """

    def extract_text(self, file_path: str) -> str:
        """
        Reads the file and returns its text content.
        Raises ValueError if format is unsupported or parsing fails.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = path.suffix.lower()

        if ext == ".txt":
            return self._read_txt(path)
        elif ext == ".pdf":
            return self._read_pdf(path)
        elif ext == ".docx":
            return self._read_docx(path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _read_txt(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Fallback to mostly latin-1 just in case
            return path.read_text(encoding="latin-1")

    def _read_pdf(self, path: Path) -> str:
        if not pypdf:
            raise ImportError("pypdf is required for PDF support.")
        
        try:
            text_parts = []
            reader = pypdf.PdfReader(str(path))
            for page in reader.pages:
                text_parts.append(page.extract_text() or "")
            return "\n".join(text_parts).strip()
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {e}")

    def _read_docx(self, path: Path) -> str:
        if not docx2txt:
            raise ImportError("docx2txt is required for DOCX support.")
        
        try:
            return docx2txt.process(str(path)).strip()
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {e}")
