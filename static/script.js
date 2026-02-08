// Utility functions for performance optimization
const utils = {
    // Debounce function to reduce API calls
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
    
    // Show animated loading indicator
    showLoading: (elementId, message = 'Thinking...') => {
        const el = document.getElementById(elementId);
        if (el) {
            el.style.display = 'flex';
            el.innerHTML = `
                <div style="text-align: center;">
                    <div class="typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                    <p style="margin-top: 15px; color: var(--text-muted); font-size: 0.95rem;">${message}</p>
                </div>
            `;
        }
    },
    
    // Hide loading indicator
    hideLoading: (elementId) => {
        const el = document.getElementById(elementId);
        if (el) {
            el.style.display = 'none';
        }
    },
    
    // Animate element in with fade
    fadeIn: (element, duration = 300) => {
        if (!element) return;
        element.style.opacity = '0';
        element.style.transform = 'translateY(10px)';
        element.style.transition = `opacity ${duration}ms ease-out, transform ${duration}ms ease-out`;
        
        requestAnimationFrame(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        });
    }
};

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

            // Restore user data (including profile photo)
            const userData = localStorage.getItem('user_data');
            if (userData) {
                try {
                    const user = JSON.parse(userData);
                    if (user.profile_photo) {
                        const avatar = document.getElementById('user-avatar');
                        if (avatar) {
                            avatar.innerHTML = `<img src="${user.profile_photo}" alt="Profile" />`;
                        }
                    }
                    if (user.full_name) {
                        app.state.user.name = user.full_name;
                        if (userDisplay) userDisplay.innerText = user.full_name;
                    }
                } catch (e) {
                    console.error('Error parsing user data:', e);
                }
            }

            // Load Chat History (optimized with lazy rendering)
            const savedChat = localStorage.getItem('chatHistory');
            if (savedChat) {
                try {
                    app.state.chatHistory = JSON.parse(savedChat);
                    const historyContainer = document.getElementById('tutor-history');
                    if (historyContainer) {
                        // Use document fragment for better performance
                        const fragment = document.createDocumentFragment();
                        app.state.chatHistory.forEach(msg => {
                            if (msg.role !== 'system') {
                                const type = msg.role === 'user' ? 'msg-user' : 'msg-bot';
                                const div = document.createElement('div');
                                div.className = `msg ${type}`;
                                div.innerHTML = msg.content.replace(/\n/g, '<br>');
                                fragment.appendChild(div);
                            }
                        });
                        historyContainer.appendChild(fragment);
                        // Scroll to bottom after rendering
                        requestAnimationFrame(() => {
                            historyContainer.scrollTop = historyContainer.scrollHeight;
                        });
                    }
                } catch (e) { console.error("Chat load error", e); }
            }

            app.showTopic();
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

    showTopic: () => {
        document.getElementById('auth-view').style.display = 'none';
        document.getElementById('app-container').style.display = 'block';
        app.showView('topic-view');
        app.state.uploadedFile = null;
    },

    showUpload: () => {
        document.getElementById('auth-view').style.display = 'none';
        document.getElementById('app-container').style.display = 'block';
        app.showView('upload-view');
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
        localStorage.removeItem('user_data');
        app.state.token = null;
        window.location.reload();
    },

    toggleProfileMenu: () => {
        const menu = document.getElementById('profile-menu');
        if (menu) {
            menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
        }
    },

    viewProfile: () => {
        alert('Profile feature coming soon!');
        const menu = document.getElementById('profile-menu');
        if (menu) menu.style.display = 'none';
    },

    /* --- AUTH --- */
    /* --- AUTH & GUEST --- */
    
    // Google Sign-In
    googleSignIn: async () => {
        try {
            // Get Google Client ID from backend
            const configRes = await fetch('/auth/google/config');
            if (!configRes.ok) {
                throw new Error('Google Sign-In is not configured on the server');
            }
            const config = await configRes.json();
            
            // Initialize Google Sign-In
            google.accounts.id.initialize({
                client_id: config.client_id,
                callback: app.handleGoogleResponse,
                auto_select: false,
            });
            
            // Show One Tap prompt
            google.accounts.id.prompt((notification) => {
                if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
                    // Fallback to button click
                    console.log('One Tap not shown, using button click');
                }
            });
            
        } catch (error) {
            console.error('Google Sign-In error:', error);
            alert(error.message || 'Google Sign-In failed. Please try regular login.');
        }
    },
    
    handleGoogleResponse: async (response) => {
        try {
            const idToken = response.credential;
            
            // Show loading state
            const btn = document.getElementById('google-signin-btn');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
            btn.disabled = true;
            
            // Send token to backend for verification
            const res = await fetch('/auth/google', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id_token: idToken })
            });
            
            if (!res.ok) {
                throw new Error('Google authentication failed');
            }
            
            const data = await res.json();
            
            // Save authentication data
            app.state.token = data.access_token;
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('username', data.user.username);
            localStorage.setItem('user_data', JSON.stringify(data.user));
            
            // Update user display
            app.state.user = {
                name: data.user.full_name || data.user.username,
                photo: data.user.profile_photo
            };
            
            document.getElementById('user-display').innerText = app.state.user.name;
            
            // Update profile photo if available
            if (data.user.profile_photo) {
                const avatar = document.getElementById('user-avatar');
                avatar.innerHTML = `<img src="${data.user.profile_photo}" alt="Profile" />`;
            }
            
            // Show success message and redirect
            setTimeout(() => {
                app.showTopic();
            }, 300);
            
        } catch (error) {
            console.error('Google authentication error:', error);
            alert('Failed to sign in with Google. Please try again.');
            // Restore button
            const btn = document.getElementById('google-signin-btn');
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    },
    
    login: async () => {
        const username = document.getElementById('username-input').value;
        const password = document.getElementById('password-input').value;

        if (!username || !password) {
            alert("Please enter credentials");
            return;
        }

        try {
            // Auto Register Logic
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

            // Update user info if available
            if (data.user) {
                localStorage.setItem('user_data', JSON.stringify(data.user));
                if (data.user.profile_photo) {
                    const avatar = document.getElementById('user-avatar');
                    avatar.innerHTML = `<img src="${data.user.profile_photo}" alt="Profile" />`;
                }
            }

            document.getElementById('user-display').innerText = username;
            app.showTopic();

        } catch (e) {
            alert(e.message);
        }
    },

    guestLogin: () => {
        app.state.token = "guest_token_placeholder";
        localStorage.setItem('token', "guest_token_placeholder");
        app.state.user.name = "Guest User";
        document.getElementById('user-display').innerText = "Guest User";
        app.showTopic();
        alert("Welcome, Guest! Progress will not be saved permanently.");
    },

    /* --- QUIZ FEATURE --- */
    handleFileSelect: (input) => {
        if (input.files && input.files[0]) {
            app.state.uploadedFile = input.files[0];
            const label = document.getElementById('file-label-text');
            if (label) {
                label.innerText = `✅ ${input.files[0].name}`;
                label.style.color = 'var(--success)';
            }
        }
    },

    // --- TOPIC QUIZ ---
    generateTopicQuiz: async () => {
        const topic = document.getElementById('topic-input').value.trim();
        const numQ = parseInt(document.getElementById('q-count').value);
        const diff = document.getElementById('difficulty-select').value;
        const lang = document.getElementById('language-select').value;

        if (lang !== app.state.language) app.setLanguage(lang);
        
        // Input validation
        if (!topic || topic.length < 2) {
            alert("Please enter a valid topic (at least 2 characters).");
            document.getElementById('topic-input').focus();
            return;
        }
        
        if (numQ < 1 || numQ > 50) {
            alert("Please enter a valid number of questions (1-50).");
            document.getElementById('q-count').focus();
            return;
        }

        // Use enhanced loading indicator
        utils.showLoading('loading-topic', `Generating ${numQ} questions on ${topic}...`);

        try {
            const res = await fetch('/quiz/generate', {
                method: 'POST',
                headers: app.getHeaders(),
                body: JSON.stringify({
                    topic,
                    num_questions: numQ,
                    difficulty: diff,
                    mastery_level: "Intermediate",
                    language: app.state.language
                })
            });

            if (res.status === 401) {
                app.logout();
                throw new Error("Session expired. Please login again.");
            }
            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}));
                throw new Error(errorData.detail || "Failed to generate quiz. Try a different topic.");
            }
            const data = await res.json();
            app.startQuiz(data);

        } catch (e) {
            alert("Error: " + e.message);
        } finally {
            utils.hideLoading('loading-topic');
        }
    },

    // --- FILE QUIZ ---
    generateFileQuiz: async () => {
        if (!app.state.uploadedFile) {
            alert("Please upload a file first.");
            return;
        }

        const numQ = parseInt(document.getElementById('file-q-count').value);
        const diff = document.getElementById('file-difficulty-select').value;
        const lang = document.getElementById('file-language-select').value;
        
        // Validate number of questions
        if (numQ < 1 || numQ > 50) {
            alert("Please enter a valid number of questions (1-50).");
            document.getElementById('file-q-count').focus();
            return;
        }
        
        // Validate file size (max 10MB for performance)
        if (app.state.uploadedFile.size > 10 * 1024 * 1024) {
            alert("File is too large. Please upload a file smaller than 10MB.");
            return;
        }

        utils.showLoading('loading-file', `Processing ${app.state.uploadedFile.name}...`);

        try {
            const fd = new FormData();
            fd.append('file', app.state.uploadedFile);
            fd.append('num_questions', numQ);
            fd.append('difficulty', diff);
            fd.append('mastery_level', "Intermediate");
            fd.append('language', lang);

            const headers = app.getAuthHeaders();

            const res = await fetch('/quiz/generate-from-file', {
                method: 'POST',
                headers: headers,
                body: fd
            });

            if (res.status === 401) {
                app.logout();
                throw new Error("Session expired. Please login again.");
            }
            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}));
                throw new Error(errorData.detail || "Failed to process file. Please try a different file.");
            }
            const data = await res.json();
            app.startQuiz(data);

        } catch (e) {
            alert("Error: " + e.message);
        } finally {
            utils.hideLoading('loading-file');
        }
    },

    startQuiz: (data) => {
        app.state.questions = data.questions;
        app.state.currentQuestionIndex = 0;
        app.state.score = 0;
        app.showQuiz();
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

        // Use document fragment for better performance
        const fragment = document.createDocumentFragment();
        q.choices.forEach((opt, index) => {
            const div = document.createElement('div');
            div.className = 'option-card';
            div.innerText = opt;
            div.onclick = () => app.checkAnswer(opt, div);
            // Use CSS animation-delay for staggered entrance
            div.style.animationDelay = `${index * 0.05}s`;
            fragment.appendChild(div);
        });
        con.appendChild(fragment);
    },

    checkAnswer: (selected, el) => {
        const q = app.state.questions[app.state.currentQuestionIndex];
        const opts = document.querySelectorAll('.option-card');
        
        // Disable all options to prevent multiple clicks
        opts.forEach(o => o.onclick = null);

        if (selected == q.answer) {
            el.classList.add('correct');
            app.state.score++;
        } else {
            el.classList.add('wrong');
            opts.forEach(o => { if (o.innerText == q.answer) o.classList.add('correct'); });
        }

        // Show Explanation with fade in
        const expBox = document.getElementById('explanation-box');
        const expText = document.getElementById('explanation-text');
        expText.innerText = q.explanation;
        expBox.style.display = 'block';
        utils.fadeIn(expBox, 400);

        // Auto scroll to explanation smoothly
        setTimeout(() => {
            expBox.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }, 100);
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
        // Simple clipboard share
        const text = `I just scored ${Math.round((app.state.score / app.state.questions.length) * 100)}% on a QuizAI lesson! 🚀`;
        navigator.clipboard.writeText(text).then(() => alert("Result copied to clipboard!"));
    },

    /* --- TUTOR --- */
    sendTutorMessage: async () => {
        const input = document.getElementById('tutor-input');
        const msg = input.value.trim();
        
        // Validation
        if (!msg) return;
        if (msg.length > 2000) {
            alert("Message is too long. Please keep it under 2000 characters.");
            return;
        }

        const box = document.getElementById('tutor-history');
        
        // Add user message with animation (using textContent for XSS safety)
        const userMsg = document.createElement('div');
        userMsg.className = 'msg msg-user';
        userMsg.textContent = msg; // Use textContent instead of innerHTML for safety
        box.appendChild(userMsg);
        utils.fadeIn(userMsg, 200);
        
        input.value = '';
        input.disabled = true; // Prevent spamming
        
        // Smooth scroll using requestAnimationFrame for better performance
        requestAnimationFrame(() => {
            box.scrollTop = box.scrollHeight;
        });

        // Add typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'msg msg-bot typing-container';
        typingIndicator.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
        box.appendChild(typingIndicator);
        requestAnimationFrame(() => {
            box.scrollTop = box.scrollHeight;
        });

        try {
            const res = await fetch('/ai/chat', {
                method: 'POST',
                headers: app.getHeaders(),
                body: JSON.stringify({
                    message: msg,
                    history: app.state.chatHistory.slice(-10), // Only send last 10 messages for performance
                    language: app.state.language
                })
            });
            
            // Remove typing indicator
            typingIndicator.remove();
            
            if (res.status === 401) {
                app.logout();
                throw new Error("Session expired.");
            }
            
            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}));
                throw new Error(errorData.detail || "Failed to get response from AI.");
            }
            
            const data = await res.json();
            
            // Add bot response with animation
            const botMsg = document.createElement('div');
            botMsg.className = 'msg msg-bot';
            botMsg.innerHTML = data.response.replace(/\n/g, '<br>');
            box.appendChild(botMsg);
            utils.fadeIn(botMsg, 300);
            requestAnimationFrame(() => {
                box.scrollTop = box.scrollHeight;
            });

            app.state.chatHistory.push({ role: 'user', content: msg });
            app.state.chatHistory.push({ role: 'assistant', content: data.response });
            
            // Keep only last 50 messages for performance
            if (app.state.chatHistory.length > 50) {
                app.state.chatHistory = app.state.chatHistory.slice(-50);
            }
            localStorage.setItem('chatHistory', JSON.stringify(app.state.chatHistory));

        } catch (e) {
            typingIndicator.remove();
            const errorMsg = document.createElement('div');
            errorMsg.className = 'msg msg-bot';
            errorMsg.style.color = 'var(--error)';
            errorMsg.innerHTML = `Error: ${e.message}`;
            box.appendChild(errorMsg);
        } finally {
            input.disabled = false;
            input.focus();
        }
    },

    /* --- SMART NOTES --- */
    showNotes: () => {
        app.showView('presentation-view'); // View ID kept same in HTML update for simplicity, or we should have updated it.
        // In previous step I kept ID as presentation-view in HTML for the container div? 
        // Let me check my previous HTML update.
        // Yes: <div id="presentation-view" class="screen" style="display: none;">
        // So keeping view ID same is fine.
    },

    generateNotes: async () => {
        const topic = document.getElementById('ppt-topic').value.trim();
        const slidesValue = document.getElementById('ppt-slides').value;
        const slides = parseInt(slidesValue, 10);
        const font = document.getElementById('ppt-font').value;
        const format = document.getElementById('ppt-format').value;

        // Input validation
        if (!topic || topic.length < 2) {
            alert("Please enter a valid topic (at least 2 characters).");
            document.getElementById('ppt-topic').focus();
            return;
        }
        
        // Check for valid number after parsing
        if (isNaN(slides) || slides < 3 || slides > 30) {
            alert("Please enter a valid number of slides (3-30).");
            return;
        }

        utils.showLoading('ppt-loading', `Creating ${format.toUpperCase()} on ${topic}...`);

        try {
            const res = await fetch('/presentation/generate', {
                method: 'POST',
                headers: app.getHeaders(),
                body: JSON.stringify({
                    topic,
                    num_slides: slides,
                    language: app.state.language,
                    font_style: font,
                    format: format,
                    tone: "Professional"
                })
            });

            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}));
                throw new Error(errorData.detail || "Generation Failed. Check API status.");
            }

            // Handle File Download
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);

            // Determine extension
            let ext = "pptx";
            if (format === "pdf") ext = "pdf";
            if (format === "docx") ext = "docx";

            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `${topic.replace(/\s/g, '_')}_Notes.${ext}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();

            alert("Notes Downloaded! 📝");

        } catch (e) {
            alert("Error: " + e.message);
        } finally {
            utils.hideLoading('ppt-loading');
        }
    }
};

// Start
app.init();

// Close profile menu when clicking outside
document.addEventListener('click', (e) => {
    const menu = document.getElementById('profile-menu');
    const dropdown = document.querySelector('.user-profile-dropdown');
    if (menu && dropdown && !dropdown.contains(e.target)) {
        menu.style.display = 'none';
    }
});
