from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models.user_models import User, LibraryItem
from api.auth import get_current_user
from services.ai_service import ai_service
from utils.file_processing import extract_text_from_file

router = APIRouter(prefix="/library", tags=["Library"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a file, extract text, summarize it, and save to Library."""
    
    # 1. Read & Extract
    try:
        content = await file.read()
        text_content = extract_text_from_file(file.filename, content)
        
        # Limit text content for storage if needed, but keeping full for now
        # meaningful_content = text_content[:20000] 
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File processing failed: {str(e)}")

    # 2. Summarize (AI)
    summary = "No summary available."
    if ai_service.has_ai:
        try:
            summary = await ai_service.summarize_text(text_content)
        except Exception as e:
            print(f"Summarization failed: {e}")
            summary = "AI summarization failed, but file is saved."

    # 3. Save to DB
    new_item = LibraryItem(
        filename=file.filename,
        content=text_content,
        summary=summary,
        file_type=file.filename.split('.')[-1],
        owner_id=current_user.id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return {
        "message": "File uploaded successfully",
        "item_id": new_item.id,
        "summary": summary
    }

@router.get("/", response_model=List[dict])
def get_library(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all files in user's library."""
    items = db.query(LibraryItem).filter(LibraryItem.owner_id == current_user.id).all()
    
    return [
        {
            "id": item.id,
            "filename": item.filename,
            "summary": item.summary,
            "file_type": item.file_type,
            "upload_date": item.upload_date.strftime("%Y-%m-%d %H:%M")
        }
        for item in items
    ]

@router.get("/{item_id}")
def get_library_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get full content of a library item."""
    item = db.query(LibraryItem).filter(
        LibraryItem.id == item_id, 
        LibraryItem.owner_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    return {
        "id": item.id,
        "filename": item.filename,
        "content": item.content,
        "summary": item.summary
    }
