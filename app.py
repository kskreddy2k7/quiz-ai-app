"""
Quiz AI Academy - PREMIUM VERSION
Features:
- Custom question count (1-100)
- Premium UI with gradients and animations
- Motivational quotes
- Enhanced emojis throughout
- Beautiful design
"""

from flask import Flask, render_template_string, request, jsonify
import json
import os
import random
from werkzeug.utils import secure_filename
import secrets as secret_module

# Load API key
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GEMINIAPIKEY') or ''

if not GEMINI_API_KEY:
    try:
        with open('secrets.json', 'r') as f:
            GEMINI_API_KEY = json.load(f).get('GEMINI_API_KEY', '')
    except:
        GEMINI_API_KEY = ''

# Initialize Gemini
HAS_GEMINI = False
model = None
AI_STATUS = "Offline"
AI_DEBUG = ""

if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Dynamic discovery of models
        available_models = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority order for models (Updated for latest Gemini versions)
        preferred_models = [
            'gemini-2.5-flash', 
            'gemini-2.0-flash', 
            'gemini-1.5-flash', 
            'gemini-flash-latest', 
            'gemini-1.5-flash-latest', 
            'gemini-1.5-pro', 
            'gemini-pro-latest'
        ]
        selected_model_name = None
        
        for pm in preferred_models:
            if pm in available_models:
                selected_model_name = pm
                break
                
        if not selected_model_name and available_models:
            selected_model_name = available_models[0]
            
        if selected_model_name:
            model = genai.GenerativeModel(selected_model_name)
            HAS_GEMINI = True
            AI_STATUS = "Online"
            print(f"✅ Gemini AI initialized with model: {selected_model_name}")
        else:
            AI_STATUS = "Offline (No available models found)"
    except Exception as e:
        AI_STATUS = f"Offline (Error: {str(e)[:50]}...)"
        AI_DEBUG = str(e)
        print(f"⚠️ Gemini initialization failed: {e}")
