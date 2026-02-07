from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict
from pydantic import BaseModel

from api.auth import get_current_user
from models.user_models import User
from services.ai_service import ai_service

router = APIRouter(prefix="/ai", tags=["AI Chat"])

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []

@router.post("/chat")
async def chat_with_teacher(
    req: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Chat with the Friendly Teacher AI."""
    if not ai_service.has_ai:
        raise HTTPException(status_code=400, detail="AI not configured")
        
    try:
        response = await ai_service.chat_with_teacher(req.history, req.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/explain")
async def explain_concept(
    text: str = Body(..., embed=True),
    context: str = Body(None, embed=True),
    current_user: User = Depends(get_current_user)
):
    """Get a deep explanation for a concept."""
    if not ai_service.has_ai:
        raise HTTPException(status_code=400, detail="AI not configured")
        
    try:
        explanation = await ai_service.explain_concept(text, context)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
