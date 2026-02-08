# 🎓 S Quiz - Premium AI Learning Platform

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/kskreddy2k7/quiz-ai-app/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Play Store](https://img.shields.io/badge/Google_Play-Coming_Soon-orange.svg)](PLAY_STORE_LISTING_KIT.md)

> **Clean, fast, student-friendly AI learning platform** - Generate personalized quizzes in seconds, learn in your own language, get instant AI tutoring.

---

## 🌟 Overview

**S Quiz** is a comprehensive AI-powered learning platform that helps students learn faster with personalized quizzes. Featuring a clean, premium interface optimized for both web and mobile, S Quiz makes learning accessible and enjoyable for everyone.

✨ **New in v1.0:** Complete UX redesign, enhanced PWA support, professional branding, and production-ready distribution!

---

## ✨ Key Features

### 🎯 Smart Learning
- **AI Quiz Generator**: Create quizzes on ANY topic in seconds
- **Multi-Language Support**: Learn in 12+ languages (Hindi, Telugu, Tamil, Kannada, Malayalam, etc.)
- **File Upload**: Generate quizzes from your PDFs, DOCX, or TXT files
- **Smart Notes**: Create professional study guides automatically
- **AI Tutor**: 24/7 instant help with any question

### 🎨 Premium Experience
- **Clean Interface**: Distraction-free, student-friendly design
- **Collapsible Sidebar**: Icon-only navigation that expands on hover
- **Animated Feedback**: See AI progress step-by-step
- **Dark Theme**: Easy on the eyes for extended study sessions
- **Mobile Optimized**: Bottom navigation bar for easy thumb access

### 🔐 Secure & Flexible
- **Google Sign-In**: One-click authentication
- **Guest Mode**: Try without creating an account
- **Privacy First**: Files processed securely, never stored permanently
- **Offline Support**: PWA works without internet

---

## 🚀 Quick Start

### Option 1: Progressive Web App (Recommended)
1. Visit the [web app](https://quiz-ai-app-1.onrender.com) *(update with your URL)*
2. Tap "Install" or "Add to Home Screen"
3. Launch like a native app!

**Benefits:** Auto-updates, works offline, smaller size, no app store needed

### Option 2: Android APK
1. Download from [GitHub Releases](https://github.com/kskreddy2k7/quiz-ai-app/releases)
2. Install the APK on your Android device
3. Enjoy native app experience!

### Option 3: Use in Browser
Just visit the website - no installation required! All features work directly in your browser.

📖 **Detailed instructions:** See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)

---

## ✨ What's New in v1.0

### 🎨 Complete UX Redesign
- ✅ Clean, single-action home screen
- ✅ Collapsible sidebar (desktop) / bottom nav (mobile)
- ✅ Animated AI loading steps
- ✅ Smart quote system (login, results, daily motivation)
- ✅ Reduced visual clutter

### 🎯 Professional Branding
- ✅ Custom app icons (1024x1024 down to 144x144)
- ✅ Favicon and PWA icons
- ✅ Consistent purple theme
- ✅ Improved typography and spacing

### ⚡ Enhanced Performance
- ✅ Faster perceived AI responses
- ✅ Improved model fallback logic
- ✅ Better offline support
- ✅ Optimized animations

### 📦 Production Ready
- ✅ Enhanced PWA with offline caching
- ✅ APK/AAB auto-build via GitHub Actions
- ✅ Play Store listing kit
- ✅ GDPR/COPPA compliant privacy policy
- ✅ Comprehensive documentation

📄 **Full details:** See [TRANSFORMATION_SUMMARY.md](TRANSFORMATION_SUMMARY.md)

---

## 📝 Complete Feature List

### 🔐 Authentication
- Google Sign-In (OAuth 2.0)
- Traditional username/password
- Guest Mode
- Secure JWT token handling

### 📚 Quiz Generation
- Topic-based quizzes (1-50 questions)
- File upload support (PDF, DOCX, TXT)
- 3 difficulty levels (Easy, Medium, Hard)
- Detailed explanations for every answer
- Multi-language support (12+ languages)

### 👨‍🏫 Study Tools
- AI Tutor chatbot
- Smart notes generation (PDF/DOCX/PPTX)
- Lesson planning assistance
- Concept simplification

### 🌍 Languages Supported
English • Hindi (हिन्दी) • Telugu (తెలుగు) • Tamil (தமிழ்) • Kannada (ಕನ್ನಡ) • Malayalam (മലയാളം) • Marathi (मराठी) • Gujarati (ગુજરાતી) • Punjabi (ਪੰਜਾਬੀ) • Bengali (বাংলা) • Odia (ଓଡ଼ିଆ) • Urdu (اردو)

---

## 💻 Local Development

### 1. Requirements
- Python 3.10+
- Google Gemini API Key (free tier available)

### 1. Requirements
- Python 3.10+
- **FREE AI Options** (No credit card required):
  - Google Gemini API Key (Primary - Free tier available)
  - HuggingFace API Token (Secondary - Free tier available)
  - Cloudflare AI (Optional - Free tier available)
  - **Offline Mode** (Always available as fallback)
- Google OAuth Client ID (for Google Sign-In) - Optional but recommended

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory (copy from `.env.example`):
```bash
# AI Providers (All Free - No Credit Card Required)
# At least ONE is recommended, but app works without any (offline mode)
GEMINI_API_KEY=your-gemini-api-key-here
HUGGINGFACE_API_KEY=your-huggingface-token-here
CLOUDFLARE_API_KEY=your-cloudflare-api-key-here
CLOUDFLARE_ACCOUNT_ID=your-cloudflare-account-id

# Required for security
SECRET_KEY=your-secure-jwt-secret-key

# Optional (for Google Sign-In)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

#### Getting Free AI Keys:
- **Gemini**: https://makersuite.google.com/app/apikey (No credit card)
- **HuggingFace**: https://huggingface.co/settings/tokens (No credit card)
- **Cloudflare**: https://dash.cloudflare.com/ (No credit card)

**To enable Google Sign-In**, see [GOOGLE_AUTH_SETUP.md](GOOGLE_AUTH_SETUP.md) for detailed instructions.

### 4. Run Locally
```bash
python main_web.py
```
Open `http://localhost:8000` in your browser.

### 🤖 AI System Features
- **Multi-Provider Fallback**: Automatically switches between Gemini, Cloudflare, HuggingFace
- **Smart Caching**: Reuses previous AI responses for faster performance
- **Offline Mode**: Rule-based quiz generation when all providers are unavailable
- **Zero Downtime**: App never stops responding, even without API keys
- **Free Forever**: No payment required, no credit card needed

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

## 📂 Project Structure
```
S-Quiz/
├── .github/workflows/     # CI/CD pipelines
│   └── build-apk.yml     # Android build automation
├── api/                   # FastAPI endpoints
├── services/             # Business logic & AI
├── models/               # Database models
├── static/               # Frontend assets
│   ├── icon.svg         # App icon source
│   ├── icon-*.png       # Generated icons
│   ├── index.html       # Main app
│   ├── style.css        # Styling
│   └── script.js        # Frontend logic
├── main.py              # Android app (Kivy)
├── main_web.py          # Web server (FastAPI)
├── manifest.json        # PWA configuration
├── sw.js                # Service worker
├── buildozer.spec       # Android build config
└── Documentation/
    ├── INSTALLATION_GUIDE.md
    ├── PLAY_STORE_LISTING_KIT.md
    ├── PRIVACY_POLICY.md
    └── TRANSFORMATION_SUMMARY.md
```

---

## 🔐 Privacy & Security
- Files processed securely, never stored permanently
- GDPR and COPPA compliant
- No tracking, no ads, no data selling
- Full privacy policy: [PRIVACY_POLICY.md](PRIVACY_POLICY.md)

---

## 📚 Documentation

- **[Installation Guide](INSTALLATION_GUIDE.md)** - How to install on any platform
- **[Play Store Kit](PLAY_STORE_LISTING_KIT.md)** - Complete submission guide
- **[Privacy Policy](PRIVACY_POLICY.md)** - Privacy and data handling
- **[Transformation Summary](TRANSFORMATION_SUMMARY.md)** - Development journey
- **[Build Notes](build_notes.md)** - Android build instructions
- **[Google Auth Setup](GOOGLE_AUTH_SETUP.md)** - OAuth configuration

---

## 🤝 Contributing

We welcome contributions! Whether it's:
- 🐛 Bug reports
- 💡 Feature suggestions  
- 🌍 New language translations
- 📖 Documentation improvements
- 🎨 UI/UX enhancements

Please open an issue or submit a pull request!

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- **Google Gemini AI** for powering the quiz generation
- **Cloudflare Workers AI** for fallback AI support
- **Open source community** for amazing tools and libraries
- **Students everywhere** who inspired this project

---

## 📞 Support

- **GitHub Issues:** [Report a bug](https://github.com/kskreddy2k7/quiz-ai-app/issues)
- **Discussions:** [Ask questions](https://github.com/kskreddy2k7/quiz-ai-app/discussions)
- **Email:** [your-support-email] *(update with actual email)*

---

## 🌟 Star Us!

If you find S Quiz helpful, please consider giving it a ⭐ on GitHub! It helps others discover the project.

---

**Made with ❤️ for students everywhere**

*Learn faster. Study smarter. Succeed together.* 🚀📚

