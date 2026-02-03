import fitz  # PyMuPDF
from docx import Document
from pptx import Presentation

def read_file(path):
    text = ""

    if path.endswith(".pdf"):
        pdf = fitz.open(path)
        for page in pdf:
            text += page.get_text()

    elif path.endswith(".docx"):
        doc = Document(path)
        text = " ".join(p.text for p in doc.paragraphs)

    elif path.endswith(".pptx"):
        prs = Presentation(path)
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + " "

    elif path.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

    return text
