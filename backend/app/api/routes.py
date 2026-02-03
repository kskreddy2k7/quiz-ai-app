from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import get_settings
from app.core.logging import logger
from app.schemas import ChatRequest, ChatResponse, QuizGenerateResponse
from app.services.doubt_service import DoubtService
from app.services.file_service import read_upload
from app.services.quiz_service import QuizService
from app.utils.text import normalize_text, summarize_topic

router = APIRouter()
settings = get_settings()
quiz_service = QuizService()
doubt_service = DoubtService()


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": settings.app_name}


@router.post("/quiz/generate", response_model=QuizGenerateResponse)
def generate_quiz(
    text: str | None = Form(None),
    num_questions: int = Form(5),
    difficulty: str = Form("easy"),
    file: UploadFile | None = File(None),
) -> QuizGenerateResponse:
    if not text and not file:
        raise HTTPException(status_code=400, detail="Provide text or upload a file.")

    content = text or ""
    if file:
        content = read_upload(file)
        logger.info("File uploaded for quiz generation: %s", file.filename)

    normalized = normalize_text(content)
    if not normalized:
        raise HTTPException(status_code=400, detail="Uploaded content is empty.")

    difficulty = difficulty.lower()
    if difficulty not in {"easy", "medium", "hard"}:
        raise HTTPException(status_code=400, detail="Difficulty must be easy, medium, or hard.")

    questions = quiz_service.generate(normalized, num_questions, difficulty)
    if not questions:
        raise HTTPException(status_code=400, detail="Unable to generate questions from content.")

    return QuizGenerateResponse(
        topic=summarize_topic(normalized) or "Your Study Material",
        difficulty=difficulty,
        questions=questions,
    )


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    logger.info("Chat request received.")
    response, tips = doubt_service.respond(request.message, request.context)
    return ChatResponse(response=response, tips=tips)
