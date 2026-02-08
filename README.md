# 🎓 S Quiz by Sai - Premium AI Learning Platform (Web Edition)

## 🌟 Overview

**S Quiz** is a comprehensive, premium AI-powered learning platform designed for both teachers and students. Created by **Sai**, it leverages Google Gemini AI to generate quizzes, provide deep explanations, and assist with complex educational tasks. This version is optimized as a high-performance **Web Application** and **PWA**.

---

## ✨ Features

### 🔐 Secure Authentication
- **Google Sign-In**: One-click login with your Google account
- **Traditional Login**: Username/password authentication
- **Guest Mode**: Try the app without creating an account
- **Profile Management**: View your progress and stats
- **Secure Token Handling**: Industry-standard JWT authentication

### 📝 Smart Quiz Generation
- **Topic-Based**: Generate quizzes on any topic instantly (1 to 100 questions).
- **File Upload**: Upload PDF, DOCX, or TXT files to generate quizzes from your own study material.
- **Multi-Language**: Support for English, Hindi, and Telugu.
- **Deep Explanations**: 
  - Detailed reasoning for correct answers.
  - Educational "Why this is wrong" explanations for EVERY incorrect option.

### 👨‍🏫 Teacher Assistant Tools
- **Lesson Planner**: Create structured lesson plans in seconds.
- **Concept Simplifier**: Transform complex topics into student-friendly explanations.
- **Activity Suggester**: Get creative ideas for classroom or home learning.
- **Rubric Creator**: Generate professional assessment rubrics.

### 💬 AI Study Help
- **Instant Doubt Solving**: Ask any academic question.
- **Customizable Styles**: Simple, Detailed, Step-by-Step, or Example-based responses.

---

## 🚀 How to Use

### 🌐 Website Access
- The website is designed to be hosted on platforms like **Render**, **Railway**, or **Heroku**.
- Once deployed, simply visit the URL in any browser.

### 📱 Install as App (PWA)
1. Open the website on your phone (Chrome for Android / Safari for iOS).
2. Tap **"Add to Home Screen"** or the Install icon.
3. The website will now run like a native app without the browser bar!

### 📱 Android APK (Native App)
S Quiz is also available as a native Android app! The APK is automatically built using GitHub Actions.

**Download the APK**:
- Go to [Releases](https://github.com/kskreddy2k7/quiz-ai-app/releases)
- Download the latest `S-Quiz-*.apk` file
- Install on your Android device

**Build from Source**:
See [build_notes.md](build_notes.md) for detailed instructions on building the Android APK locally or using GitHub Actions.

---

## 📦 Installation & Setup (Local)

### 1. Requirements
- Python 3.10+
- Google Gemini API Key (for AI features)
- Google OAuth Client ID (for Google Sign-In) - Optional but recommended

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory (copy from `.env.example`):
```bash
# Required
GEMINI_API_KEY=your-gemini-api-key-here
SECRET_KEY=your-secure-jwt-secret-key

# Optional (for Google Sign-In)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

**To enable Google Sign-In**, see [GOOGLE_AUTH_SETUP.md](GOOGLE_AUTH_SETUP.md) for detailed instructions.

### 4. Run Locally
```bash
python main_web.py
```
Open `http://localhost:8000` in your browser.

---

## 📂 Project Structure
```
S-Quiz/
├── .github/workflows/ # GitHub Actions CI/CD
│   └── build-apk.yml  # Android APK build workflow
├── main.py            # Android app entry point (Kivy)
├── main_web.py        # Web app entry point (FastAPI)
├── static/            # Static assets (CSS/JS)
├── api/               # API endpoints
├── services/          # Business logic
├── models/            # Database models
├── uploads/           # Temporary folder for processed files
├── requirements.txt   # Web Server Dependencies
├── buildozer.spec     # Android build configuration
├── build_notes.md     # Android build instructions
├── manifest.json      # PWA Configuration
├── sw.js              # Service Worker for Offline/PWA
├── Procfile           # Render/Railway Deployment Config
└── render.yaml        # Render deployment config
```

---

## 🔐 Privacy & Security
- **Secure Processing**: Your files are processed securely and not stored permanently.
- **Safety First**: Your API keys are excluded from version control via `.gitignore`.

---

## 🎨 Premium Branding
This version of the app features the **"S Quiz"** branding by **Sai**, including a floating animated logo and a modern glassmorphism UI design.

---

## 🎉 Credits
- Created by: **Sai**
- Powered by: **Google Gemini AI**
- Framework: **Flask (Python)**

---

**Enjoy your premium AI learning experience with S Quiz!** 🚀🎓

