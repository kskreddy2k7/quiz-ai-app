from pydantic import BaseModel, Field


class QuizGenerateRequest(BaseModel):
    text: str | None = Field(None, description="Raw text prompt to generate questions from.")
    num_questions: int = Field(5, ge=1, le=20)
    difficulty: str = Field("easy", pattern="^(easy|medium|hard)$")
    subject: str | None = Field(None, description="Optional subject focus for the quiz.")


class IncorrectExplanation(BaseModel):
    option: str
    reason: str


class QuizItem(BaseModel):
    question: str
    options: list[str]
    answer: str
    explanation: str
    incorrect_explanations: list[IncorrectExplanation]


class QuizGenerateResponse(BaseModel):
    topic: str
    difficulty: str
    questions: list[QuizItem]


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2)
    subject: str = Field("General", description="Subject category for the doubt.")
    context: str | None = None


class ChatResponse(BaseModel):
    response: str
    tips: list[str] = []


class FileUploadResponse(BaseModel):
    filename: str
    extracted_text: str
    summary: str
