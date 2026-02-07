"""
Quiz AI Academy - PREMIUM VERSION
Features:
- Custom question count (1-100)
- Premium UI with gradients and animations
- Motivational quotes
- Enhanced emojis throughout
- Beautiful design
"""

from flask import Flask, render_template_string, request, jsonify, send_from_directory
import json
import os
import random
import traceback
import time
from werkzeug.utils import secure_filename
import secrets as secret_module

# Load API keys for multiple providers
CLOUDFLARE_API_KEY = os.environ.get('CLOUDFLARE_API_KEY') or ''
CLOUDFLARE_ACCOUNT_ID = os.environ.get('CLOUDFLARE_ACCOUNT_ID') or ''
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GEMINIAPIKEY') or ''

# Try loading from secrets.json if environment variables not set
if not CLOUDFLARE_API_KEY or not GEMINI_API_KEY:
    try:
        with open('secrets.json', 'r') as f:
            secrets = json.load(f)
            if not CLOUDFLARE_API_KEY:
                CLOUDFLARE_API_KEY = secrets.get('CLOUDFLARE_API_KEY', '')
            if not CLOUDFLARE_ACCOUNT_ID:
                CLOUDFLARE_ACCOUNT_ID = secrets.get('CLOUDFLARE_ACCOUNT_ID', '')
            if not GEMINI_API_KEY:
                GEMINI_API_KEY = secrets.get('GEMINI_API_KEY', '')
    except:
        pass



# Initialize AI Providers
HAS_AI = False
AI_PROVIDER = "None"
AI_STATUS = "Offline"
AI_DEBUG = ""
model = None  # For Gemini fallback
fallback_models = []

# Try Cloudflare Workers AI first (10,000 free requests/day!)
if CLOUDFLARE_API_KEY and CLOUDFLARE_ACCOUNT_ID:
    try:
        # Test Cloudflare API connection
        test_url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/models"
        test_headers = {"Authorization": f"Bearer {CLOUDFLARE_API_KEY}"}
        
        import requests
        test_response = requests.get(test_url, headers=test_headers, timeout=5)
        
        if test_response.status_code == 200:
            HAS_AI = True
            AI_PROVIDER = "Cloudflare"
            AI_STATUS = "Online (Cloudflare Workers AI)"
            print(f"✅ Cloudflare Workers AI initialized successfully!")
        else:
            AI_STATUS = f"Cloudflare Error: HTTP {test_response.status_code}"
            print(f"⚠️ Cloudflare API test failed: {test_response.status_code}")
    except Exception as e:
        AI_STATUS = f"Cloudflare Error: {str(e)[:50]}..."
        AI_DEBUG = str(e)
        print(f"⚠️ Cloudflare initialization failed: {e}")

# Fallback to Gemini if Cloudflare not available
if not HAS_AI and GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Dynamic discovery of models
        available_models = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority order for models
        preferred_models = [
            'gemini-2.5-flash', 
            'gemini-2.0-flash', 
            'gemini-1.5-flash', 
            'gemini-flash-latest', 
            'gemini-1.5-flash-latest', 
            'gemini-1.5-pro', 
            'gemini-pro-latest'
        ]
        
        # Find best available models
        fallback_models = []
        for pm in preferred_models:
            if pm in available_models:
                fallback_models.append(pm)
        
        if not fallback_models and available_models:
             fallback_models = available_models[:3]

        if fallback_models:
            selected_model_name = fallback_models[0]
            model = genai.GenerativeModel(selected_model_name)
            HAS_AI = True
            AI_PROVIDER = "Gemini"
            AI_STATUS = "Online (Gemini - Fallback)"
            print(f"✅ Gemini AI initialized. Primary: {selected_model_name}. Backups: {fallback_models[1:]}")
        else:
            AI_STATUS = "Offline (No available models found)"

    except Exception as e:
        AI_STATUS = f"Offline (Error: {str(e)[:50]}...)"
        AI_DEBUG = str(e)
        print(f"⚠️ Gemini initialization failed: {e}")
else:
    if not HAS_AI:
        AI_STATUS = "Offline (No API Key found)"

