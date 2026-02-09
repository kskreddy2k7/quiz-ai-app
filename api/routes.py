import os
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from .models import TopicQuizRequest, TeacherHelpRequest, AIHelpRequest
from services.ai_service import ai_service
from services.file_service import file_service
from utils.helpers import get_random_quote

from utils.limiter import limiter

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "ai_status": ai_service.status,
        "provider": ai_service.provider
    }

@router.post("/generate_topic")
@limiter.limit("5/minute")
async def generate_topic(req: TopicQuizRequest, request: Request):
    if not ai_service.has_ai:
        raise HTTPException(status_code=400, detail="AI not configured")
    
    prompt = f"""
    Generate {req.num_questions} {req.question_type} questions about "{req.topic}" in {req.language}.
    Difficulty: {req.difficulty}.
    
    IMPORTANT: The output must be valid JSON only. Ensure the questions are in {req.language}.
    
    Return ONLY a JSON array of objects with this structure:
    [
        {{
            "type": "single", // OR "multi"
            "prompt": "Question text...",
            "choices": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Option A", // IF type is "single": Exact string match
            "correct_answers": ["Option A", "Option C"], // IF type is "multi": List of correct strings
            "explanation": "Explanation...",
            "wrong_explanations": {{"Option B": "Why wrong..."}}
        }}
    ]
    
    RULES:
    - If {req.question_type} is "Multiple Choice", generate 70% "single" and 30% "multi" type questions.
    - If {req.question_type} is "Mixed", generate 50% "single" and 50% "multi".
    - For "multi" type, ensure there are at least 2 correct options.
    """
    
    try:
        questions = await ai_service.generate_quiz(prompt)
        return {"questions": questions}
    except Exception as e:
        print(f"Error in generate_topic: {e}") # Debug log
        # Fallback to offline quiz
        offline_questions = ai_service.generate_offline_quiz(req.topic, req.num_questions, req.difficulty)
        return {"questions": offline_questions}

@router.post("/generate_file")
@limiter.limit("3/minute")
async def generate_file(
    request: Request,
    file: UploadFile = File(...),
    difficulty: str = Form("medium"),
    num_questions: int = Form(5)
):
    if not ai_service.has_ai:
        raise HTTPException(status_code=400, detail="AI not configured")
    
    # Limit question count
    num_questions = min(max(num_questions, 1), 10)
    
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        text = await file_service.extract_text(filepath)
        if text.startswith("Error"):
             raise HTTPException(status_code=400, detail=text)
             
        prompt = f"""
        Based on the following text, generate {num_questions} multiple-choice questions.
        Difficulty: {difficulty}
        
        Text excerpt: {text[:5000]}
        
        Return ONLY a valid JSON array as defined for quizzes.
        """
        
        questions = await ai_service.generate_quiz(prompt)
        return {
            "questions": questions,
            "filename": file.filename,
            "text_length": len(text)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@router.post("/teacher_help")
@limiter.limit("5/minute")
async def teacher_help(req: TeacherHelpRequest, request: Request):
    if not ai_service.has_ai:
         raise HTTPException(status_code=400, detail="AI not configured")
    
    prompt = f"Task: {req.task}. Topic: {req.topic}. Details: {req.details}"
    try:
        response = await ai_service.generate_text(prompt)
        return {"response": response}
    except Exception as e:
        print(f"Error in teacher_help: {e}") # Debug log
        # Fallback to offline notes
        fallback_notes = ai_service.generate_offline_notes(req.topic)
        return {"response": fallback_notes}

@router.post("/ai_help")
@limiter.limit("5/minute")
async def ai_help(req: AIHelpRequest, request: Request):
    if not ai_service.has_ai:
         raise HTTPException(status_code=400, detail="AI not configured")
    
    prompt = f"Style: {req.style}. Question: {req.question}"
    try:
        response = await ai_service.generate_text(prompt)
        return {"response": response}
    except Exception as e:
        print(f"Error in ai_help: {e}")
        return {"response": "🤖 **AI Tutor Offline**: I'm having trouble connecting to the brain right now. Please check your internet or try again later."}