else:
    AI_STATUS = "Offline (No API Key found)"

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
        }
        
        .tab {
            padding: 15px 30px;
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: #fff;
            font-weight: 600;
            font-size: 1.05rem;
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
        
        .history-item {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s ease;
        }
        
        .history-item:hover {
            background: rgba(255,255,255,0.2);
            transform: scale(1.02);
        }
        
        .history-info h4 {
            margin-bottom: 5px;
            font-size: 1.1rem;
        }
        
        .history-info p {
            font-size: 0.9rem;
            color: rgba(255,255,255,0.7);
        }
        
        .history-score {
            font-size: 1.5rem;
            font-weight: 700;
            color: #38ef7d;
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
                <div class="logo">S</div>
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
            <div class="tab active" onclick="switchTab('topic')">📝 Topic Quiz</div>
            <div class="tab" onclick="switchTab('file')">📂 File Upload</div>
            <div class="tab" onclick="switchTab('history')">📜 Recent Tests</div>
            <div class="tab" onclick="switchTab('teacher')">👨‍🏫 Teacher Tools</div>
            <div class="tab" onclick="switchTab('help')">💡 AI Help</div>
        </div>
        
        <!-- History Tab -->
        <div id="history-content" class="tab-content">
            <div class="card">
                <h2>📜 Your Recent Tests</h2>
                <div id="historyList">
                    <p style="text-align: center; color: rgba(255,255,255,0.6); padding: 20px;">No tests taken yet. Start a quiz to see it here!</p>
                </div>
            </div>
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
    
    <script>
        function switchTab(tab) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tab + '-content').classList.add('active');
            event.target.classList.add('active');
        }
        
        async function generateTopicQuiz() {
            const topic = document.getElementById('topic').value;
            const difficulty = document.getElementById('difficulty').value;
            const language = document.getElementById('language').value;
            const num_questions = parseInt(document.getElementById('num_questions').value);
            
            if (!topic) {
                alert('Please enter a topic!');
                return;
            }
            
            if (num_questions < 1 || num_questions > 100) {
                alert('Please enter a number between 1 and 100!');
                return;
            }
            
            showLoading('topic');
            
            try {
                const response = await fetch('/generate_topic', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({topic, difficulty, language, num_questions})
                });
                
                const data = await response.json();
                
                if (data.error) {
                    showError('topic', data.error);
                } else {
                    displayQuiz('topic', data.questions);
                }
            } catch (error) {
                showError('topic', error.message);
            } finally {
                hideLoading('topic');
            }
        }
        
        async function generateFileQuiz() {
            const fileInput = document.getElementById('fileInput');
            const difficulty = document.getElementById('fileDifficulty').value;
            const num_questions = parseInt(document.getElementById('fileNumQuestions').value);
            
            if (!fileInput.files[0]) {
                alert('Please select a file!');
                return;
            }
            
            if (num_questions < 1 || num_questions > 100) {
                alert('Please enter a number between 1 and 100!');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('difficulty', difficulty);
            formData.append('num_questions', num_questions);
            
            showLoading('file');
            
            try {
                const response = await fetch('/generate_file', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.error) {
                    showError('file', data.error);
                } else {
                    document.getElementById('fileInfo').style.display = 'block';
                    document.getElementById('fileInfo').textContent = `✅ Processed: ${data.filename} (${data.text_length} characters)`;
                    displayQuiz('file', data.questions);
                }
            } catch (error) {
                showError('file', error.message);
            } finally {
                hideLoading('file');
            }
        }
        
        async function getTeacherHelp() {
            const task = document.getElementById('teacherTask').value;
            const topic = document.getElementById('teacherTopic').value;
            const details = document.getElementById('teacherDetails').value;
            
            if (!topic) {
                alert('Please enter a topic!');
                return;
            }
            
            showLoading('teacher');
            
            try {
                const response = await fetch('/teacher_help', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({task, topic, details})
                });
                
                const data = await response.json();
                
                if (data.error) {
                    showError('teacher', data.error);
                } else {
                    displayTeacherHelp(data.response);
                }
            } catch (error) {
                showError('teacher', error.message);
            } finally {
                hideLoading('teacher');
            }
        }
        
        async function getAIHelp() {
            const question = document.getElementById('helpQuestion').value;
            const style = document.getElementById('helpStyle').value;
            
            if (!question) {
                alert('Please enter a question!');
                return;
            }
            
            showLoading('help');
            
            try {
                const response = await fetch('/ai_help', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question, style})
                });
                
                const data = await response.json();
                
                if (data.error) {
                    showError('help', data.error);
                } else {
                    displayAIHelp(data.response);
                }
            } catch (error) {
                showError('help', error.message);
            } finally {
                hideLoading('help');
            }
        }
        
        function showLoading(tab) {
            document.getElementById(tab + 'Loading').style.display = 'block';
            document.getElementById(tab + 'Error').style.display = 'none';
            document.getElementById(tab + 'Result').innerHTML = '';
            document.getElementById(tab + 'Btn').disabled = true;
        }
        
        function hideLoading(tab) {
            document.getElementById(tab + 'Loading').style.display = 'none';
            document.getElementById(tab + 'Btn').disabled = false;
        }
        
        function showError(tab, message) {
            document.getElementById(tab + 'Error').textContent = '❌ ' + message;
            document.getElementById(tab + 'Error').style.display = 'block';
        }
        
        let currentQuestions = [];
        let userAnswers = {};

        function displayQuiz(tab, questions) {
            currentQuestions = questions;
            userAnswers = {};
            
            const resultDiv = document.getElementById(tab + 'Result');
            resultDiv.innerHTML = '<h2 style="margin: 40px 0 30px 0; text-align: center;">📚 Your Premium Quiz</h2>';
            
            questions.forEach((q, index) => {
                const card = document.createElement('div');
                card.className = 'question-card';
                card.id = `q-card-${index}`;
                
                let html = `
                    <div class="question-text">
                        <strong>Q${index + 1}:</strong> ${q.prompt}
                    </div>
                    <div class="options-container">
                `;
                
                q.choices.forEach((choice, i) => {
                    html += `
                        <div class="option" onclick="selectOption(${index}, '${choice.replace(/'/g, "\\'")}', this)">
                            ${String.fromCharCode(65 + i)}) ${choice}
                        </div>
                    `;
                });
                
                html += `</div>`; // End options-container
                
                // Add hidden result sections
                html += `
                    <div class="explanation hidden" id="exp-${index}">
                        <div class="explanation-title">💡 Explanation:</div>
                        ${q.explanation}
                    </div>
                `;
                
                if (q.wrong_explanations) {
                    html += `<div class="wrong-explanations-group hidden" id="wrong-exp-${index}">`;
                    for (const [option, explanation] of Object.entries(q.wrong_explanations)) {
                        html += `
                            <div class="wrong-explanation">
                                <strong>❌ Why "${option}" is wrong:</strong><br>
                                ${explanation}
                            </div>
                        `;
                    }
                    html += `</div>`;
                }
                
                card.innerHTML = html;
                resultDiv.appendChild(card);
            });
            
            // Add submit button
            const submitBtn = document.createElement('button');
            submitBtn.id = 'submit-quiz-btn';
            submitBtn.style.marginTop = '30px';
            submitBtn.textContent = '✅ Submit Quiz & Get Results';
            submitBtn.onclick = () => checkQuiz(tab);
            resultDiv.appendChild(submitBtn);
        }

        function selectOption(qIndex, choice, element) {
            // Already submitted? Don't allow changes
            if (document.getElementById('submit-quiz-btn').classList.contains('hidden')) return;
            
            userAnswers[qIndex] = choice;
            
            // UI Update
            const container = element.parentElement;
            container.querySelectorAll('.option').forEach(opt => opt.classList.remove('selected'));
            element.classList.add('selected');
        }

        function checkQuiz(tab) {
            if (Object.keys(userAnswers).length < currentQuestions.length) {
                if (!confirm('You haven\'t answered all questions. Submit anyway?')) return;
            }
            
            let score = 0;
            currentQuestions.forEach((q, index) => {
                const isCorrect = userAnswers[index] === q.answer;
                if (isCorrect) score++;
                
                const card = document.getElementById(`q-card-${index}`);
                const options = card.querySelectorAll('.option');
                
                options.forEach(opt => {
                    const optText = opt.textContent.split(') ')[1].trim();
                    if (optText === q.answer) {
                        opt.classList.add('correct');
                        opt.innerHTML += ' ✅ (Correct)';
                    } else if (userAnswers[index] === optText) {
                        opt.classList.add('wrong');
                        opt.innerHTML += ' ❌ (Your Choice)';
                    }
                    opt.classList.remove('selected');
                });
                
                // Reveal explanations
                document.getElementById(`exp-${index}`).classList.remove('hidden');
                const wrongExp = document.getElementById(`wrong-exp-${index}`);
                if (wrongExp) wrongExp.classList.remove('hidden');
            });
            
            // Save to history
            saveToHistory({
                topic: tab === 'topic' ? document.getElementById('topic').value : 'File Quiz',
                score: score,
                total: currentQuestions.length,
                date: new Date().toLocaleString(),
                questions: currentQuestions
            });
            
            // Show score summary
            const resultDiv = document.getElementById(tab + 'Result');
            const summary = document.createElement('div');
            summary.className = 'score-summary';
            const percent = Math.round((score / currentQuestions.length) * 100);
            summary.innerHTML = `
                <h1 style="margin:0; font-size: 3rem;">${percent}%</h1>
                <p style="font-size: 1.5rem;">Score: ${score} / ${currentQuestions.length}</p>
                <div class="creator-badge" style="background: rgba(255,255,255,0.2); margin-bottom: 15px;">
                    ${score === currentQuestions.length ? '🌟 PERFECT! 🌟' : score > currentQuestions.length / 2 ? '👏 GREAT JOB! 👏' : '📚 Keep Learning! 📚'}
                </div>
                <div class="btn-group" style="justify-content: center;">
                    <button class="share-btn" onclick="shareQuiz(${percent})">📢 Share with Friends</button>
                </div>
            `;
            resultDiv.insertBefore(summary, resultDiv.firstChild);
            
            // Hide submit button
            document.getElementById('submit-quiz-btn').classList.add('hidden');
            
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function saveToHistory(quizData) {
            let history = JSON.parse(localStorage.getItem('quizHistory') || '[]');
            history.unshift(quizData);
            if (history.length > 20) history.pop(); // Keep last 20
            localStorage.setItem('quizHistory', JSON.stringify(history));
            loadHistory();
        }

        function loadHistory() {
            const historyList = document.getElementById('historyList');
            const history = JSON.parse(localStorage.getItem('quizHistory') || '[]');
            
            if (history.length === 0) return;
            
            historyList.innerHTML = '';
            history.forEach((item, index) => {
                const percent = Math.round((item.score / item.total) * 100);
                const div = document.createElement('div');
                div.className = 'history-item';
                div.innerHTML = `
                    <div class="history-info">
                        <h4>${item.topic}</h4>
                        <p>📅 ${item.date} • ${item.total} Questions</p>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <span class="history-score">${percent}%</span>
                        <button class="share-btn" onclick="shareQuiz(${percent}, '${item.topic.replace(/'/g, "\\'")}')">🔗 Share</button>
                    </div>
                `;
                historyList.appendChild(div);
            });
        }

        async function shareQuiz(score, topic = "a Quiz") {
            const text = `🚀 I just scored ${score}% on ${topic} in the S Quiz AI Academy! Can you beat me? 🎓✨`;
            const url = window.location.href;

            if (navigator.share) {
                try {
                    await navigator.share({
                        title: 'S Quiz Result',
                        text: text,
                        url: url
                    });
                } catch (err) {
                    console.log('Share failed:', err);
                }
            } else {
                // Fallback: Copy to clipboard
                const dummy = document.createElement("textarea");
                document.body.appendChild(dummy);
                dummy.value = text + " " + url;
                dummy.select();
                document.execCommand("copy");
                document.body.removeChild(dummy);
                alert("Score & Link copied to clipboard! Share it with your friends! 🚀");
            }
        }

        // Load history on startup
        document.addEventListener('DOMContentLoaded', loadHistory);
        
        function displayTeacherHelp(response) {
            const resultDiv = document.getElementById('teacherResult');
            resultDiv.innerHTML = `
                <div class="card" style="margin-top: 30px; background: rgba(255,255,255,0.2);">
                    <h3 style="margin-bottom: 20px;">📋 AI Assistant Response</h3>
                    <div style="white-space: pre-wrap; line-height: 1.8;">${response}</div>
                </div>
            `;
        }
        
        function displayAIHelp(response) {
            const resultDiv = document.getElementById('helpResult');
            resultDiv.innerHTML = `
                <div class="card" style="margin-top: 30px; background: rgba(255,255,255,0.2);">
                    <h3 style="margin-bottom: 20px;">💬 AI Response</h3>
                    <div style="white-space: pre-wrap; line-height: 1.8;">${response}</div>
                </div>
            `;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    quote = get_random_quote()
    # Pass detailed status for debugging if offline
    status_text = AI_STATUS
    if not HAS_GEMINI and GEMINI_API_KEY:
        # Key exists but something else failed
        status_text = f"❌ AI Offline - {AI_STATUS}"
    elif not GEMINI_API_KEY:
        status_text = "❌ Add API Key to Unlock AI Features"
    else:
        status_text = "✅ AI Online - Unlimited Learning Power!"
        
    return render_template_string(HTML_TEMPLATE, has_ai=HAS_GEMINI, status_text=status_text, quote=quote)

@app.route('/generate_topic', methods=['POST'])
def generate_topic_quiz():
    if not HAS_GEMINI:
        return jsonify({'error': 'AI not configured'}), 400
    
    data = request.json
    topic = data.get('topic', '')
    difficulty = data.get('difficulty', 'easy')
    language = data.get('language', 'English')
    num_questions = min(data.get('num_questions', 5), 100)  # Cap at 100
    
    prompt = f"""
    Generate {num_questions} multiple-choice questions about "{topic}" in {language}.
    Difficulty: {difficulty}
    
    For EACH question, provide:
    1. The question text
    2. Four options (A, B, C, D)
    3. The correct answer
    4. A simple explanation of why it's correct
    5. Brief explanations of why EACH wrong option is incorrect
    
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
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        
        questions = json.loads(text)
        return jsonify({'questions': questions})
    
    except Exception as e:
        model_name = model.model_name if model else "None"
        return jsonify({'error': f'AI generation failed (Model: {model_name}): {str(e)}'}), 500

@app.route('/generate_file', methods=['POST'])
def generate_file_quiz():
    if not HAS_GEMINI:
        return jsonify({'error': 'AI not configured'}), 400
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    difficulty = request.form.get('difficulty', 'easy')
    num_questions = min(int(request.form.get('num_questions', 5)), 100)
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    text = extract_text_from_file(filepath)
    
    if text.startswith('Error'):
        return jsonify({'error': text}), 400
    
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
    5. Explanations of why each wrong option is incorrect
    
    Return ONLY a JSON array with the structure shown earlier.
    """
    
    try:
        response = model.generate_content(prompt)
        text_response = response.text.strip()
        
        if '```json' in text_response:
            text_response = text_response.split('```json')[1].split('```')[0]
        elif '```' in text_response:
            text_response = text_response.split('```')[1].split('```')[0]
        
        questions = json.loads(text_response)
        return jsonify({
            'questions': questions,
            'filename': filename,
            'text_length': len(text)
        })
    
    except Exception as e:
        return jsonify({'error': f'Quiz generation failed: {str(e)}'}), 500

@app.route('/teacher_help', methods=['POST'])
def teacher_help():
    if not HAS_GEMINI:
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
        response = model.generate_content(prompt)
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ai_help', methods=['POST'])
def ai_help():
    if not HAS_GEMINI:
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
        response = model.generate_content(prompt)
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌟 QUIZ AI ACADEMY - PREMIUM VERSION 🌟")
    print("="*60)
    print(f"✅ AI Status: {'Online' if HAS_GEMINI else 'Offline'}")
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
    app.run(host='0.0.0.0', port=port, debug=False)
