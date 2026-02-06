# Technical Design Document: QuizAI Academy App

## 1. Architecture Overview
The application follows a **Service-Oriented Architecture (SOA)** within a standard **Model-View-Controller (MVC)** adaptation for Kivy.

- **View (UI)**: Defined in `app/ui/*.kv` and `app/screens/*.py`. Handles presentation and user interaction.
- **Controller (Logic)**: `main.py` acts as the central coordinator, delegating specific business logic to `app/services/`.
- **Model (Data)**: Data structures are defined implicitly in services or as simple Python classes (e.g., `QuizQuestion`). Persistence is handled by `StorageService`.

## 2. Directory Structure

```
quiz-ai-app/
├── main.py                 # Application Entry Point & Global State
├── buildozer.spec          # Android Build Configuration
├── assets/                 # Images, Icons, Fonts
├── app/
│   ├── screens/            # UI Controllers (View Logic)
│   │   ├── home.py
│   │   ├── quiz_play.py
│   │   ├── ai_chat.py
│   │   └── ...
│   ├── ui/                 # Kivy Layout Definitions (.kv)
│   │   ├── home.kv
│   │   ├── quiz_play.kv
│   │   └── ...
│   ├── services/           # Business Logic
│   │   ├── ai_service.py       # Wrapper for AI APIs (Gemini/OpenAI)
│   │   ├── quiz_generator.py   # Prompt engineering & Parsing
│   │   ├── storage_service.py  # Local JSON/DB management
│   │   ├── file_service.py     # File reading (PDF/Docx) extraction
│   │   └── ...
│   ├── utils/              # Helper Functions
│   │   ├── permissions.py
│   │   └── helpers.py
│   └── data/               # Static data or Templates
└── tests/                  # Unit Tests
```

## 3. Data Flow

### 3.1 Quiz Generation Flow
1. **User Input**: User selects topic or uploads file in `QuizSetupScreen`.
2. **Controller**: `QuizSetupScreen` calls `FileService` (if needed) to extract text.
3. **Logic**: `QuizGenerator` receives text + difficulty settings.
4. **AI Call**: `AIService` constructs a prompt and calls the Gemini API.
5. **Parsing**: The JSON response is parsed into `QuizQuestion` objects.
6. **UI Update**: `QuizPlayScreen` is populated with the question list.

### 3.2 Chat/Doubt Solver Flow
1. **User Input**: User types message in `AIChatScreen`.
2. **Logic**: `TutorService` manages chat history context.
3. **AI Call**: `AIService` sends history + system prompt to API.
4. **Response**: Streamed or atomic text response displayed in UI bubble.

## 4. Design System (UI/UX)

The application utilizes a **Futuristic Glassmorphism** design language.

### 4.1 Color Palette
- **Background**: Deep Space Blue / Carbon Black (`#0f0c29` -> `#302b63` gradients).
- **Glass Surface**: Semi-transparent white/blue with background blur (`rgba(255, 255, 255, 0.1)`).
- **Primary Accent**: Neon Cyan and Electric Violet.
- **Text**: White (High Emphasis) and Light Grey (Medium Emphasis).

### 4.2 Typography
- **Headings**: Modern geometric fonts (e.g., 'Orbitron' or 'Roboto-Bold').
- **Body**: Clean readable sans-serif (e.g., 'Roboto', 'Open Sans').

### 4.3 Components
- **Cards**: Rounded corners (20dp), thin semi-transparent borders, drop shadows.
- **Buttons**: Gradient backgrounds with glow effects on press.
- **Inputs**: Underlined or filled capsules with floating labels.

## 5. External Dependencies
- **Core**: `kivy`, `kivymd`
- **AI**: `google-generativeai` (Gemini)
- **Data Processing**: `pypdf`, `python-docx` (for file reading)
- **Async**: `asynckivy` (for non-blocking UI operations)

## 6. Security & Storage
- **Credentials**: API Keys are loaded from environment variables or secure local config (not hardcoded).
- **Local Data**: `user_data.json` stores progress and history in the app's user data directory (sandbox).
