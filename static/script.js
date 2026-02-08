// Configuration Constants
const CONFIG = {
    PWA_BANNER_DELAY: 5000,
    APK_MODAL_DELAY: 10000,
    PROMO_DELAY: 3000
};

// Motivational Quotes Pool
const QUOTES = [
    { text: "The beautiful thing about learning is that no one can take it away from you.", author: "B.B. King" },
    { text: "Education is the most powerful weapon which you can use to change the world.", author: "Nelson Mandela" },
    { text: "Live as if you were to die tomorrow. Learn as if you were to live forever.", author: "Mahatma Gandhi" },
    { text: "An investment in knowledge pays the best interest.", author: "Benjamin Franklin" },
    { text: "Learning never exhausts the mind.", author: "Leonardo da Vinci" }
];

const getRandomQuote = () => {
    const quote = QUOTES[Math.floor(Math.random() * QUOTES.length)];
    return quote;
};

// Utility functions
const utils = {
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    showLoadingSteps: (elementId, steps) => {
        const el = document.getElementById(elementId);
        if (!el) return;

        // Remove existing overlay if any
        const existing = el.querySelector('.loading-overlay');
        if (existing) existing.remove();

        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div style="text-align: center; width: 100%;">
                <div class="typing-indicator"><span></span><span></span><span></span></div>
                <div class="loading-steps">
                    ${steps.map((step, i) => `<div class="loading-step" data-step="${i}">○ ${step}</div>`).join('')}
                </div>
            </div>`;

        el.style.position = 'relative';
        el.appendChild(overlay);

        steps.forEach((_, i) => {
            setTimeout(() => {
                const stepEl = overlay.querySelector(`[data-step="${i}"]`);
                if (stepEl) {
                    stepEl.innerHTML = `● ${steps[i]}`;
                    stepEl.classList.add('active');
                }
            }, i * 800);
        });
    },

    showLoading: (elementId, message = 'Thinking...') => {
        const el = document.getElementById(elementId);
        if (!el) return;

        const existing = el.querySelector('.loading-overlay');
        if (existing) existing.remove();

        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div style="text-align: center;">
                <div class="typing-indicator"><span></span><span></span><span></span></div>
                <p style="margin-top: 15px; color: var(--primary); font-weight: 600;">${message}</p>
            </div>`;

        el.style.position = 'relative';
        el.appendChild(overlay);
    },

    hideLoading: (elementId) => {
        const el = document.getElementById(elementId);
        if (el) {
            const overlay = el.querySelector('.loading-overlay');
            if (overlay) overlay.remove();
        }
    },

    showNotification: (message, type = 'info') => {
        const toast = document.createElement('div');
        toast.className = `notification-toast toast-${type}`;

        let icon = 'info-circle';
        if (type === 'success') icon = 'check-circle';
        if (type === 'error') icon = 'exclamation-circle';

        toast.innerHTML = `<i class="bi bi-${icon}"></i> <span>${message}</span>`;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    fadeIn: (element, duration = 300) => {
        if (!element) return;
        element.style.opacity = '0';
        element.style.display = 'block';
        setTimeout(() => {
            element.style.transition = `opacity ${duration}ms ease`;
            element.style.opacity = '1';
        }, 10);
    }
};

const app = {
    state: {
        questions: [],
        currentQuestionIndex: 0,
        score: 0,
        user: { name: "Student", email: "", class: "", language: "English" },
        token: localStorage.getItem('token'),
        role: localStorage.getItem('role') || 'guest',
        language: localStorage.getItem('language') || 'English',
        onboardingStep: 1,
        uploadedFile: null,
        chatHistory: JSON.parse(localStorage.getItem('chatHistory') || '[]')
    },

    init: async () => {
        const hasSeenOnboarding = localStorage.getItem('onboarding_completed');
        const hasSeenPermissions = localStorage.getItem('permissions_accepted');

        if (!hasSeenOnboarding) app.showOnboarding();
        else if (!hasSeenPermissions) app.showPermissions();

        // Load saved user data
        const savedUser = JSON.parse(localStorage.getItem('userData') || '{}');
        app.state.user = { ...app.state.user, ...savedUser };

        app.updateUIForRole();
        app.updateTranslations();
        app.updateAuthQuote();

        if (app.state.token) {
            app.showTopic();
        } else if (hasSeenOnboarding && hasSeenPermissions) {
            app.showView('auth-view');
        }

        app.initPWA();
        app.detectAndroidDevice();
    },

    /* --- AUTH --- */
    switchAuthTab: (type) => {
        document.getElementById('login-container').style.display = type === 'login' ? 'block' : 'none';
        document.getElementById('signup-container').style.display = type === 'signup' ? 'block' : 'none';
        document.querySelectorAll('.auth-tab').forEach((t, i) => t.classList.toggle('active', (i === 0 && type === 'login') || (i === 1 && type === 'signup')));
    },

    togglePassword: (id, btn) => {
        const input = document.getElementById(id);
        const icon = btn.querySelector('i');
        const isSecret = input.type === 'password';
        input.type = isSecret ? 'text' : 'password';
        icon.className = isSecret ? 'bi bi-eye-slash' : 'bi bi-eye';
    },

    handleLogin: async () => {
        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value.trim();
        if (!email || !password) return utils.showNotification("Fields required", "error");

        try {
            utils.showLoading('auth-view', 'Authenticating...');
            const params = new URLSearchParams();
            params.append('username', email); // backend uses email as username
            params.append('password', password);

            const res = await fetch('/auth/token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: params
            });
            if (!res.ok) throw new Error("Invalid credentials");

            const data = await res.json();
            app.onAuthSuccess(data);
            utils.showNotification("Welcome back!", "success");
        } catch (e) {
            utils.showNotification(e.message, "error");
            app.showView('auth-view');
        }
    },

    handleSignup: async () => {
        const name = document.getElementById('signup-name').value.trim();
        const email = document.getElementById('signup-email').value.trim();
        const password = document.getElementById('signup-password').value.trim();
        if (!name || !email || !password) return utils.showNotification("All fields required", "error");

        try {
            utils.showLoading('auth-view', 'Creating account...');
            const res = await fetch('/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, full_name: name, username: email.split('@')[0] })
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Registration failed");
            }

            utils.showNotification("Account created! Logging in...", "success");
            const params = new URLSearchParams();
            params.append('username', email);
            params.append('password', password);
            const loginRes = await fetch('/auth/token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: params
            });
            if (loginRes.ok) app.onAuthSuccess(await loginRes.json());
        } catch (e) {
            utils.showNotification(e.message, "error");
            app.showView('auth-view');
        }
    },

    guestLogin: () => {
        app.onAuthSuccess({ access_token: "guest_token_placeholder", role: "guest", username: "Guest" });
        utils.showNotification("Guest mode active", "info");
    },

    googleLogin: () => {
        utils.showNotification("Google Sign-In coming soon!", "info");
    },

    onAuthSuccess: (data) => {
        app.state.token = data.access_token;
        app.state.role = data.role || (data.user ? data.user.role : 'user');
        app.state.user.name = data.username || (data.user ? data.user.full_name : "Student");

        localStorage.setItem('token', app.state.token);
        localStorage.setItem('role', app.state.role);
        localStorage.setItem('username', app.state.user.name);

        app.updateUIForRole();
        app.showTopic();
    },

    logout: () => {
        localStorage.clear();
        window.location.reload();
    },

    /* --- NAVIGATION --- */
    showView: (id) => {
        document.querySelectorAll('.screen').forEach(s => s.style.display = 'none');
        const view = document.getElementById(id);
        if (view) view.style.display = 'block';
    },

    showTopic: () => {
        app.showView('topic-view');
        app.setActiveFeature('btn-topic');
    },

    showUpload: () => {
        if (app.state.role === 'guest') return utils.showNotification("Members only", "error");
        app.showView('upload-view');
        app.setActiveFeature('btn-upload');
    },

    showTutor: () => {
        if (app.state.role === 'guest') return utils.showNotification("Members only", "error");
        app.showView('tutor-view');
        app.setActiveFeature('btn-tutor');
    },

    showNotes: () => {
        if (app.state.role === 'guest') return utils.showNotification("Members only", "error");
        app.showView('presentation-view');
        app.setActiveFeature('btn-notes');
    },

    setActiveFeature: (id) => {
        document.querySelectorAll('.feature-button').forEach(b => b.classList.remove('active'));
        const btn = document.getElementById(id);
        if (btn) btn.classList.add('active');
    },

    /* --- PROFILE --- */
    showProfile: () => {
        app.showView('profile-view');
        document.getElementById('profile-name-display').innerText = app.state.user.name;
        document.getElementById('profile-name-input').value = app.state.user.name;
        document.getElementById('profile-class-input').value = app.state.user.class || "";
        document.getElementById('profile-lang-select').value = app.state.language;
    },

    saveProfile: () => {
        app.state.user.name = document.getElementById('profile-name-input').value;
        app.state.user.class = document.getElementById('profile-class-input').value;
        app.state.language = document.getElementById('profile-lang-select').value;

        localStorage.setItem('userData', JSON.stringify(app.state.user));
        localStorage.setItem('language', app.state.language);
        localStorage.setItem('username', app.state.user.name);

        app.updateTranslations();
        app.updateUIForRole();
        utils.showNotification("Profile Saved", "success");
        app.showTopic();
    },

    /* --- ONBOARDING --- */
    showOnboarding: () => {
        document.getElementById('onboarding-modal').style.display = 'flex';
    },

    nextOnboarding: () => {
        const steps = document.querySelectorAll('.onboarding-step');
        const dots = document.querySelectorAll('.dot');
        if (app.state.onboardingStep < steps.length) {
            steps[app.state.onboardingStep - 1].classList.remove('active');
            dots[app.state.onboardingStep - 1].classList.remove('active');
            app.state.onboardingStep++;
            steps[app.state.onboardingStep - 1].classList.add('active');
            dots[app.state.onboardingStep - 1].classList.add('active');
            if (app.state.onboardingStep === steps.length) {
                document.querySelector('.onboarding-controls button').innerHTML = 'Finish <i class="bi bi-check"></i>';
            }
        } else {
            app.finishOnboarding();
        }
    },

    finishOnboarding: () => {
        document.getElementById('onboarding-modal').style.display = 'none';
        localStorage.setItem('onboarding_completed', 'true');
        app.showPermissions();
    },

    showPermissions: () => {
        document.getElementById('permission-modal').style.display = 'flex';
    },

    allowPermissions: () => {
        document.getElementById('permission-modal').style.display = 'none';
        localStorage.setItem('permissions_accepted', 'true');
        if (!app.state.token) app.showView('auth-view');
    },

    /* --- UI UPDATES --- */
    updateUIForRole: () => {
        const isGuest = app.state.role === 'guest';
        const pill = document.getElementById('user-pill-container');
        const logout = document.getElementById('btn-logout');
        const name = document.getElementById('nav-user-display');

        if (pill) pill.classList.toggle('hidden', isGuest);
        if (logout) logout.classList.toggle('hidden', isGuest);
        if (name) name.innerText = app.state.user.name;

        ['btn-upload', 'btn-notes', 'btn-tutor'].forEach(id => {
            const btn = document.getElementById(id);
            if (btn) btn.classList.toggle('disabled', isGuest);
        });
    },

    updateAuthQuote: () => {
        const q = getRandomQuote();
        const text = document.getElementById('auth-quote-text');
        const auth = document.getElementById('auth-quote-author');
        if (text) text.innerText = `"${q.text}"`;
        if (auth) auth.innerText = `— ${q.author}`;
    },

    updateTranslations: () => {
        const lang = app.state.language;
        if (typeof translations === 'undefined' || !translations[lang]) return;
        document.querySelectorAll('[id^="t-"]').forEach(el => {
            const key = el.id.replace('t-', '');
            if (translations[lang][key]) el.innerText = translations[lang][key];
        });
    },

    /* --- CORE FEATURES --- */
    generateTopicQuiz: async () => {
        const topic = document.getElementById('topic-input').value.trim();
        if (!topic) return utils.showNotification("Please enter a topic", "error");

        utils.showLoadingSteps('topic-view', ['Scanning Library', 'AI Brainstorming', 'Generating Quiz']);
        try {
            const res = await fetch('/quiz/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${app.state.token}` },
                body: JSON.stringify({
                    topic,
                    num_questions: parseInt(document.getElementById('q-count').value),
                    difficulty: document.getElementById('difficulty-select').value,
                    language: document.getElementById('language-select').value
                })
            });
            if (!res.ok) throw new Error("Our AI is currently busy. Please try again.");
            app.startQuiz(await res.json());
        } catch (e) {
            utils.showNotification(e.message, "error");
        } finally {
            utils.hideLoading('topic-view');
        }
    },

    startQuiz: (data) => {
        app.state.questions = data.questions;
        app.state.currentQuestionIndex = 0;
        app.state.score = 0;
        app.showView('quiz-view');
        app.renderQuestion();
    },

    renderQuestion: () => {
        const q = app.state.questions[app.state.currentQuestionIndex];
        const textEl = document.getElementById('question-text');
        if (textEl) textEl.innerText = q.question;

        const currentQEl = document.getElementById('current-q');
        if (currentQEl) currentQEl.innerText = app.state.onboardingStep + 1; // Wrong index, use:
        if (currentQEl) currentQEl.innerText = app.state.currentQuestionIndex + 1;

        const opts = document.getElementById('options-container');
        if (!opts) return;
        opts.innerHTML = '';

        q.options.forEach((opt, i) => {
            const btn = document.createElement('button');
            btn.className = 'btn btn-outline w-100 option-btn';
            btn.innerHTML = `<span>${String.fromCharCode(65 + i)}.</span> ${opt}`;
            btn.onclick = () => app.handleAnswer(opt, btn);
            opts.appendChild(btn);
        });

        const nextBtn = document.getElementById('btn-next-question');
        if (nextBtn) {
            nextBtn.classList.add('hidden');
            nextBtn.innerHTML = (app.state.currentQuestionIndex === app.state.questions.length - 1)
                ? 'Finish Quiz <i class="bi bi-check-circle"></i>'
                : 'Next Question <i class="bi bi-arrow-right"></i>';
        }

        const expBox = document.getElementById('explanation-box');
        if (expBox) expBox.style.display = 'none';
    },

    handleAnswer: (selected, btn) => {
        if (btn.parentElement.classList.contains('locked')) return;

        const q = app.state.questions[app.state.currentQuestionIndex];
        const isCorrect = selected === q.answer;

        btn.classList.add(isCorrect ? 'correct' : 'wrong');
        btn.parentElement.classList.add('locked');

        if (isCorrect) app.state.score++;

        const expText = document.getElementById('explanation-text');
        const expBox = document.getElementById('explanation-box');
        if (expText) expText.innerText = q.explanation;
        if (expBox) expBox.style.display = 'block';

        const nextBtn = document.getElementById('btn-next-question');
        if (nextBtn) nextBtn.classList.remove('hidden');
    },

    nextQuestion: () => {
        if (app.state.currentQuestionIndex < app.state.questions.length - 1) {
            app.state.currentQuestionIndex++;
            app.renderQuestion();
        } else {
            app.showResult();
        }
    },

    showResult: () => {
        app.showView('result-view');
        const pct = Math.round((app.state.score / app.state.questions.length) * 100);
        const scoreEl = document.getElementById('final-score');
        if (scoreEl) scoreEl.innerText = `${pct}%`;

        // Quote
        const q = getRandomQuote();
        const text = document.getElementById('result-quote-text');
        const auth = document.getElementById('result-quote-author');
        if (text) text.innerText = q.text;
        if (auth) auth.innerText = q.author;
    },

    /* --- TUTOR --- */
    sendTutorMessage: async () => {
        const input = document.getElementById('tutor-input');
        const msg = input.value.trim();
        if (!msg) return;

        const box = document.getElementById('tutor-history');
        const userDiv = document.createElement('div');
        userDiv.className = 'msg msg-user';
        userDiv.textContent = msg;
        box.appendChild(userDiv);
        input.value = '';

        try {
            const res = await fetch('/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${app.state.token}` },
                body: JSON.stringify({ message: msg, language: app.state.language, history: app.state.chatHistory.slice(-5) })
            });
            const data = await res.json();
            const botDiv = document.createElement('div');
            botDiv.className = 'msg msg-bot';
            botDiv.innerHTML = data.response.replace(/\n/g, '<br>');
            box.appendChild(botDiv);
            app.state.chatHistory.push({ role: 'user', content: msg }, { role: 'assistant', content: data.response });
            localStorage.setItem('chatHistory', JSON.stringify(app.state.chatHistory.slice(-20)));
        } catch (e) {
            utils.showNotification("Chat error");
        }
    },

    /* --- UTILS --- */
    initPWA: () => { console.log("PWA initialized"); },
    detectAndroidDevice: () => {
        const isAndroid = /Android/i.test(navigator.userAgent);
        if (isAndroid && !localStorage.getItem('apk_modal_dismissed')) {
            // Optional: app.showAPKModal();
        }
    },
    showDailyMotivation: () => { },
    getHeaders: () => ({ 'Content-Type': 'application/json', 'Authorization': `Bearer ${app.state.token}` }),

    shareQuiz: () => {
        const score = document.getElementById('final-score').innerText;
        const text = `I just scored ${score} on S Quiz! 🚀 Try it yourself: ${window.location.origin}`;
        if (navigator.share) {
            navigator.share({ title: 'S Quiz Result', text: text, url: window.location.origin });
        } else {
            navigator.clipboard.writeText(text);
            utils.showNotification("Result copied to clipboard!", "success");
        }
    }
};

function getRandomQuote() {
    const quotes = [
        { text: "The beautiful thing about learning is that no one can take it away from you.", author: "B.B. King" },
        { text: "Education is the most powerful weapon which you can use to change the world.", author: "Nelson Mandela" },
        { text: "Believe in yourself and all that you are.", author: "Christian D. Larson" },
        { text: "Success is not final, failure is not fatal: it is the courage to continue that counts.", author: "Winston Churchill" },
        { text: "Your talent is God's gift to you. What you do with it is your gift back to God.", author: "Leo Buscaglia" }
    ];
    return quotes[Math.floor(Math.random() * quotes.length)];
}

app.init();
