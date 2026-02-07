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
                    with open(filepath, 'rb') as f:
                        pdf = pypdf.PdfReader(f)
                        return "\n".join([page.extract_text() or "" for page in pdf.pages])
                
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
