
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os
import json
from fastapi.middleware.cors import CORSMiddleware

# --- Configuration ---
# In a real deployed app, this comes from ENV. 
# For this local session, we'll try to read from env or fallback to the key we know works.
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCzGL07JLc003wfbDLmnarcQb-FGMZRn0s")

# --- Gemini Initialization ---
try:
    genai.configure(api_key=API_KEY)
    # Dynamic discovery of models
    available_models = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Priority order
    preferred_models = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-pro']
    selected_model_name = None
    
    for pm in preferred_models:
        if pm in available_models:
            selected_model_name = pm
            break
            
    if not selected_model_name and available_models:
        selected_model_name = available_models[0]
        
    if selected_model_name:
        model = genai.GenerativeModel(selected_model_name)
        print(f"✅ Gemini initialized with model: {selected_model_name}")
    else:
        print("CRITICAL: No AI models available for this API key.")
        model = None
except Exception as e:
    print(f"Gemini Init Error: {e}")
    model = None

app = FastAPI()

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class QuizRequest(BaseModel):
    topic: str
    difficulty: str = "medium"
    content_text: str = "" # Optional context from files

class DoubtRequest(BaseModel):
    question: str
    context: str = "" # Optional previous chat context

class ExplainRequest(BaseModel):
    question_text: str
    correct_answer: str
    user_answer: str

# --- Routes ---

@app.get("/health")
def health_check():
    return {"status": "online", "model": "gemini-1.5-flash"}

@app.post("/generate-quiz")
async def generate_quiz(req: QuizRequest):
    try:
        if req.content_text:
            prompt = f"""
            Generate a {req.difficulty} level quiz based on this text:
            "{req.content_text[:2000]}..."
            
            Create 5 multiple-choice questions.
            Return ONLY valid JSON in this format:
            [
                {{
                    "prompt": "Question text",
                    "choices": ["Option A", "Option B", "Option C", "Option D"],
                    "answer": "Option A",
                    "explanation": "Detailed reasoning for correct answer",
                    "wrong_explanations": {{
                        "Option B": "Why B is wrong",
                        "Option C": "Why C is wrong",
                        "Option D": "Why D is wrong"
                    }}
                }}
            ]
            """
        else:
            prompt = f"""
            Generate a {req.difficulty} level quiz about "{req.topic}".
            Create 5 conceptual, exam-oriented multiple-choice questions.
            Return ONLY valid JSON in this format:
            [
                {{
                    "prompt": "Question text",
                    "choices": ["Option A", "Option B", "Option C", "Option D"],
                    "answer": "Option A",
                    "explanation": "Detailed reasoning for correct answer",
                    "wrong_explanations": {{
                        "Option B": "Why B is wrong",
                        "Option C": "Why C is wrong",
                        "Option D": "Why D is wrong"
                    }}
                }}
            ]
            """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean markdown
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text)
        
    except Exception as e:
        print(f"Error generating quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask-doubt")
async def ask_doubt(req: DoubtRequest):
    try:
        prompt = f"""
        You are a helpful AI Tutor.
        User asks: "{req.question}"
        
        Answer clearly and concisely. Use emojis where appropriate.
        """
        response = model.generate_content(prompt)
        return {"answer": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain-answer")
async def explain_answer(req: ExplainRequest):
    try:
        prompt = f"""
        Question: "{req.question_text}"
        Correct Answer: "{req.correct_answer}"
        User Selected: "{req.user_answer}"
        
        Explain why the correct answer is right and why the user's answer (if different) is wrong.
        Keep it short and educational.
        """
        response = model.generate_content(prompt)
        return {"explanation": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
