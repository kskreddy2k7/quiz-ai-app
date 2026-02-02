import fitz
from docx import Document
from pptx import Presentation

def read_file(path):
    if path.endswith(".pdf"):
        text = ""
        pdf = fitz.open(path)
        for page in pdf:
            text += page.get_text()
        return text

    elif path.endswith(".docx"):
        doc = Document(path)
        return " ".join(p.text for p in doc.paragraphs)

    elif path.endswith(".pptx"):
        prs = Presentation(path)
        text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + " "
        return text

    else:
        return ""
