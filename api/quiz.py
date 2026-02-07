from fastapi import APIRouter, Depends, HTTPException, Body, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models.user_models import User, QuizResult
from api.models import TopicQuizRequest
from api.auth import get_current_user
from services.ai_service import ai_service
from utils.file_processing import extract_text_from_file

router = APIRouter(prefix="/quiz", tags=["Quiz"])

from uuid import uuid4

def _build_quiz_prompt(topic, num_questions, difficulty, language, user_level, mastery_level="Intermediate", context=None):
    # Adjust prompt based on Mastery Level
    audience_desc = f"Level {user_level} Student"
    focus_instruction = "Focus on standard application of concepts."
    
    if mastery_level == "Beginner":
        audience_desc = "Beginner Student (Zero Knowledge)"
        focus_instruction = "Focus on foundational concepts and 'Why' questions. Simplify everything."
    elif mastery_level == "Advanced" or mastery_level == "Exam":
        audience_desc = "Advanced Student (Competitive Exam/IIT-JEE Level)"
        focus_instruction = "Focus on complex application, edge cases, and multi-step reasoning."

    base_prompt = f"""
    Act as a friendly but serious teacher. Generate {num_questions} multiple-choice questions about "{topic}" in {language}.
    Target Audience: {audience_desc}.
    Difficulty: {difficulty}.
    Instruction: {focus_instruction}
    
    CRITICAL: Provide deep, step-by-step explanations for the correct answer.
    """
    
    if context:
        base_prompt += f"\n\nContext to use:\n{context}\n\n"
        
    base_prompt += """
    Return ONLY a raw JSON array.
    Structure:
    [
        {
            "prompt": "Question text",
            "choices": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "The text of the correct option",
            "explanation": "Deep, step-by-step explanation of why this is correct.",
            "wrong_explanations": { "Option X": "Why this is wrong" }
        }
    ]
    """
    return base_prompt

@router.post("/generate")
async def generate_quiz(
    req: TopicQuizRequest, 
    current_user: User = Depends(get_current_user)
):
    """Generate a quiz with adaptive difficulty based on user level."""
    if not ai_service.has_ai:
        raise HTTPException(status_code=400, detail="AI not configured")

    # Adaptive Logic
    difficulty = req.difficulty
    if current_user.level > 5 and difficulty == "easy":
        difficulty = "medium"
    
    prompt = _build_quiz_prompt(
        topic=req.topic,
        num_questions=req.num_questions,
        difficulty=difficulty,
        language=req.language,
        user_level=current_user.level,
        mastery_level=req.mastery_level,
        context=req.context
    )
    
    try:
        questions = await ai_service.generate_quiz(prompt)
        return {
            "questions": questions, 
            "adjusted_difficulty": difficulty,
            "user_level": current_user.level
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-from-file")
async def generate_quiz_from_file(
    file: UploadFile = File(...),
    num_questions: int = Form(5),
    difficulty: str = Form("medium"),
    language: str = Form("English"),
    mastery_level: str = Form("Intermediate"),
    current_user: User = Depends(get_current_user)
):
    """Generate quiz from uploaded file content."""
    if not ai_service.has_ai:
        raise HTTPException(status_code=400, detail="AI not configured")
    
    try:
        content = await file.read()
        text_content = extract_text_from_file(file.filename, content)
        
        # Limit text content to avoid token limits (approx 10k chars for safety)
        text_content = text_content[:15000]
        
        prompt = _build_quiz_prompt(
            topic=f"the uploaded document ({file.filename})",
            num_questions=num_questions,
            difficulty=difficulty,
            language=language,
            user_level=current_user.level,
            mastery_level=mastery_level,
            context=text_content
        )
        
        questions = await ai_service.generate_quiz(prompt)
        return {
            "questions": questions,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit")
async def submit_quiz(
    topic: str = Body(...),
    score: int = Body(...),
    total_questions: int = Body(...),
    difficulty: str = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit quiz results and generate share link."""
    
    accuracy = (score / total_questions) * 100 if total_questions > 0 else 0
    share_id = str(uuid4()) # Generate unique share ID
    
    result = QuizResult(
        topic=topic,
        score=score,
        total_questions=total_questions,
        difficulty=difficulty,
        accuracy=accuracy,
        share_id=share_id,
        owner_id=current_user.id
    )
    db.add(result)
    db.commit()
    
    return {
        "message": "Quiz submitted successfully",
        "score": score,
        "total": total_questions,
        "accuracy": accuracy,
        "share_id": share_id,
        "share_link": f"/share/{share_id}" 
    }

@router.get("/share/{share_id}")
def get_shared_result(share_id: str, db: Session = Depends(get_db)):
    """Get a shared quiz result (Public Access)."""
    result = db.query(QuizResult).filter(QuizResult.share_id == share_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Quiz result not found")
        
    return {
        "topic": result.topic,
        "score": result.score,
        "total_questions": result.total_questions,
        "accuracy": result.accuracy,
        "difficulty": result.difficulty,
        "owner_name": result.owner.username if result.owner else "Anonymous"
    }
