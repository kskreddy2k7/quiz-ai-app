# 🎓 S Quiz by Sai - Premium AI Learning Platform (Web Edition)

## 🌟 Overview

**S Quiz** is a comprehensive, premium AI-powered learning platform designed for both teachers and students. Created by **Sai**, it leverages Google Gemini AI to generate quizzes, provide deep explanations, and assist with complex educational tasks. This version is optimized as a high-performance **Web Application** and **PWA**.

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

## 🚀 How to Use

### 🌐 Website Access
- The website is designed to be hosted on platforms like **Render**, **Railway**, or **Heroku**.
- Once deployed, simply visit the URL in any browser.

### 📱 Install as App (PWA)
1. Open the website on your phone (Chrome for Android / Safari for iOS).
2. Tap **"Add to Home Screen"** or the Install icon.
3. The website will now run like a native app without the browser bar!

---

## 📦 Installation & Setup (Local)

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

### 4. Run Locally
```bash
python app.py
```
Open `http://localhost:5002` in your browser.

---

## 📂 Project Structure
```
S-Quiz/
├── app.py             # Main Flask Application
├── static/            # Static assets (CSS/JS)
├── uploads/           # Temporary folder for processed files
├── requirements.txt   # Web Server Dependencies
├── manifest.json      # PWA Configuration
├── sw.js              # Service Worker for Offline/PWA
├── Procfile           # Render/Railway Deployment Config
└── secrets.json       # (Local only) Your API key
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

