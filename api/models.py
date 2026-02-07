from pydantic import BaseModel, Field
from typing import Optional

class TopicQuizRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    difficulty: str = "medium"
    language: str = "English"
    num_questions: int = Field(5, ge=1, le=10)
    context: Optional[str] = None

class TeacherHelpRequest(BaseModel):
    task: str
    topic: str
    details: Optional[str] = ""

class AIHelpRequest(BaseModel):
    question: str
    style: str = "simple"
