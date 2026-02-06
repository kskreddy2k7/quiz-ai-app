# Product Requirements Document: QuizAI Academy App

## 1. Introduction
QuizAI Academy is an AI-powered mobile education platform designed to revolutionize how students study. It converts study materials (text, PDFs, DOCs) into interactive quizzes and provides an intelligent doubt-solving assistant. The functionality is wrapped in a "futuristic", high-fidelity glassmorphism UI.

## 2. Core Features

### 2.1 AI Quiz Generation
- **Input Methods**:
  - Direct Text Input (Paste content).
  - File Upload (PDF, DOCX, TXT).
  - Topic Selection (Subject + Topic name).
- **Configuration**:
  - Difficulty Levels: Easy, Medium, Hard.
  - Number of Questions: Custom (default 5, max 20).
  - Question Types: Multiple Choice (MCQ), True/False, Mixed.
- **Output**:
  - Structured questions with 4 options.
  - Correct answer identification.
  - Detailed explanations for answers.

### 2.2 AI Doubt Solver (Tutor Mode)
- **Chat Interface**:
  - Real-time chat with an AI educational assistant.
  - Context-aware responses based on quiz topics.
  - Support for general academic queries.
- **Interactive Elements**:
  - "Ask about this question" from within quiz results.

### 2.3 Interactive Quiz Experience
- **Gameplay**:
  - One question per screen.
  - Visual feedback for correct/incorrect answers.
  - Timer/Stopwatch.
  - Progress bar.
- **Post-Quiz Review**:
  - Score summary.
  - Detailed breakdown of answers.
  - Explanations for every question.

### 2.4 User Progress & Analytics
- **Dashboard**:
  - Total quizzes taken.
  - Average score.
  - Performance trends over time.
- **Persistence**:
  - Local storage of quiz history.
  - User preferences (Theme, Difficulty).

### 2.5 Miscellaneous
- **Daily Motivation**: A daily quote or encouraging message on launch.
- **Settings**: Manage permissions, clear data, toggle sound/haptics.

## 3. Non-Functional Requirements

### 3.1 User Interface (UI) / User Experience (UX)
- **Aesthetic**: Futuristic, "Sci-Fi" Glassmorphism.
- **Color Palette**: Dark mode base with neon accents (Cyan, Purple, Electric Blue).
- **Animations**: Smooth transitions between screens, micro-interactions for button clicks.
- **Transparency**: Glass-like overlays for cards and dialogs.

### 3.2 Performance
- **Responsiveness**: UI must remain responsive during AI generation (blocking operations offloaded to threads/async).
- **Startup Time**: App should load to Home or Splash within 2 seconds.

### 3.3 Compatibility
- **Platform**: Android (APK/AAB via Buildozer).
- **Screen Sizes**: Responsive layout adapting to various mobile aspect ratios.

### 3.4 Security & Privacy
- **API Keys**: Secure management of AI provider keys.
- **Data Privacy**: Local processing where possible; minimal data retention on server (if applicable).

## 4. Technical Stack
- **Language**: Python 3.x
- **Framework**: Kivy (UI), KivyMD (Components).
- **AI Provider**: Google Gemini (Primary) / OpenAI (Fallback).
- **Local Storage**: JSON / SQLite.
- **Build Tool**: Buildozer (for Android packaging).
