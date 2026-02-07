from pydantic import BaseModel, Field
from typing import Optional

class TopicQuizRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    difficulty: str = "medium"
    language: str = "English"
    num_questions: int = Field(5, ge=1, le=10)
    mastery_level: str = "Intermediate" # Beginner, Intermediate, Advanced, Exam
    context: Optional[str] = None

class TeacherHelpRequest(BaseModel):
    task: str
    topic: str
    details: Optional[str] = ""

class AIHelpRequest(BaseModel):
    question: str
    style: str = "simple"

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserDisplay(UserBase):
    id: int
    xp: int
    level: int
    streak_count: int
    
    class Config:
        from_attributes = True
