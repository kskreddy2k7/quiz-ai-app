from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
import logging

from database import get_db
from models.user_models import User
from api.models import UserCreate, Token, UserDisplay, UserLogin, GoogleAuthRequest
from services.auth_service import auth_service, ACCESS_TOKEN_EXPIRE_MINUTES
from services.google_auth_service import google_auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

@router.post("/register", response_model=UserDisplay)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth_service.get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not user.hashed_password or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "profile_photo": user.profile_photo
        }
    }

@router.post("/google", response_model=Token)
def google_login(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Google Sign-In endpoint
    Verifies Google ID token and creates/logs in user
    """
    # Verify Google token
    user_info = google_auth_service.verify_token(request.id_token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    
    # Check if user exists by Google ID
    user = db.query(User).filter(User.google_id == user_info["google_id"]).first()
    
    if not user:
        # Check if user exists by email
        user = db.query(User).filter(User.email == user_info["email"]).first()
        
        if user:
            # Link Google account to existing user
            user.google_id = user_info["google_id"]
            user.profile_photo = user_info.get("picture")
            user.full_name = user_info.get("name")
        else:
            # Create new user from Google account
            username = user_info["email"].split("@")[0]
            
            # Ensure unique username
            base_username = username
            counter = 1
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User(
                username=username,
                email=user_info["email"],
                google_id=user_info["google_id"],
                full_name=user_info.get("name"),
                profile_photo=user_info.get("picture"),
                hashed_password=None  # No password for OAuth users
            )
            db.add(user)
        
        db.commit()
        db.refresh(user)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    logger.info(f"Google login successful for user: {user.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "profile_photo": user.profile_photo
        }
    }

@router.get("/google/config")
def get_google_config():
    """
    Get Google OAuth configuration for frontend
    Returns the client ID needed for Google Sign-In button
    """
    import os
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        raise HTTPException(
            status_code=503,
            detail="Google OAuth not configured"
        )
    return {"client_id": client_id}

# Dependency to get current user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Guest Mode Support
    if token == "guest_token_placeholder":
        return User(id=9999, username="Guest", email="guest@quizai.com", level=1)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = auth_service.decode_token(token)
    if username is None:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
