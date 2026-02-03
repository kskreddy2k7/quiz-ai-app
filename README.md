# QuizAI Academy 🎯

QuizAI Academy is a production-ready AI education platform that turns study material into interactive MCQs and provides an AI-powered doubt solver. It ships with a scalable FastAPI backend, a modern responsive frontend, and AI-ready infrastructure for real-world deployment.

## ✨ Features

- **MCQ generation from text, PDF, PPT, and DOC files**
- **AI-powered Doubt Solver** with chat-style UX
- **Step-by-step explanations** for correct answers
- **Clear reasons why incorrect options are wrong**
- **Difficulty levels** (easy, medium, hard)
- **Responsive UI** with smooth animations, loading screen, and friendly tone
- **Production-ready backend** with validation, logging, security headers, and configuration support

## 🧱 Tech Stack

- **Backend:** FastAPI, Pydantic, Uvicorn
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **AI Provider:** OpenAI (optional) + smart fallback generator
- **Docs & Deploy:** Docker-ready structure with `.env` support

## ✅ Local Setup

### 1. Clone & install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Set your `OPENAI_API_KEY` and update `AI_PROVIDER=openai` to enable AI-powered generation.

### 3. Run the app

```bash
uvicorn app.main:app --reload --app-dir backend
```

Open [http://localhost:8000](http://localhost:8000).

## 🧪 API Endpoints

- `POST /api/quiz/generate` – Generate MCQs from text or uploaded file
- `POST /api/chat` – Chat with the AI tutor
- `GET /api/health` – Health check

## 🚀 Deployment

- Use a simple Dockerfile or cloud runtime of choice (Render, Fly.io, AWS App Runner).
- Configure environment variables for OpenAI or connect to an internal LLM endpoint.

## 🗺️ Future Roadmap

- User accounts & progress tracking
- Adaptive learning paths and personalization
- Rich analytics dashboards for educators
- Multi-language content generation
- Mobile app packaging (Play Store ready)

---

Built with ❤️ for students and lifelong learners.
