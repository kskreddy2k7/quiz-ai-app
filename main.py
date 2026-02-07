import os
from dotenv import load_dotenv

# Load environment variables FIRST before other imports read them
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from utils.helpers import get_random_quote
from services.ai_service import ai_service
from utils.limiter import limiter
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

app = FastAPI(title="S Quiz AI Academy - PRO")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

# Templates
templates = Jinja2Templates(directory="static")

@app.get("/")
async def home(request: Request):
    quote = get_random_quote()
    status_text = ai_service.status
    if ai_service.has_ai:
        status_text = f"✅ AI Online ({ai_service.provider}) - Unlimited Learning Power!"
    else:
        status_text = "❌ AI Offline - Please check API keys"
        
    return templates.TemplateResponse("index.html", {
        "request": request,
        "has_ai": ai_service.has_ai,
        "status_text": status_text,
        "quote": quote
    })

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
