from pydantic import BaseModel, Field
from typing import Optional, Dict

class PresentationRequest(BaseModel):
    topic: str
    num_slides: int = Field(8, ge=5, le=20)
    language: str = "English"
    theme: str = "Modern" # Minimal, Professional, Creative, Dark, Gradient
    font_style: str = "Modern" # Poppins, Inter, Roboto, Open Sans, Montserrat, Playfair
    color_palette: str = "Vibrant" # Pastel, Vibrant, Corporate
    tone: str = "Professional" # Professional, Fun, Academic
    format: str = "pptx" # pptx, pdf, docx

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

class GoogleAuthRequest(BaseModel):
    """Request model for Google Sign-In"""
    id_token: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[Dict] = None  # Include user info in token response

class UserDisplay(UserBase):
    id: int
    xp: int
    level: int
    streak_count: int
    full_name: Optional[str] = None
    profile_photo: Optional[str] = None
    
    class Config:
        from_attributes = True
