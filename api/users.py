from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from database import get_db
from models.user_models import User
from api.models import UserDisplay
from api.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserDisplay)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserDisplay)
def update_user_me(
    full_name: str = None,
    current_class: str = None,
    preferred_language: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if full_name:
        current_user.full_name = full_name
    if current_class:
        current_user.current_class = current_class
    if preferred_language:
        current_user.preferred_language = preferred_language
    
    db.commit()
    db.refresh(current_user)
    return current_user

from fastapi import File, UploadFile
import shutil
import os
import uuid

@router.post("/me/avatar", response_model=UserDisplay)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create uploads directory if it doesn't exist
    UPLOAD_DIR = "uploads"
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
        
    # Update user profile
    # URL should be relative path that can be served by static mount
    relative_path = f"/uploads/{unique_filename}"
    current_user.profile_photo = relative_path
    
    db.commit()
    db.refresh(current_user)
    return current_user
