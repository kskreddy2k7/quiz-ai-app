// --- CONFIGURATION ---
const API_BASE_URL = ""; // Use relative path since backend serves frontend
const CONFIG = {
    MOCK_DELAY: 800,
    TOAST_DURATION: 3000
};

// --- QUOTES POOL ---
const QUOTES = [
    { text: "The beautiful thing about learning is that no one can take it away from you.", author: "B.B. King" },
    { text: "Education is the most powerful weapon which you can use to change the world.", author: "Nelson Mandela" },
    { text: "Live as if you were to die tomorrow. Learn as if you were to live forever.", author: "Mahatma Gandhi" },
    { text: "An investment in knowledge pays the best interest.", author: "Benjamin Franklin" },
    { text: "Learning never exhausts the mind.", author: "Leonardo da Vinci" },
    { text: "I have no special talent. I am only passionately curious.", author: "Albert Einstein" }
];

// --- UTILITIES ---
const utils = {
    // Show a toast notification
    showNotification: (message, type = 'info') => {
        // Remove existing toasts first to prevent stacking
        const existing = document.querySelector('.notification-toast');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = `notification-toast toast-${type}`;

        // Icon selection
        let icon = 'info-circle';
        if (type === 'success') icon = 'check-circle';
        if (type === 'error') icon = 'exclamation-triangle';

        toast.innerHTML = `<i class="bi bi-${icon}"></i> <span>${message}</span>`;
        document.body.appendChild(toast);

        // Auto remove
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, CONFIG.TOAST_DURATION);
    },

    // Show loading overlay
    showLoading: (containerId, message = 'Processing...') => {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Check if already loading
        if (container.querySelector('.loading-overlay')) return;

        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.style.cssText = `
            position: absolute; inset: 0; background: rgba(15,23,42,0.7); 
            backdrop-filter: blur(5px); display: flex; flex-direction: column;
            align-items: center; justify-content: center; z-index: 50; border-radius: inherit;
        `;
        overlay.innerHTML = `
            <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p style="margin-top: 15px; font-weight: 600; color: white;">${message}</p>
        `;

        // Ensure container is relative for absolute positioning of overlay
        if (getComputedStyle(container).position === 'static') {
            container.style.position = 'relative';
        }

        container.appendChild(overlay);
    },

    // Hide loading overlay
    hideLoading: (containerId) => {
        const container = document.getElementById(containerId);
        if (!container) return;
        const overlay = container.querySelector('.loading-overlay');
        if (overlay) overlay.remove();
    },

    getRandomQuote: () => QUOTES[Math.floor(Math.random() * QUOTES.length)]
};

