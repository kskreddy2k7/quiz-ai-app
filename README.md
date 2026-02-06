# 🎓 S Quiz by Sai - Premium AI Learning Platform

## 🌟 Overview

**S Quiz** is a comprehensive, premium AI-powered learning platform designed for both teachers and students. Created by **Sai**, it leverages Google Gemini AI to generate quizzes, provide deep explanations, and assist with complex educational tasks.

---

## ✨ Features

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

## 🚀 Quick Start (Windows)

### Option 1: Premium Desktop App (Recommended)
Double-click: `START_S_QUIZ.bat`

### Option 2: Mobile Browser (PWA)
- Open `https://sai.onrender.com` on your phone.
- Tap **"Add to Home Screen"** in your browser menu.
- The website will now run like a native app without the browser bar!

---

### Option 3: Android APK (Native)
- Download the APK from the GitHub Actions artifacts (see below for details).
This repository is configured with **GitHub Actions** to automatically build an Android APK using **Buildozer**.
1. Push your code to the `main` branch.
2. Go to the **Actions** tab in GitHub.
3. Download the generated APK from the successful "Build Android APK" workflow.

---

## 📦 Installation & Setup

### 1. Requirements
- Python 3.10+
- Google Gemini API Key

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create or edit `secrets.json` in the root directory:
```json
{
    "GEMINI_API_KEY": "YOUR_ACTUAL_API_KEY_HERE"
}
```
*Note: Your `secrets.json` is automatically ignored by git to keep your key safe.*

---

## 📂 File Structure (Keep for GitHub)
```
S-Quiz/
├── premium_app.py             # Main Premium Web Logic
├── premium_desktop_app.py     # Desktop Wrapper (PyWebView)
├── main.py                    # Mobile App Logic (Kivy)
├── buildozer.spec             # Android Build Configuration
├── requirements.txt           # Project Dependencies
├── START_S_QUIZ.bat           # Easy Windows Launcher
├── BRANDED_VERSION.md         # Branding Documentation
├── .github/workflows/         # Auto-APK Build Workflow
└── secrets.json               # (Local only) Your API key
```

---

## 🔐 Privacy & Security
- **No Data Collection**: Your files and questions are processed in real-time and not stored.
- **Secure API**: Uses standard Google Generative AI integration.
- **Safety First**: Your API keys are excluded from version control via `.gitignore`.

---

## 🎨 Premium Branding
This version of the app features the **"S Quiz"** branding by **Sai**, including a floating animated logo and a modern glassmorphism UI design.

---

## 🎉 Credits
- Created by: **Sai**
- Powered by: **Google Gemini AI**
- Frameworks: **Flask, Kivy, PyWebView**

---

**Enjoy your premium AI learning experience with S Quiz!** 🚀🎓
