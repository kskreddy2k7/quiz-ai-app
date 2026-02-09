import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from api import auth
from utils.helpers import get_random_quote
from services.ai_service import ai_service
from utils.limiter import limiter
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from database import engine
from models import user_models

# Create Database Tables
user_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="S Quiz AI Academy - PRO")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    await ai_service.close()

@app.get("/manifest.json")
async def manifest():
    return FileResponse("manifest.json")

@app.get("/sw.js")
async def service_worker():
    return FileResponse("sw.js")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serves static files (CSS, JS, Images)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Templates
templates = Jinja2Templates(directory="static")

@app.get("/")
async def home(request: Request):
    quote = get_random_quote()
    # Always show positive status - we have offline fallbacks
    status_text = "✅ Free & Open AI - Unlimited Learning Power!"
        
    return templates.TemplateResponse("index.html", {
        "request": request,
        "has_ai": True,  # Always true - we have offline mode
        "status_text": status_text,
        "quote": quote
    })

from api import users
app.include_router(users.router)
from api import quiz
app.include_router(quiz.router)
from api import chat
app.include_router(chat.router)
from api import library
app.include_router(library.router)
from api import presentation
app.include_router(presentation.router)
app.include_router(auth.router)
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main_web:app", host="0.0.0.0", port=port, reload=True)