// --- APPLICATION LOGIC ---
const app = {
    state: {
        user: null,
        token: localStorage.getItem('token'),
        role: localStorage.getItem('role') || 'guest'
    },

    init: () => {
        console.log("App Initializing...");

        // 1. Setup global event listeners
        app.setupEventListeners();

        // 2. Check Auth State
        if (app.state.token) {
            app.fetchUserProfile();
        } else {
            app.showAuth();
        }

        // 3. Random Quote for Auth Screen
        const quote = utils.getRandomQuote();
        // If we had a quote element on auth screen, we'd update it here
    },

    setupEventListeners: () => {
        // Auth Tab Switching
        document.querySelectorAll('.auth-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const mode = e.target.textContent.trim().toLowerCase().includes('sign') ? 'signup' : 'login';
                app.switchAuthTab(mode);
            });
        });
    },

    // --- NAVIGATION ---
    showAuth: () => {
        document.getElementById('auth-view').style.display = 'flex';
        document.getElementById('app-container').style.display = 'none';
        document.querySelector('.navbar-compact').style.display = 'none';
    },

    showDashboard: () => {
        document.getElementById('auth-view').style.display = 'none';
        document.getElementById('app-container').style.display = 'block';
        document.querySelector('.navbar-compact').style.display = 'flex';

        // Default View
        app.showView('dashboard-view');
        app.updateActiveNav('btn-dashboard');
    },

    showView: (viewId) => {
        // Close any open modals first
        document.querySelectorAll('.modal-overlay').forEach(modal => modal.remove());

        // Hide all screens
        document.querySelectorAll('.screen').forEach(el => el.style.display = 'none');

        // Show target screen
        const target = document.getElementById(viewId);
        if (target) {
            target.style.display = 'block';
            window.scrollTo(0, 0);
        } else {
            console.error(`View not found: ${viewId}`);
        }
    },

    updateActiveNav: (btnId) => {
        document.querySelectorAll('.feature-button').forEach(b => b.classList.remove('active'));
        const btn = document.getElementById(btnId);
        if (btn) btn.classList.add('active');
    },

    // --- AUTH ACTIONS ---
    switchAuthTab: (mode) => {
        document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));

        if (mode === 'login') {
            document.querySelector('.auth-tab:first-child').classList.add('active');
            document.getElementById('login-container').style.display = 'block';
            document.getElementById('signup-container').style.display = 'none';
        } else {
            document.querySelector('.auth-tab:last-child').classList.add('active');
            document.getElementById('login-container').style.display = 'none';
            document.getElementById('signup-container').style.display = 'block';
        }
    },

    togglePassword: (inputId, btn) => {
        const input = document.getElementById(inputId);
        const icon = btn.querySelector('i');
        if (input.type === 'password') {
            input.type = 'text';
            icon.className = 'bi bi-eye-slash';
        } else {
            input.type = 'password';
            icon.className = 'bi bi-eye';
        }
    },

    previewSignupAvatar: (input) => {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = (e) => {
                document.getElementById('signup-avatar-preview').src = e.target.result;
            };
            reader.readAsDataURL(input.files[0]);
        }
    },

    handleLogin: async () => {
        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value.trim();

        if (!email || !password) return utils.showNotification("Please fill in all fields", "error");

        utils.showLoading('auth-view', 'Logging in...');

        try {
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);

            const res = await fetch(`${API_BASE_URL}/auth/token`, {
                method: 'POST',
                body: formData
            });

            if (!res.ok) throw new Error("Invalid credentials");

            const data = await res.json();
            localStorage.setItem('token', data.access_token);
            app.state.token = data.access_token;

            await app.fetchUserProfile();
            utils.showNotification("Welcome back!", "success");

        } catch (err) {
            utils.showNotification(err.message, "error");
        } finally {
            utils.hideLoading('auth-view');
        }
    },

    handleSignup: async () => {
        const name = document.getElementById('signup-name').value.trim();
        const email = document.getElementById('signup-email').value.trim();
        const password = document.getElementById('signup-password').value.trim();
        // const avatarInput = document.getElementById('signup-avatar');

        if (!name || !email || !password) return utils.showNotification("All fields required", "error");

        utils.showLoading('auth-view', 'Creating account...');

        try {
            // 1. Signup
            const signupRes = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, full_name: name, username: email.split('@')[0] })
            });

            if (!signupRes.ok) {
                const errData = await signupRes.json();
                throw new Error(errData.detail || "Signup failed. Email might be taken.");
            }

            // 2. Auto Login
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);

            const loginRes = await fetch(`${API_BASE_URL}/auth/token`, { method: 'POST', body: formData });
            if (!loginRes.ok) throw new Error("Auto-login failed");

            const loginData = await loginRes.json();
            localStorage.setItem('token', loginData.access_token);
            app.state.token = loginData.access_token;

            // 3. Avatar Upload Removed
            // if (avatarInput && avatarInput.files[0]) { ... }

            await app.fetchUserProfile();
            utils.showNotification("Account created!", "success");

        } catch (err) {
            utils.showNotification(err.message, "error");
        } finally {
            utils.hideLoading('auth-view');
        }
    },

    guestLogin: () => {
        app.state.role = 'guest';
        app.state.user = {
            full_name: 'Guest User',
            email: 'guest@example.com',
            profile_photo: '/static/default-avatar.png'
        };
        app.updateUI(app.state.user);
        app.showDashboard();
        utils.showNotification("Guest Mode Active", "warning");
    },

    logout: () => {
        localStorage.removeItem('token');
        window.location.reload();
    },

    // --- DATA FETCHING ---
    fetchUserProfile: async () => {
        if (!app.state.token) return;

        try {
            const res = await fetch(`${API_BASE_URL}/users/me`, {
                headers: { 'Authorization': `Bearer ${app.state.token}` }
            });

            if (res.ok) {
                const user = await res.json();
                app.state.user = user;
                app.updateUI(user);
                app.showDashboard();
            } else {
                // Token invalid
                app.logout();
            }
        } catch (err) {
            console.error(err);
            utils.showNotification("Connection error", "error");
        }
    },

    updateUI: (user) => {
        // Nav
        const avatar = user.profile_photo || '/static/default-avatar.png';
        const firstName = user.full_name?.split(' ')[0] || 'User';

        // Update all avatar instances
        document.querySelectorAll('#nav-user-avatar, #dashboard-avatar, #profile-avatar-display').forEach(img => {
            img.src = avatar;
        });

        // Text updates
        document.getElementById('nav-user-display').textContent = firstName;
        document.getElementById('dashboard-welcome').textContent = `Welcome back, ${firstName}! 👋`;
        document.getElementById('dashboard-quote').textContent = `"${utils.getRandomQuote().text}"`;

        // Profile Inputs
        document.getElementById('profile-name-display').textContent = user.full_name;
        document.getElementById('profile-email-display').textContent = user.email;

        // Stats
        document.getElementById('stat-quizzes').textContent = user.quizzes_taken || 0;
        document.getElementById('stat-score').textContent = (user.avg_score || 0) + '%';
        document.getElementById('stat-streak').textContent = (user.streak_count || 0) + ' Days';

        // Feature Locking for Guests
        const isGuest = app.state.role === 'guest';
        // Logic to gray out buttons could go here
    },

    // --- FEATURE NAVIGATION HANDLERS ---
    showTopic: () => { app.showView('topic-view'); app.updateActiveNav('btn-topic'); },
    showUpload: () => { app.showView('upload-view'); app.updateActiveNav('btn-upload'); },
    showNotes: () => { app.showView('presentation-view'); app.updateActiveNav('btn-notes'); },
    showTutor: () => { app.showView('tutor-view'); app.updateActiveNav('btn-tutor'); },

    showProfile: () => {
        app.showView('profile-view');
        // Pre-fill
        if (app.state.user) {
            document.getElementById('profile-name-input').value = app.state.user.full_name || '';
            document.getElementById('profile-class-input').value = app.state.user.current_class || '';
            document.getElementById('profile-lang-select').value = app.state.user.preferred_language || 'English';
        }
    },

    // --- PROFILE ACTIONS ---
    uploadProfilePicture: async (input) => {
        if (!input.files || !input.files[0]) return;

        utils.showLoading('profile-view', 'Uploading...');

        try {
            const formData = new FormData();
            formData.append('file', input.files[0]);

            const res = await fetch(`${API_BASE_URL}/users/me/avatar`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${app.state.token}` },
                body: formData
            });

            if (!res.ok) throw new Error("Upload failed");

            // Refresh Profile
            await app.fetchUserProfile();
            utils.showNotification("Avatar updated!", "success");

        } catch (err) {
            utils.showNotification(err.message, "error");
        } finally {
            utils.hideLoading('profile-view');
        }
    },

    saveProfile: async () => {
        const name = document.getElementById('profile-name-input').value;
        const currentClass = document.getElementById('profile-class-input').value;
        const lang = document.getElementById('profile-lang-select').value;

        utils.showLoading('profile-view', 'Saving...');

        try {
            const res = await fetch(`${API_BASE_URL}/users/me`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${app.state.token}`
                },
                body: JSON.stringify({
                    full_name: name,
                    current_class: currentClass,
                    preferred_language: lang
                })
            });

            if (!res.ok) throw new Error("Update failed");

            await app.fetchUserProfile();
            utils.showNotification("Profile saved!", "success");

            // Return to dashboard
            setTimeout(() => app.showDashboard(), 500);

        } catch (err) {
            utils.showNotification(err.message, "error");
        } finally {
            utils.hideLoading('profile-view');
        }
    },

    // --- QUIZ GENERATION & HANDLING ---

    generateTopicQuiz: async () => {
        const topic = document.getElementById('topic-input').value.trim();
        const count = parseInt(document.getElementById('q-count').value);
        const difficulty = document.getElementById('difficulty-select').value;
        const language = document.getElementById('language-select').value;
        const type = document.getElementById('type-select').value;

        if (!topic) return utils.showNotification("Please enter a topic", "error");

        utils.showLoading('topic-view', 'Generating Quiz with AI...');

        try {
            const res = await fetch(`${API_BASE_URL}/generate_topic`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${app.state.token}`
                },
                body: JSON.stringify({
                    topic,
                    num_questions: count,
                    difficulty,
                    language,
                    question_type: type
                })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Generation failed");
            }

            const data = await res.json();
            app.startQuiz(data.questions, topic);

        } catch (err) {
            console.error(err);
            utils.showNotification(err.message || "Failed to generate quiz", "error");
        } finally {
            utils.hideLoading('topic-view');
        }
    },

    handleFileSelect: (input) => {
        if (input.files && input.files[0]) {
            document.getElementById('file-label-text').textContent = input.files[0].name;
        }
    },

    generateFileQuiz: async () => {
        const input = document.getElementById('file-upload');
        if (!input.files || !input.files[0]) return utils.showNotification("Please select a file", "error");

        const count = parseInt(document.getElementById('file-q-count').value);
        const difficulty = document.getElementById('file-difficulty-select').value;

        utils.showLoading('upload-view', 'Analyzing file & generating quiz...');

        try {
            const formData = new FormData();
            formData.append('file', input.files[0]);
            formData.append('num_questions', count);
            formData.append('difficulty', difficulty);

            const res = await fetch(`${API_BASE_URL}/generate_file`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${app.state.token}` },
                body: formData
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "File processing failed");
            }

            const data = await res.json();
            app.startQuiz(data.questions, `File: ${data.filename}`);

        } catch (err) {
            console.error(err);
            utils.showNotification(err.message, "error");
        } finally {
            utils.hideLoading('upload-view');
        }
    },

    // --- QUIZ GAMEPLAY ---

    currentQuiz: {
        questions: [],
        currentIndex: 0,
        score: 0,
        topic: ''
    },

    startQuiz: (questions, topic) => {
        if (!questions || questions.length === 0) {
            return utils.showNotification("No questions generated. Try again.", "error");
        }

        app.currentQuiz = {
            questions: questions,
            currentIndex: 0,
            score: 0,
            topic: topic,
            userAnswers: new Array(questions.length).fill(null)
        };

        app.showView('quiz-view');
        document.getElementById('quiz-topic-display').textContent = topic;
        app.showQuestion();
    },

    showQuestion: () => {
        const q = app.currentQuiz.questions[app.currentQuiz.currentIndex];
        document.getElementById('current-q').textContent = app.currentQuiz.currentIndex + 1;
        document.getElementById('question-text').textContent = q.prompt;

        const container = document.getElementById('options-container');
        container.innerHTML = '';
        document.getElementById('explanation-box').style.display = 'none';
        document.getElementById('btn-next-question').classList.add('hidden');

        q.choices.forEach((choice, index) => {
            const btn = document.createElement('div');
            btn.className = 'quiz-option';
            btn.textContent = choice;
            btn.onclick = () => app.handleAnswer(btn, choice, q);
            container.appendChild(btn);
        });
    },

    handleAnswer: (btnElement, choice, question) => {
        // Prevent multiple answers
        if (document.querySelector('.quiz-option.correct') || document.querySelector('.quiz-option.wrong')) return;

        const isCorrect = choice === question.answer;

        if (isCorrect) {
            btnElement.classList.add('correct');
            app.currentQuiz.score++;
            utils.showNotification("Correct! 🎉", "success");
        } else {
            btnElement.classList.add('wrong');
            utils.showNotification("Incorrect", "error");

            // Highlight correct answer
            document.querySelectorAll('.quiz-option').forEach(opt => {
                if (opt.textContent === question.answer) opt.classList.add('correct');
            });
        }

        // Show explanation
        const expBox = document.getElementById('explanation-box');
        const expText = document.getElementById('explanation-text');
        expBox.style.display = 'block';
        expText.textContent = isCorrect ? question.explanation : (question.explanation || "No explanation available.");

        document.getElementById('btn-next-question').classList.remove('hidden');
    },

    nextQuestion: () => {
        app.currentQuiz.currentIndex++;
        if (app.currentQuiz.currentIndex < app.currentQuiz.questions.length) {
            app.showQuestion();
        } else {
            app.showResult();
        }
    },

    showResult: () => {
        app.showView('result-view');
        const percentage = Math.round((app.currentQuiz.score / app.currentQuiz.questions.length) * 100);
        document.getElementById('final-score').textContent = `${percentage}%`;

        // Create Action Buttons Container if not exists
        let actionContainer = document.getElementById('result-actions');
        if (!actionContainer) {
            actionContainer = document.createElement('div');
            actionContainer.id = 'result-actions';
            actionContainer.style.marginTop = '20px';
            actionContainer.style.display = 'flex';
            actionContainer.style.gap = '10px';
            actionContainer.style.justifyContent = 'center';
            document.querySelector('#result-view .card-premium').appendChild(actionContainer);
        }

        actionContainer.innerHTML = `
            <button class="btn-primary-small" onclick="app.restartQuiz()">Re-attempt 🔄</button>
            <button class="btn-primary-small" style="background: rgba(255,255,255,0.1);" onclick="app.reviewQuiz()">Review 📝</button>
        `;

        // Save score if logged in
        if (app.state.token) {
            // Logic to save score to backend could go here
            // fetch(`${API_BASE_URL}/users/me/stats`, ...)
        }
    },

    restartQuiz: () => {
        app.startQuiz(app.currentQuiz.questions, app.currentQuiz.topic);
    },

    reviewQuiz: () => {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.style.display = 'flex';

        let content = `<div class="glass-card" style="max-width: 800px; max-height: 90vh; overflow-y: auto; text-align: left;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                <h2 class="indigo-text" style="margin:0;">Quiz Review</h2>
                <div class="score-badge">${Math.round((app.currentQuiz.score / app.currentQuiz.questions.length) * 100)}%</div>
            </div>`;

        app.currentQuiz.questions.forEach((q, i) => {
            const uAns = app.currentQuiz.userAnswers[i];
            const cAns = q.correct_answers || q.answer;

            // Format Display
            const uStr = Array.isArray(uAns) ? uAns.join(", ") : (uAns || "Skipped");
            const cStr = Array.isArray(cAns) ? cAns.join(", ") : cAns;

            // Check Correctness
            let isCorrect = false;
            if (Array.isArray(cAns)) {
                if (Array.isArray(uAns) && uAns.length === cAns.length && uAns.every(val => cAns.includes(val))) isCorrect = true;
            } else {
                if (uAns === cAns) isCorrect = true;
            }

            const statusColor = isCorrect ? 'var(--success)' : 'var(--error)';
            const statusIcon = isCorrect ? '<i class="bi bi-check-circle-fill"></i>' : '<i class="bi bi-x-circle-fill"></i>';

            content += `
                <div style="margin-bottom: 20px; padding: 20px; background: rgba(255,255,255,0.03); border-radius: 12px; border-left: 4px solid ${statusColor};">
                    <p style="font-weight: 600; margin-bottom: 12px; font-size: 1.1rem;">
                        <span style="opacity:0.6; margin-right:8px;">Q${i + 1}.</span> ${q.prompt}
                    </p>
                    
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px; font-size: 0.95rem;">
                        <div style="padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px;">
                            <span style="display:block; font-size:0.8rem; opacity:0.7; margin-bottom:4px;">Your Answer</span>
                            <span style="color: ${statusColor}; font-weight: 500;">${uStr} ${statusIcon}</span>
                        </div>
                        <div style="padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px;">
                            <span style="display:block; font-size:0.8rem; opacity:0.7; margin-bottom:4px;">Correct Answer</span>
                            <span style="color: var(--success); font-weight: 500;">${cStr}</span>
                        </div>
                    </div>

                    <div style="background: rgba(99, 102, 241, 0.1); padding: 12px; border-radius: 8px; font-size: 0.9rem; color: var(--text-secondary);">
                        <i class="bi bi-lightbulb-fill" style="color: var(--warning); margin-right: 5px;"></i> ${q.explanation}
                    </div>
                </div>
            `;
        });

        content += `<button class="btn-primary-glass w-100" onclick="this.closest('.modal-overlay').remove()">Close Review</button></div>`;

        modal.innerHTML = content;
        document.body.appendChild(modal);
    },

    // --- PRESENTATION & TUTOR LOGIC ---

    generateNotes: async () => {
        const topic = document.getElementById('ppt-topic').value.trim();
        if (!topic) return utils.showNotification("Please enter a topic", "error");

        utils.showLoading('presentation-view', 'Creating Smart Notes...');

        try {
            // Note: Currently reusing generate_topic but ideally would have dedicated endpoint
            // For now, let's use teacher_help to get a structured summary
            const res = await fetch(`${API_BASE_URL}/teacher_help`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${app.state.token}`
                },
                body: JSON.stringify({
                    task: "Create detailed study notes",
                    topic: topic,
                    details: "Include key concepts, examples, and a summary."
                })
            });

            if (!res.ok) throw new Error("Failed to create notes");
            const data = await res.json();

            // Display in a simple modal or alert for now (can be improved to a full view)
            // Creating a simple modal on the fly
            const noteContent = data.response;
            const modal = document.createElement('div');
            modal.className = 'modal-overlay';
            modal.style.display = 'flex';
            modal.innerHTML = `
                <div class="glass-card" style="max-width: 600px; max-height: 80vh; overflow-y: auto; text-align: left;">
                    <h2 class="indigo-text"><i class="bi bi-journal-text"></i> Smart Notes: ${topic}</h2>
                    <div style="white-space: pre-wrap; line-height: 1.6; color: var(--text-secondary); margin: 20px 0;">${noteContent.replace(/\*\*/g, '')}</div>
                    <button class="btn-primary-glass w-100" onclick="this.closest('.modal-overlay').remove()">Close</button>
                </div>
            `;
            document.body.appendChild(modal);

        } catch (err) {
            console.error(err);
            utils.showNotification(err.message, "error");
        } finally {
            utils.hideLoading('presentation-view');
        }
    },

    // --- AI TUTOR CHAT ---

    tutorHistory: [],

    sendTutorMessage: async () => {
        const input = document.getElementById('tutor-input');
        const message = input.value.trim();
        if (!message) return;

        // Add User Message
        const historyContainer = document.getElementById('tutor-history');
        const userMsg = document.createElement('div');
        userMsg.className = 'msg user';
        userMsg.style.cssText = `background: var(--primary); color: white; padding: 10px 15px; border-radius: 12px 12px 0 12px; max-width: 80%; align-self: flex-end; margin: 5px 0;`;
        userMsg.textContent = message;
        historyContainer.appendChild(userMsg);

        // Clear input
        input.value = '';
        historyContainer.scrollTop = historyContainer.scrollHeight;

        // Show thinking indicator
        const loadingMsg = document.createElement('div');
        loadingMsg.className = 'msg bot loading';
        loadingMsg.style.cssText = `background: rgba(255,255,255,0.1); padding: 10px 15px; border-radius: 12px 12px 12px 0; max-width: 80%; margin: 5px 0; font-style: italic; color: var(--text-muted);`;
        loadingMsg.innerHTML = '<i class="bi bi-three-dots"></i> Thinking...';
        historyContainer.appendChild(loadingMsg);
        historyContainer.scrollTop = historyContainer.scrollHeight;

        try {
            const res = await fetch(`${API_BASE_URL}/teacher_help`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${app.state.token}`
                },
                body: JSON.stringify({
                    task: "Chat",
                    topic: "General",
                    details: message
                })
            });

            if (!res.ok) throw new Error("AI didn't respond");
            const data = await res.json();

            // Remove loading
            loadingMsg.remove();

            // Add Bot Message
            const botMsg = document.createElement('div');
            botMsg.className = 'msg bot';
            botMsg.style.cssText = `background: rgba(255,255,255,0.1); padding: 10px 15px; border-radius: 12px 12px 12px 0; max-width: 80%; margin: 5px 0;`;
            // Simple markdown parsing for bold
            botMsg.innerHTML = data.response.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
            historyContainer.appendChild(botMsg);
            historyContainer.scrollTop = historyContainer.scrollHeight;

        } catch (err) {
            loadingMsg.textContent = "Error: " + err.message;
            loadingMsg.style.color = '#ef4444';
        }
    }
};
