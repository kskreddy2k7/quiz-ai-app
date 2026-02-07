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


