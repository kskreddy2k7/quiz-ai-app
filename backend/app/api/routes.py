from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import get_settings
from app.core.logging import logger
from app.schemas import ChatResponse, FileUploadResponse, QuizGenerateResponse
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


@router.post("/generate_quiz", response_model=QuizGenerateResponse)
def generate_quiz(
    text: str | None = Form(None),
    num_questions: int = Form(5),
    difficulty: str = Form("easy"),
    subject: str = Form("General"),
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

    questions = quiz_service.generate(normalized, num_questions, difficulty, subject)
    if not questions:
        raise HTTPException(status_code=400, detail="Unable to generate questions from content.")

    topic = summarize_topic(normalized) or f"{subject} Study Material"

    return QuizGenerateResponse(
        topic=topic,
        difficulty=difficulty,
        questions=questions,
    )


@router.post("/ask_doubt", response_model=ChatResponse)
def ask_doubt(
    message: str | None = Form(None),
    subject: str = Form("General"),
    context: str | None = Form(None),
    file: UploadFile | None = File(None),
) -> ChatResponse:
    if not message and not file:
        raise HTTPException(status_code=400, detail="Provide a question or upload a file.")

    extracted = ""
    if file:
        extracted = read_upload(file)
        logger.info("File uploaded for doubt solving: %s", file.filename)

    combined_context = " ".join(filter(None, [context, extracted]))
    prompt_message = message or "Please explain the key ideas from the uploaded content."

    response, tips = doubt_service.respond(prompt_message, subject, combined_context)
    return ChatResponse(response=response, tips=tips)


@router.post("/upload_file", response_model=FileUploadResponse)
def upload_file(file: UploadFile = File(...)) -> FileUploadResponse:
    extracted = read_upload(file)
    normalized = normalize_text(extracted)
    summary = summarize_topic(normalized, max_length=160) if normalized else ""
    return FileUploadResponse(
        filename=file.filename or "uploaded",
        extracted_text=normalized,
        summary=summary,
    )
