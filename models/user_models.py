from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)  # Nullable for Google OAuth users
    is_active = Column(Boolean, default=True)
    
    # Google OAuth fields
    google_id = Column(String, unique=True, nullable=True, index=True)
    profile_photo = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    
    # Gamification Stats
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak_count = Column(Integer, default=0)
    last_active_date = Column(DateTime, default=None)
    created_at = Column(DateTime, default=datetime.utcnow)

    quiz_results = relationship("QuizResult", back_populates="owner")
    library_items = relationship("LibraryItem", back_populates="owner")
    progress = relationship("LearningProgress", back_populates="owner")

class QuizResult(Base):
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, index=True)
    share_id = Column(String, unique=True, index=True, nullable=True) # For public sharing
    topic = Column(String, index=True)
    score = Column(Integer)
    total_questions = Column(Integer)
    difficulty = Column(String)
    accuracy = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="quiz_results")

class LibraryItem(Base):
    __tablename__ = "library_items"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    content = Column(String) # Extracted text
    summary = Column(String, nullable=True) # AI Summary
    file_type = Column(String) # pdf, docx, txt
    upload_date = Column(DateTime, default=datetime.utcnow)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="library_items")

class LearningProgress(Base):
    __tablename__ = "learning_progress"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    mastery_level = Column(String, default="Beginner") # Beginner, Intermediate, Advanced
    last_practiced = Column(DateTime, default=datetime.utcnow)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="progress")