def generate_with_cloudflare(prompt):
    """Generate content using Cloudflare Workers AI"""
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/meta/llama-3.3-70b-instruct-fp8-fast"
    
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4096
    }
    
    import requests
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        print(f"DEBUG: Cloudflare response: {result}")  # Debug logging
        
        # Cloudflare Workers AI returns: {"result": {"response": "text"}} or {"success": true, "result": {"response": "text"}}
        if 'result' in result:
            # Handle different response formats
            if isinstance(result['result'], dict):
                if 'response' in result['result']:
                    return result['result']['response']
                elif 'text' in result['result']:
                    return result['result']['text']
                elif 'content' in result['result']:
                    return result['result']['content']
            elif isinstance(result['result'], str):
                return result['result']
        
        # If we get here, the format is unexpected
        raise Exception(f"Unexpected Cloudflare response format: {result}")
    else:
        raise Exception(f"Cloudflare API error: HTTP {response.status_code} - {response.text}")

def generate_with_fallback(prompt):
    """Attempts to generate content using Cloudflare first, then Gemini fallback"""
    global model, AI_PROVIDER
    
    # Try Cloudflare first
    if AI_PROVIDER == "Cloudflare" or (CLOUDFLARE_API_KEY and CLOUDFLARE_ACCOUNT_ID):
        try:
            print(f"🚀 Using Cloudflare Workers AI...")
            response_text = generate_with_cloudflare(prompt)
            
            # Create a response object similar to Gemini's format
            class CloudflareResponse:
                def __init__(self, text):
                    self.text = text
            
            return CloudflareResponse(response_text)
            
        except Exception as e:
            error_str = str(e)
            print(f"⚠️ Cloudflare failed: {error_str[:100]}")
            
            # If Cloudflare fails, try Gemini fallback
            if GEMINI_API_KEY and model is not None:
                print(f"🔄 Falling back to Gemini...")
                AI_PROVIDER = "Gemini"
            else:
                raise Exception(f"Cloudflare AI error: {error_str}")
    
    # Try Gemini (either as primary or fallback)
    if AI_PROVIDER == "Gemini" or model is not None:
        try:
            if model is None:
                 raise Exception("AI Model is not initialized")
                 
            return model.generate_content(prompt)
            
        except Exception as e:
            error_str = str(e)
            # Check for 429 Resource Exhausted
            if "429" in error_str or "quota" in error_str.lower():
                print(f"⚠️ Quota hit on {getattr(model, 'model_name', 'current model')}. Trying fallbacks...")
                
                # Ensure we have a list of fallbacks
                candidates = []
                if fallback_models:
                    candidates.extend(fallback_models)
                
                # Always add these standard reliable models if not already present
                standard_backups = ['gemini-2.0-flash-exp', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-1.0-pro']
                for backup in standard_backups:
                    if backup not in candidates:
                        candidates.append(backup)
                
                for model_name in candidates:
                    # Strip 'models/' prefix for comparison
                    current_model = getattr(model, 'model_name', '')
                    if current_model:
                         current_model = current_model.replace('models/', '')
                         
                    if current_model == model_name:
                        continue
                        
                    print(f"🔄 Switching to fallback model: {model_name}")
                    time.sleep(2)
                    try:
                        import google.generativeai as genai
                        fallback_model = genai.GenerativeModel(model_name)
                        response = fallback_model.generate_content(prompt)
                        
                        print(f"✅ Fallback successful. Switching primary model to {model_name}")
                        model = fallback_model 
                        return response
                    except Exception as fallback_error:
                        error_msg = f"❌ Fallback {model_name} failed: {fallback_error}"
                        print(error_msg)
                        try:
                            with open('debug_error.log', 'a') as f:
                                 f.write(f"{error_msg}\n")
                        except:
                            pass
                        continue
                
                # If all fail
                raise Exception("All AI models busy or quota exceeded. Please wait 1 minute.")
            
            # If not a 429 error, re-raise original
            raise e
    
    # If no provider available
    raise Exception("No AI provider available. Please configure CLOUDFLARE_API_KEY or GEMINI_API_KEY.")


app = Flask(__name__)
app.secret_key = secret_module.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs('uploads', exist_ok=True)

# Motivational Quotes
QUOTES = [
    {"text": "Education is the most powerful weapon which you can use to change the world.", "author": "Nelson Mandela"},
    {"text": "The beautiful thing about learning is that no one can take it away from you.", "author": "B.B. King"},
    {"text": "Learning is not attained by chance, it must be sought for with ardor.", "author": "Abigail Adams"},
    {"text": "The expert in anything was once a beginner.", "author": "Helen Hayes"},
    {"text": "Success is the sum of small efforts repeated day in and day out.", "author": "Robert Collier"},
    {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
    {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"text": "Don't watch the clock; do what it does. Keep going.", "author": "Sam Levenson"},
    {"text": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
    {"text": "Education is not preparation for life; education is life itself.", "author": "John Dewey"}
]

def get_random_quote():
    quote = random.choice(QUOTES)
    return quote

def extract_text_from_file(filepath):
    ext = filepath.lower().split('.')[-1]
    
    try:
        if ext == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == 'pdf':
            try:
                import pypdf
                with open(filepath, 'rb') as f:
                    pdf = pypdf.PdfReader(f)
                    text = ''
                    for page in pdf.pages:
                        text += page.extract_text() + '\n'
                    return text
            except ImportError:
                return "Error: pypdf not installed"
        elif ext in ['docx', 'doc']:
            try:
                import docx2txt
                return docx2txt.process(filepath)
            except ImportError:
                return "Error: docx2txt not installed"
        else:
            return f"Unsupported file type: {ext}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

# Premium HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Quiz AI Academy - Premium</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="manifest" href="/manifest.json">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script>
        // CRITICAL: Define switchTab in head so it's ready immediately
        function switchTab(tab) {
            console.log("Tab click:", tab);
            try {
                const contents = document.querySelectorAll('.tab-content');
                const tabs = document.querySelectorAll('.tab');
                
                for (let i = 0; i < contents.length; i++) {
                    contents[i].style.display = 'none';
                    contents[i].classList.remove('active');
                }
                for (let i = 0; i < tabs.length; i++) {
                    tabs[i].classList.remove('active');
                }
                
                const targetContent = document.getElementById(tab + '-content');
                const targetTab = document.getElementById('tab-' + tab);
                
                if (targetContent) {
                    targetContent.style.display = 'block';
                    setTimeout(() => targetContent.classList.add('active'), 10);
                }
                if (targetTab) targetTab.classList.add('active');
            } catch (e) {
                console.error("Tab error:", e);
            }
        }
    </script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 30px;
            animation: fadeInDown 0.8s ease;
        }
        
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            margin-bottom: 15px;
        }
        
        .logo {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            font-weight: 900;
            color: white;
            box-shadow: 0 10px 40px rgba(102,126,234,0.5);
            animation: logoFloat 3s ease-in-out infinite;
        }
        
        @keyframes logoFloat {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        h1 {
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #fff 0%, #f0f0f0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            text-shadow: 0 0 30px rgba(255,255,255,0.3);
            letter-spacing: 2px;
        }
        
        .subtitle {
            font-size: 1.3rem;
            color: rgba(255,255,255,0.9);
            font-weight: 300;
        }
        
        .creator-badge {
            display: inline-block;
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            padding: 8px 20px;
            border-radius: 50px;
            font-size: 0.9rem;
            margin-top: 10px;
            border: 1px solid rgba(255,255,255,0.3);
        }
        
        .quote-box {
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            animation: fadeIn 1s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .quote-text {
            font-size: 1.2rem;
            font-style: italic;
            margin-bottom: 10px;
            color: #fff;
        }
        
        .quote-author {
            text-align: right;
            color: rgba(255,255,255,0.8);
            font-weight: 600;
        }
        
        .status {
            text-align: center;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            font-weight: 600;
            font-size: 1.1rem;
            animation: pulse 2s ease infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }
        
        .status.online {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            box-shadow: 0 10px 40px rgba(56,239,125,0.3);
        }
        
        .status.offline {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            box-shadow: 0 10px 40px rgba(235,51,73,0.3);
        }
        
        .tabs {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
            position: relative;
            z-index: 10000;
            pointer-events: auto !important;
        }
        
        .tab {
            padding: 15px 30px;
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 50px;
            cursor: pointer !important;
            transition: all 0.3s ease;
            color: #fff;
            font-weight: 600;
            font-size: 1.05rem;
            position: relative;
            z-index: 10001;
            pointer-events: auto !important;
            user-select: none;
        }
        
        .tab.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-color: #fff;
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(102,126,234,0.4);
        }
        
        .tab:hover:not(.active) {
            background: rgba(255,255,255,0.2);
            transform: translateY(-3px);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
            animation: fadeInUp 0.5s ease;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .card {
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            padding: 40px;
            margin-bottom: 25px;
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            font-size: 2rem;
            margin-bottom: 25px;
            background: linear-gradient(135deg, #fff 0%, #f0f0f0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 10px;
            color: #fff;
            font-weight: 600;
            font-size: 1.05rem;
        }
        
        input, select, textarea {
            width: 100%;
            padding: 15px;
            border-radius: 15px;
            border: 2px solid rgba(255,255,255,0.3);
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            color: #fff;
            font-size: 1rem;
            font-family: 'Poppins', sans-serif;
            transition: all 0.3s ease;
        }
        
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #fff;
            background: rgba(255,255,255,0.2);
            box-shadow: 0 0 20px rgba(255,255,255,0.3);
        }
        
        input::placeholder, textarea::placeholder {
            color: rgba(255,255,255,0.6);
        }
        
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 18px 40px;
            border-radius: 50px;
            cursor: pointer;
            font-size: 1.2rem;
            font-weight: 700;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(102,126,234,0.4);
            font-family: 'Poppins', sans-serif;
        }
        
        button:hover:not(:disabled) {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(102,126,234,0.6);
        }
        
        button:active:not(:disabled) {
            transform: translateY(-1px);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .question-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 25px;
            transition: all 0.3s ease;
        }
        
        .question-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }
        
        .question-text {
            font-size: 1.3rem;
            margin-bottom: 20px;
            font-weight: 600;
            color: #fff;
        }
        
        .option {
            background: rgba(255,255,255,0.1);
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: #fff;
        }
        
        .option:hover {
            background: rgba(255,255,255,0.2);
            border-color: #fff;
            transform: translateX(5px);
        }
        
        .option.correct {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            border-color: #38ef7d;
        }
        
        .option.wrong {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            border-color: #f45c43;
        }
        
        .option.selected {
            background: rgba(255,255,255,0.3);
            border-color: #fff;
            transform: translateX(10px);
            box-shadow: 0 0 20px rgba(255,255,255,0.2);
        }
        
        .hidden {
            display: none !important;
        }
        
        .score-summary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 30px;
            animation: bounce 0.8s ease;
        }
        
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
            40% {transform: translateY(-20px);}
            60% {transform: translateY(-10px);}
        }
        
        .explanation {
            background: rgba(56,239,125,0.2);
            border: 2px solid #38ef7d;
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
        }
        
        .explanation-title {
            font-weight: 700;
            color: #38ef7d;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }
        
        .wrong-explanation {
            background: rgba(235,51,73,0.2);
            border: 2px solid #eb3349;
            border-radius: 12px;
            padding: 15px;
            margin-top: 12px;
            color: #ffcccb;
        }
        
        .loading {
            text-align: center;
            padding: 30px;
            font-size: 1.2rem;
            color: #fff;
        }
        
        .spinner {
            border: 4px solid rgba(255,255,255,0.3);
            border-top: 4px solid #fff;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            padding: 20px;
            border-radius: 15px;
            margin-top: 20px;
            box-shadow: 0 10px 30px rgba(235,51,73,0.3);
        }
        
        .file-info {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            margin-top: 20px;
            box-shadow: 0 10px 30px rgba(102,126,234,0.3);
        }
        
        
        
        .share-btn {
            background: linear-gradient(135deg, #00B4DB 0%, #0083B0 100%);
            border: none;
            padding: 8px 15px;
            border-radius: 10px;
            color: white;
            cursor: pointer;
            font-size: 0.9rem;
            margin-left: 10px;
            transition: all 0.3s ease;
        }

        .share-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,180,219,0.4);
        }

        .btn-group {
            display: flex;
            gap: 10px;
        }

        @media (max-width: 768px) {
            h1 { font-size: 2.5rem; }
            .grid-2 { grid-template-columns: 1fr; }
            .tabs { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo-container">
                <div class="logo">
                    <img src="/static/logo.png" alt="S" style="width: 100%; height: 100%; object-fit: contain; border-radius: 15px;" onerror="this.style.display='none'; this.parentElement.innerText='S'">
                </div>
                <div>
                    <h1>S Quiz</h1>
                    <div class="creator-badge">✨ Created by Sai ✨</div>
                </div>
            </div>
            <p class="subtitle">🎓 AI-Powered Learning Platform</p>
        </header>
        
        <div class="quote-box">
            <div class="quote-text">"{{ quote.text }}"</div>
            <div class="quote-author">— {{ quote.author }}</div>
        </div>
        
        <div class="status {{ 'online' if has_ai else 'offline' }}">
            {{ status_text }}
        </div>
        
        <div class="tabs">
            <div id="tab-topic" class="tab active" onclick="switchTab('topic')">📝 Topic Quiz</div>
            <div id="tab-file" class="tab" onclick="switchTab('file')">📂 File Upload</div>
            <div id="tab-teacher" class="tab" onclick="switchTab('teacher')">👨‍🏫 Teacher Tools</div>
            <div id="tab-help" class="tab" onclick="switchTab('help')">💡 AI Help</div>
        </div>
        
        
        
        <!-- Topic Quiz Tab -->
        <div id="topic-content" class="tab-content active">
            <div class="card">
                <h2>📝 Generate Quiz from Topic</h2>
                
                <div class="form-group">
                    <label>🎯 Topic</label>
                    <input type="text" id="topic" placeholder="e.g., Photosynthesis, Indian History, Python Programming">
                </div>
                
                <div class="grid-2">
                    <div class="form-group">
                        <label>⚡ Difficulty</label>
                        <select id="difficulty">
                            <option value="easy">😊 Easy</option>
                            <option value="medium">🤔 Medium</option>
                            <option value="hard">🔥 Hard</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>🌐 Language</label>
                        <select id="language">
                            <option value="English">🇬🇧 English</option>
                            <option value="Hindi">🇮🇳 Hindi</option>
                            <option value="Telugu">🇮🇳 Telugu</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>🔢 Number of Questions (1-100)</label>
                    <input type="number" id="num_questions" min="1" max="100" value="5" placeholder="Enter 1 to 100">
                </div>
                
                <button onclick="generateTopicQuiz()" id="topicBtn">
                    🚀 Generate Quiz
                </button>
                
                <div id="topicLoading" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    ⏳ AI is crafting your perfect quiz... Please wait...
                </div>
                
                <div id="topicError" class="error" style="display: none;"></div>
                <div id="topicResult"></div>
            </div>
        </div>
        
        <!-- File Upload Tab -->
        <div id="file-content" class="tab-content">
            <div class="card">
                <h2>📂 Generate Quiz from File</h2>
                
                <div class="form-group">
                    <label>📄 Upload File (PDF, DOCX, TXT)</label>
                    <input type="file" id="fileInput" accept=".pdf,.docx,.doc,.txt">
                </div>
                
                <div class="grid-2">
                    <div class="form-group">
                        <label>⚡ Difficulty</label>
                        <select id="fileDifficulty">
                            <option value="easy">😊 Easy</option>
                            <option value="medium">🤔 Medium</option>
                            <option value="hard">🔥 Hard</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>🔢 Number of Questions (1-100)</label>
                        <input type="number" id="fileNumQuestions" min="1" max="100" value="5">
                    </div>
                </div>
                
                <button onclick="generateFileQuiz()" id="fileBtn">
                    📤 Upload & Generate Quiz
                </button>
                
                <div id="fileLoading" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    ⏳ Processing file and generating quiz...
                </div>
                
                <div id="fileInfo" class="file-info" style="display: none;"></div>
                <div id="fileError" class="error" style="display: none;"></div>
                <div id="fileResult"></div>
            </div>
        </div>
        
        <!-- Teacher Tools Tab -->
        <div id="teacher-content" class="tab-content">
            <div class="card">
                <h2>👨‍🏫 Teacher Assistant</h2>
                
                <div class="form-group">
                    <label>🎯 What do you need?</label>
                    <select id="teacherTask">
                        <option value="lesson">📚 Create Lesson Plan</option>
                        <option value="explanation">💡 Explain Concept Simply</option>
                        <option value="activity">🎮 Suggest Learning Activity</option>
                        <option value="assessment">📊 Create Assessment Rubric</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>📖 Topic/Subject</label>
                    <input type="text" id="teacherTopic" placeholder="e.g., Photosynthesis for Grade 8">
                </div>
                
                <div class="form-group">
                    <label>📝 Additional Details (Optional)</label>
                    <textarea id="teacherDetails" placeholder="Any specific requirements or context..."></textarea>
                </div>
                
                <button onclick="getTeacherHelp()" id="teacherBtn">
                    ✨ Get AI Assistance
                </button>
                
                <div id="teacherLoading" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    ⏳ AI is preparing your teaching materials...
                </div>
                
                <div id="teacherError" class="error" style="display: none;"></div>
                <div id="teacherResult"></div>
            </div>
        </div>
        
        <!-- AI Help Tab -->
        <div id="help-content" class="tab-content">
            <div class="card">
                <h2>💡 Ask AI for Help</h2>
                
                <div class="form-group">
                    <label>❓ Your Question</label>
                    <textarea id="helpQuestion" placeholder="Ask anything... e.g., 'Explain photosynthesis in simple terms'"></textarea>
                </div>
                
                <div class="form-group">
                    <label>🎨 Response Style</label>
                    <select id="helpStyle">
                        <option value="simple">😊 Simple & Student-Friendly</option>
                        <option value="detailed">📚 Detailed Explanation</option>
                        <option value="examples">💡 With Examples</option>
                        <option value="stepbystep">📝 Step-by-Step</option>
                    </select>
                </div>
                
                <button onclick="getAIHelp()" id="helpBtn">
                    💬 Ask AI
                </button>
                
                <div id="helpLoading" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    ⏳ AI is thinking...
                </div>
                
                <div id="helpError" class="error" style="display: none;"></div>
                <div id="helpResult"></div>
            </div>
        </div>
    </div>
    
    <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>
"""

@app.route('/')
def home():
    quote = get_random_quote()
    # Pass detailed status for debugging if offline
    status_text = AI_STATUS
    if not HAS_AI and (CLOUDFLARE_API_KEY or GEMINI_API_KEY):
        # Key exists but something else failed
        status_text = f"❌ AI Offline - {AI_STATUS}"
    elif not CLOUDFLARE_API_KEY and not GEMINI_API_KEY:
        status_text = "❌ Add API Key to Unlock AI Features (Cloudflare or Gemini)"
    else:
        status_text = f"✅ AI Online ({AI_PROVIDER}) - Unlimited Learning Power!"
        
    return render_template_string(HTML_TEMPLATE, has_ai=HAS_AI, status_text=status_text, quote=quote)

@app.route('/generate_topic', methods=['POST'])
def generate_topic_quiz():
    if not HAS_AI:
        return jsonify({'error': 'AI not configured'}), 400
    
    data = request.json
    topic = data.get('topic', '')
    difficulty = data.get('difficulty', 'easy')
    language = data.get('language', 'English')
    num_questions = min(data.get('num_questions', 5), 100)
    context = data.get('context') or data.get('content_text') or ''
    
    if context:
        prompt = f"""
        Generate {num_questions} multiple-choice questions based on this text in {language}:
        "{context[:5000]}"
        
        Difficulty: {difficulty}
        Topic: {topic}
        
        For EACH question, provide:
        1. The question text
        2. Four options (A, B, C, D)
        3. The correct answer
        4. A simple explanation
        5. Brief explanations for wrong options
        
        Return ONLY a JSON array as shown earlier.
        """
    else:
        prompt = f"""
        Generate {num_questions} multiple-choice questions about "{topic}" in {language}.
        Difficulty: {difficulty}
        
        For EACH question, provide:
        1. The question text
        2. Four options (A, B, C, D)
        3. The correct answer
        4. A simple explanation
        5. Brief explanations for wrong options
        
        Return ONLY a JSON array:
        [
            {{
                "prompt": "Question text",
                "choices": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "The exact correct option text",
                "explanation": "Why this is correct",
                "wrong_explanations": {{
                    "Wrong Option 1": "Why this is wrong",
                    "Wrong Option 2": "Why this is wrong",
                    "Wrong Option 3": "Why this is wrong"
                }}
            }}
        ]
        """
    
    try:
        if model is None:
            raise Exception("AI Model is not initialized")
            
        print(f"DEBUG Topic: Generating with model {getattr(model, 'model_name', 'Unknown')}")
        response = generate_with_fallback(prompt)
        text_response = response.text.strip()
        
        # Robust parsing
        cleaned_text = text_response
        if '```json' in cleaned_text:
            cleaned_text = cleaned_text.split('```json')[1].split('```')[0]
        elif '```' in cleaned_text:
            cleaned_text = cleaned_text.split('```')[1].split('```')[0]
        
        try:
            questions = json.loads(cleaned_text.strip())
        except json.JSONDecodeError:
            print(f"JSON Parse Error in Topic Quiz. Raw: {text_response}")
            return jsonify({'error': 'AI generation failed (Invalid JSON). Please try again.'}), 500
        
        # Handle cases where AI wraps the list in an object
        if isinstance(questions, dict):
            if 'questions' in questions:
                questions = questions['questions']
            elif 'quiz' in questions:
                questions = questions['quiz']
            else:
                # Search for any list value
                found = False
                for key, val in questions.items():
                    if isinstance(val, list):
                        questions = val
                        found = True
                        break
                
                if not found:
                    print(f"DEBUG Topic: Dict returned but no list found. Keys: {list(questions.keys())}")
                    # If it's a single question object, wrap it
                    if 'prompt' in questions and 'choices' in questions:
                        questions = [questions]

        if not isinstance(questions, list):
            print(f"DEBUG Topic: Final type check failed. Got: {type(questions)}")
            return jsonify({'error': 'AI returned invalid quiz format'}), 500

        return jsonify({'questions': questions})
    
    except Exception as e:
        # Write robust log
        try:
            with open('debug_error.log', 'w') as f:
                f.write(f"ERROR in generate_topic_quiz: {e}\n")
                f.write(traceback.format_exc())
        except:
            print(f"Failed to write to debug_error.log")
            
        print(f"ERROR: {str(e)}")
        model_name = "Unknown"
        if model:
             model_name = getattr(model, 'model_name', 'Unknown')
             
        return jsonify({'error': f'AI generation failed (Model: {model_name}): {str(e)}'}), 500

@app.route('/generate_file', methods=['POST'])
def generate_file_quiz():
    try:
        if not HAS_AI:
            return jsonify({'error': 'AI not configured'}), 400
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        difficulty = request.form.get('difficulty', 'easy')
        try:
            num_questions = int(request.form.get('num_questions', 5))
        except (ValueError, TypeError):
            num_questions = 5
        num_questions = min(num_questions, 100)
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        text = extract_text_from_file(filepath)
        
        if text.startswith('Error'):
            return jsonify({'error': text}), 400
            
        if model is None:
            raise Exception("AI Model is not initialized")
        
        prompt = f"""
        Based on the following text, generate {num_questions} multiple-choice questions.
        Difficulty: {difficulty}
        
        Text:
        {text[:5000]}
        
        For EACH question, provide:
        1. The question text
        2. Four options
        3. The correct answer
        4. Explanation of why it's correct
        Return ONLY a valid JSON array:
        [
            {{
                "prompt": "Question text",
                "choices": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "The exact correct option text",
                "explanation": "Why this is correct",
                "wrong_explanations": {{
                    "Choice1": "Why Choice1 is wrong",
                    "Choice2": "Why Choice2 is wrong",
                    "Choice3": "Why Choice3 is wrong"
                }}
            }}
        ]
        """
        
        response = generate_with_fallback(prompt)
        text_response = response.text.strip()
        
        # Robust parsing
        cleaned_text = text_response.strip()
        if '```json' in cleaned_text:
            cleaned_text = cleaned_text.split('```json')[1].split('```')[0]
        elif '```' in cleaned_text:
            cleaned_text = cleaned_text.split('```')[1].split('```')[0]
        
        try:
            questions = json.loads(cleaned_text)
            print(f"DEBUG: Parsed JSON type: {type(questions)}")
        except json.JSONDecodeError:
            print(f"JSON Parse Error. Raw response: {text_response}")
            return jsonify({'error': 'AI returned invalid format. Please try again.'}), 500
        
        # Handle cases where AI wraps the list in an object
        print(f"DEBUG: Checking questions type: {type(questions)}")
        
        if isinstance(questions, dict):
            # Try to find the list of questions
            if 'questions' in questions:
                questions = questions['questions']
            elif 'quiz' in questions:
                questions = questions['quiz']
            else:
                # Search for any list value
                found = False
                for key, val in questions.items():
                    if isinstance(val, list):
                        questions = val
                        found = True
                        break
                
                if not found:
                    print(f"DEBUG: Dict returned but no list found. Keys: {list(questions.keys())}")
                    # If it's a single question object, wrap it
                    if 'prompt' in questions and 'choices' in questions:
                        questions = [questions]

        if not isinstance(questions, list):
            print(f"DEBUG: Final type check failed. Got: {type(questions)}")
            return jsonify({'error': 'AI returned invalid quiz format (not a list)'}), 500

        return jsonify({
            'questions': questions,
            'filename': filename,
            'text_length': len(text)
        })
    
    except Exception as e:
        with open('debug_error.log', 'w') as f:
            f.write(f"ERROR in generate_file_quiz: {e}\n")
            f.write(traceback.format_exc())
        print(f"ERROR: Written to debug_error.log")
        return jsonify({'error': f'Quiz generation failed: {str(e)}'}), 500

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('.', 'manifest.json')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory('.', 'sw.js')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'icon-192.png'), 200, {'Content-Type': 'image/png'} if os.path.exists('static/icon-192.png') else ('', 204)

@app.route('/static/icon-192.png')
@app.route('/static/icon-512.png')
@app.route('/static/logo.png')
def serve_icons():
    # If the icon exists, serve it
    path = request.path.lstrip('/')
    if os.path.exists(path):
        return send_from_directory('.', path)
    
    # Otherwise serve a generated SVG as a fallback
    color = "#667eea" if "192" in path else "#764ba2"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
        <rect width="512" height="512" rx="100" fill="{color}"/>
        <text x="50%" y="55%" dominant-baseline="middle" text-anchor="middle" font-family="Poppins, sans-serif" font-size="300" font-weight="bold" fill="white">S</text>
    </svg>'''
    return svg, 200, {'Content-Type': 'image/svg+xml'}

@app.route('/teacher_help', methods=['POST'])
def teacher_help():
    if not HAS_AI:
        return jsonify({'error': 'AI not configured'}), 400
    
    data = request.json
    task = data.get('task', 'lesson')
    topic = data.get('topic', '')
    details = data.get('details', '')
    
    prompts = {
        'lesson': f"Create a detailed lesson plan for teaching '{topic}'. {details}",
        'explanation': f"Explain '{topic}' in simple, student-friendly language. {details}",
        'activity': f"Suggest engaging learning activities for '{topic}'. {details}",
        'assessment': f"Create an assessment rubric for '{topic}'. {details}"
    }
    
    prompt = prompts.get(task, prompts['lesson'])
    
    try:
        if model is None:
            raise Exception("AI Model is not initialized")
            
        response = generate_with_fallback(prompt)
        text = response.text
        # Ensure bold formatting is converted to HTML for better display if needed, 
        # but for now we rely on the frontend pre-wrap.
        # Check for empty response
        if not text:
            return jsonify({'error': 'AI returned empty response'}), 500
            
        return jsonify({'response': text})
    except Exception as e:
        with open('debug_error.log', 'w') as f:
            f.write(f"ERROR in teacher_help: {e}\n")
            f.write(traceback.format_exc())
            
        print(f"ERROR in teacher_help: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/ai_help', methods=['POST'])
def ai_help():
    if not HAS_AI:
        return jsonify({'error': 'AI not configured'}), 400
    
    data = request.json
    question = data.get('question', '')
    style = data.get('style', 'simple')
    
    style_prompts = {
        'simple': "Explain in simple, easy-to-understand language: ",
        'detailed': "Provide a detailed, comprehensive explanation: ",
        'examples': "Explain with clear examples: ",
        'stepbystep': "Explain step-by-step: "
    }
    
    prompt = style_prompts.get(style, style_prompts['simple']) + question
    
    try:
        if model is None:
            raise Exception("AI Model is not initialized")
            
        response = generate_with_fallback(prompt)
        return jsonify({'response': response.text})
    except Exception as e:
        with open('debug_error.log', 'w') as f:
            f.write(f"ERROR in ai_help: {e}\n")
            f.write(traceback.format_exc())
            
        print(f"ERROR in ai_help: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌟 QUIZ AI ACADEMY - PREMIUM VERSION 🌟")
    print("="*60)
    print(f"✅ AI Status: {'Online (' + AI_PROVIDER + ')' if HAS_AI else 'Offline'}")
    print("✨ Premium Features:")
    print("   - Custom question count (1-100)")
    print("   - Beautiful animated UI")
    print("   - Motivational quotes")
    print("   - Enhanced emojis")
    print("   - All learning tools")
    print("📱 Opening at: http://localhost:5002")
    print("="*60 + "\n")
    
    import webbrowser
    import threading
    
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open('http://localhost:5002')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)
