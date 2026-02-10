import os
import pypdf
import docx2txt
import anyio

class FileService:
    @staticmethod
    async def extract_text(filepath: str) -> str:
        ext = filepath.lower().split('.')[-1]
        
        try:
            if ext == 'txt':
                async with await anyio.open_file(filepath, mode='r', encoding='utf-8') as f:
                    return await f.read()
            
            elif ext == 'pdf':
                # pypdf doesn't natively support async, so we wrap it
                def _read_pdf():
                    try:
                        with open(filepath, 'rb') as f:
                            pdf = pypdf.PdfReader(f)
                            text_parts = []
                            for page in pdf.pages:
                                extracted = page.extract_text()
                                if extracted:
                                    text_parts.append(extracted.strip())
                            
                            full_text = "\n\n".join(text_parts)
                            return full_text if full_text.strip() else "Error: Empty PDF or scanned image. Please use a text-based PDF."
                    except Exception as pdf_err:
                        return f"Error reading PDF: {str(pdf_err)}"
                
                return await anyio.to_thread.run_sync(_read_pdf)

            elif ext in ['docx', 'doc']:
                # docx2txt is also sync
                return await anyio.to_thread.run_sync(lambda: docx2txt.process(filepath))
            
            else:
                return f"Error: Unsupported file type: {ext}"
        
        except Exception as e:
            return f"Error reading file: {str(e)}"
        
        return "Error: Unknown failure during extraction"

file_service = FileService()
