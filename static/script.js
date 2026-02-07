const app = {
    state: {
        questions: [],
        currentQuestionIndex: 0,
        score: 0,
        user: { name: "Student", level: 1 },
        uploadedFile: null,
        chatHistory: [],
        token: null,
        language: "English" // Default Language
    },

    init: async () => {
        // 1. Load Language Preference
        const createOption = (text, val) => {
            const opt = document.createElement('option');
            opt.value = val;
            opt.innerText = text;
            return opt;
        };
        const langSelect = document.getElementById('language-select');
        if (langSelect) {
            // Ensure options exist if not in HTML (HTML has them, but safety check)
        }

        const savedLang = localStorage.getItem('language') || "English";
        app.state.language = savedLang;
        if (document.getElementById('language-select')) {
            document.getElementById('language-select').value = savedLang;
        }
        app.updateTranslations();

        // 2. Check for Token
        const token = localStorage.getItem('token');
        if (token) {
            app.state.token = token;
            app.state.user.name = localStorage.getItem('username') || "Student";

            const userDisplay = document.getElementById('user-display');
            if (userDisplay) userDisplay.innerText = app.state.user.name;

            // Load Chat History
            const savedChat = localStorage.getItem('chatHistory');
            if (savedChat) {
                try {
                    app.state.chatHistory = JSON.parse(savedChat);
                    const historyContainer = document.getElementById('tutor-history');
                    if (historyContainer) {
                        // Clear non-system messages first to avoid duplicates if re-init
                        // Actually, just append new ones if we were robust, but simple redraw is safer
                        // For now, let's just keep the welcome message and append.
                        app.state.chatHistory.forEach(msg => {
                            if (msg.role !== 'system') {
                                const type = msg.role === 'user' ? 'msg-user' : 'msg-bot';
                                const div = document.createElement('div');
                                div.className = `msg ${type}`;
                                div.innerHTML = msg.content.replace(/\n/g, '<br>');
                                historyContainer.appendChild(div);
                            }
                        });
                        historyContainer.scrollTop = historyContainer.scrollHeight;
                    }
                } catch (e) { console.error("Chat load error", e); }
            }

            app.showSetup();
        } else {
            app.showAuth();
        }

        // 3. Mobile Promo Check
        const isMobile = window.innerWidth <= 768;
        const isWebView = navigator.userAgent.includes('wv');
        if (isMobile && !isWebView && !localStorage.getItem('promoDismissed')) {
            setTimeout(() => {
                const promo = document.getElementById('app-promo');
                if (promo) promo.style.display = 'block';
            }, 3000);
        }
    },

    /* --- I18N SYSTEM --- */
    setLanguage: (lang) => {
        app.state.language = lang;
        localStorage.setItem('language', lang);
        app.updateTranslations();
        // Optional: Notify backend to update user profile if exists
    },

    updateTranslations: () => {
        const lang = app.state.language;
        if (!translations[lang]) return; // Safety

        // Update all elements with id starting with "t-"
        // We use a mapping from the HTML ID to the translation key.
        // Convention: HTML id="t-key_name" matches translations[lang]["key_name"]

        const elements = document.querySelectorAll('[id^="t-"]');
        elements.forEach(el => {
            const key = el.id.replace('t-', '');
            if (translations[lang][key]) {
                el.innerText = translations[lang][key];
            }
        });

        // Update Placeholders
        const topicInput = document.getElementById('topic-input');
        if (topicInput) topicInput.placeholder = translations[lang]["placeholder_topic"];

        const authInput = document.getElementById('username-input');
        if (authInput) authInput.placeholder = translations[lang]["placeholder_auth"];

        const askInput = document.getElementById('tutor-input');
        if (askInput) askInput.placeholder = translations[lang]["placeholder_ask"];

        // Update Dynamic Texts (like File Label)
        if (!app.state.uploadedFile) {
            const fileLabel = document.getElementById('file-label-text'); // Corrected ID from HTML
            if (fileLabel) fileLabel.innerText = translations[lang]["file_label"];
        }
    },

    // Helper to update dynamic texts that aren't static IDs
    t: (key) => {
        const lang = app.state.language;
        return (translations[lang] && translations[lang][key]) ? translations[lang][key] : key;
    },

    /* --- API HELPERS --- */
    getHeaders: () => {
        const headers = { 'Content-Type': 'application/json' };
        if (app.state.token) headers['Authorization'] = `Bearer ${app.state.token}`;
        return headers;
    },
    getAuthHeaders: () => {
        const headers = {};
        if (app.state.token) headers['Authorization'] = `Bearer ${app.state.token}`;
        return headers;
    },

    /* --- NAVIGATION --- */
    showView: (viewId) => {
        document.querySelectorAll('.screen').forEach(el => el.style.display = 'none');
        document.getElementById(viewId).style.display = 'block';

        // Sidebar active state
        document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
        // We can't easily map click to ID without data attributes, 
        // ignoring visual active state update for brevity or adding logic later if needed.
    },

    showAuth: () => {
        document.getElementById('app-container').style.display = 'none';
        document.getElementById('auth-view').style.display = 'block';
    },

    showSetup: () => {
        document.getElementById('auth-view').style.display = 'none';
        document.getElementById('app-container').style.display = 'block';
        app.showView('setup-view');
        app.state.uploadedFile = null;
    },

    showLibrary: async () => {
        app.showView('library-view');
        const list = document.getElementById('library-list');
        list.innerHTML = '<div class="spinner" style="border-color:var(--primary); border-top-color:transparent; margin: 20px auto"></div>';

        try {
            const res = await fetch('/library', { headers: app.getHeaders() });
            const items = await res.json();
            list.innerHTML = '';

            if (items.length === 0) {
                list.innerHTML = `<p class="text-muted" style="text-align:center">Empty Library.</p>`;
                return;
            }

            items.forEach(item => {
                const card = document.createElement('div');
                card.className = 'card';
                card.style.padding = '20px';
                card.innerHTML = `
                    <div style="font-weight:600; margin-bottom:5px; font-size:1.1rem">📄 ${item.filename}</div>
                    <div style="font-size:0.95rem; color:var(--text-muted); margin-bottom:15px; line-height:1.5">${item.summary || '...'}</div>
                    <button class="btn btn-outline" style="width:auto; font-size:0.85rem">Chat / Quiz</button>
                `;
                list.appendChild(card);
            });
        } catch (e) {
            list.innerHTML = '<p style="color:var(--error); text-align:center">Error loading library.</p>';
        }
    },

    showTutor: () => {
        app.showView('tutor-view');
    },

    showPresentation: () => {
        app.showView('presentation-view');
    },

    logout: () => {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        app.state.token = null;
        window.location.reload();
    },

    /* --- AUTH --- */
    login: async () => {
        const username = document.getElementById('username-input').value;
        const password = document.getElementById('password-input').value;

        if (!username || !password) {
            alert("Please enter credentials");
            return;
        }

        try {
            // Auto Register
            if (username.length > 3) {
                const regBody = { username, password };
                if (username.includes('@')) regBody.email = username;

                try {
                    await fetch('/auth/register', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(regBody)
                    });
                } catch (e) { }
            }

            // Login
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const res = await fetch('/auth/token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            if (!res.ok) throw new Error("Invalid credentials");
            const data = await res.json();

            app.state.token = data.access_token;
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('username', username);
            app.state.user.name = username;

            document.getElementById('user-display').innerText = username;
            app.showSetup();

        } catch (e) {
            alert(e.message);
        }
    },

    /* --- QUIZ FEATURE --- */
    handleFileSelect: (input) => {
        if (input.files && input.files[0]) {
            app.state.uploadedFile = input.files[0];
            const label = document.getElementById('file-label-text') || document.getElementById('file-label'); // Handle both ID cases if distinct
            if (label) label.innerText = `✅ ${input.files[0].name}`;
        }
    },

    generateQuiz: async () => {
        const topic = document.getElementById('topic-input').value;
        const numQ = document.getElementById('q-count').value;
        const diff = document.getElementById('difficulty-select').value;
        // mastery-select might not be in the new HTML, let's check
        // We removed it in favor of simplicity? No, let's keep it if logic exists, but default if null.
        const masteryEl = document.getElementById('mastery-select');
        const mastery = masteryEl ? masteryEl.value : "Intermediate";

        if (!topic && !app.state.uploadedFile) return alert(app.t("placeholder_topic"));

        document.getElementById('loading').style.display = 'block';

        try {
            let res;
            if (app.state.uploadedFile) {
                const fd = new FormData();
                fd.append('file', app.state.uploadedFile);
                fd.append('num_questions', numQ);
                fd.append('difficulty', diff);
                fd.append('mastery_level', mastery);
                fd.append('language', app.state.language); // NEW

                // Upload
                await fetch('/library/upload', { method: 'POST', headers: app.getAuthHeaders(), body: fd });
                // Generate
                res = await fetch('/quiz/generate-from-file', { method: 'POST', headers: app.getAuthHeaders(), body: fd });

            } else {
                res = await fetch('/quiz/generate', {
                    method: 'POST',
                    headers: app.getHeaders(),
                    body: JSON.stringify({
                        topic,
                        num_questions: parseInt(numQ),
                        difficulty: diff,
                        mastery_level: mastery,
                        language: app.state.language // NEW
                    })
                });
            }

            if (!res.ok) throw new Error("Failed to generate");
            const data = await res.json();

            app.state.questions = data.questions;
            app.state.currentQuestionIndex = 0;
            app.state.score = 0;
            app.showQuiz();

        } catch (e) {
            alert("Error: " + e.message);
        } finally {
            document.getElementById('loading').style.display = 'none';
        }
    },

    showQuiz: () => {
        app.showView('quiz-view');
        app.renderQuestion();
    },

    renderQuestion: () => {
        const q = app.state.questions[app.state.currentQuestionIndex];
        document.getElementById('quiz-topic-display').innerText = q.topic || "Quiz";
        document.getElementById('current-q').innerText = app.state.currentQuestionIndex + 1;
        document.getElementById('total-q').innerText = app.state.questions.length;
        document.getElementById('question-text').innerText = q.prompt;

        const con = document.getElementById('options-container');
        con.innerHTML = '';
        document.getElementById('explanation-box').style.display = 'none';

        q.choices.forEach(opt => {
            const div = document.createElement('div');
            div.className = 'option-card';
            div.innerText = opt;
            div.onclick = () => app.checkAnswer(opt, div);
            con.appendChild(div);
        });
    },

    checkAnswer: (selected, el) => {
        const q = app.state.questions[app.state.currentQuestionIndex];
        const opts = document.querySelectorAll('.option-card');
        opts.forEach(o => o.onclick = null);

        if (selected == q.answer) {
            el.classList.add('correct');
            app.state.score++;
        } else {
            el.classList.add('wrong');
            opts.forEach(o => { if (o.innerText == q.answer) o.classList.add('correct'); });
        }

        document.getElementById('explanation-text').innerText = q.explanation;
        document.getElementById('explanation-box').style.display = 'block';
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
        const score = Math.round((app.state.score / app.state.questions.length) * 100);
        document.getElementById('final-score').innerText = `${score}%`;
    },

    shareQuiz: () => {
        // Placeholder for share logic
        alert("Link copied to clipboard! (Simulated)");
    },

    /* --- TUTOR --- */
    sendTutorMessage: async () => {
        const input = document.getElementById('tutor-input');
        const msg = input.value.trim();
        if (!msg) return;

        const box = document.getElementById('tutor-history');
        box.innerHTML += `<div class="msg msg-user">${msg}</div>`;
        input.value = '';
        box.scrollTop = box.scrollHeight;

        try {
            const res = await fetch('/ai/chat', {
                method: 'POST',
                headers: app.getHeaders(),
                body: JSON.stringify({
                    message: msg,
                    history: app.state.chatHistory,
                    language: app.state.language // NEW
                })
            });
            const data = await res.json();
            box.innerHTML += `<div class="msg msg-bot">${data.response.replace(/\n/g, '<br>')}</div>`;
            box.scrollTop = box.scrollHeight;

            app.state.chatHistory.push({ role: 'user', content: msg });
            app.state.chatHistory.push({ role: 'assistant', content: data.response });
            localStorage.setItem('chatHistory', JSON.stringify(app.state.chatHistory));

        } catch (e) {
            box.innerHTML += `<div class="msg msg-bot" style="color:var(--error)">Error: ${e.message}</div>`;
        }
    },

    /* --- PRESENTATION --- */
    generatePPT: async () => {
        const topic = document.getElementById('ppt-topic').value;
        const slides = document.getElementById('ppt-slides').value;

        if (!topic) return alert(app.t("placeholder_topic"));

        document.getElementById('ppt-loading').style.display = 'block';

        try {
            const res = await fetch('/presentation/generate', {
                method: 'POST',
                headers: app.getHeaders(),
                body: JSON.stringify({
                    topic,
                    num_slides: parseInt(slides),
                    language: app.state.language
                })
            });

            if (!res.ok) throw new Error("Generation Failed");

            // Handle File Download
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `${topic}_Presentation.pptx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);

            alert(app.state.language === "Hindi" ? "प्रेजेंटेशन डाउनलोड हो गया!" : "Presentation Downloaded!");

        } catch (e) {
            alert("Error: " + e.message);
        } finally {
            document.getElementById('ppt-loading').style.display = 'none';
        }
    }
};

// Start
app.init();
