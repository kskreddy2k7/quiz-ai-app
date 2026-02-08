// Configuration Constants
const CONFIG = {
    PWA_BANNER_DELAY: 5000,      // 5 seconds
    APK_MODAL_DELAY: 10000,      // 10 seconds
    PROMO_DELAY: 3000            // 3 seconds
};

// Motivational Quotes Pool
const QUOTES = [
    { text: "The beautiful thing about learning is that no one can take it away from you.", author: "B.B. King" },
    { text: "Education is the most powerful weapon which you can use to change the world.", author: "Nelson Mandela" },
    { text: "The only way to learn mathematics is to do mathematics.", author: "Paul Halmos" },
    { text: "Live as if you were to die tomorrow. Learn as if you were to live forever.", author: "Mahatma Gandhi" },
    { text: "An investment in knowledge pays the best interest.", author: "Benjamin Franklin" },
    { text: "The capacity to learn is a gift; the ability to learn is a skill; the willingness to learn is a choice.", author: "Brian Herbert" },
    { text: "Learning never exhausts the mind.", author: "Leonardo da Vinci" },
    { text: "The more that you read, the more things you will know. The more that you learn, the more places you'll go.", author: "Dr. Seuss" },
    { text: "Education is not the filling of a pail, but the lighting of a fire.", author: "William Butler Yeats" },
    { text: "Success is the sum of small efforts repeated day in and day out.", author: "Robert Collier" }
];

// Get a random quote that hasn't been shown recently
const getRandomQuote = () => {
    const lastQuote = localStorage.getItem('lastQuote') || '';
    let quote;
    do {
        quote = QUOTES[Math.floor(Math.random() * QUOTES.length)];
    } while (QUOTES.length > 1 && JSON.stringify(quote) === lastQuote);
    localStorage.setItem('lastQuote', JSON.stringify(quote));
    return quote;
};

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
    
    // Show animated loading indicator with AI steps
    showLoadingSteps: (elementId, steps = [
        '✓ Understanding topic',
        '✓ Selecting difficulty',
        '✓ Generating questions',
        '✓ Finalizing quiz'
    ]) => {
        const el = document.getElementById(elementId);
        if (!el) return;
        
        el.style.display = 'block';
        el.innerHTML = `
            <div style="text-align: center;">
                <div class="typing-indicator" style="margin-bottom: 20px;">
                    <span></span><span></span><span></span>
                </div>
                <div id="loading-steps" style="text-align: left; display: inline-block; margin: 0 auto;">
                    ${steps.map((step, i) => `
                        <div class="loading-step" data-step="${i}" style="opacity: 0.3; padding: 8px 0; transition: all 0.3s ease;">
                            <span style="color: var(--text-muted); font-size: 0.95rem;">${step.replace('✓', '<span class="step-check">⏳</span>')}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        // Animate steps
        steps.forEach((step, i) => {
            setTimeout(() => {
                const stepEl = el.querySelector(`[data-step="${i}"]`);
                if (stepEl) {
                    stepEl.style.opacity = '1';
                    const checkEl = stepEl.querySelector('.step-check');
                    if (checkEl) {
                        checkEl.textContent = '✓';
                        checkEl.style.color = 'var(--success)';
                    }
                }
            }, i * 400);
        });
    },
    
    // Show animated loading indicator (fallback for simple cases)
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
    },

    // Show notification modal (replaces alert)
    showNotification: (message, type = 'info') => {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'notification-toast';
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 30px;
            background: ${type === 'error' ? 'linear-gradient(135deg, #ef4444, #dc2626)' : 
                        type === 'success' ? 'linear-gradient(135deg, #10b981, #059669)' : 
                        'linear-gradient(135deg, #6366f1, #a855f7)'};
            color: white;
            padding: 20px 30px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            z-index: 10001;
            max-width: 400px;
            animation: slideInRight 0.3s ease-out;
            font-weight: 500;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
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
        // 0. Check if first time user and show onboarding
        const hasSeenOnboarding = localStorage.getItem('onboarding_completed');
        if (!hasSeenOnboarding) {
            app.showOnboarding();
        }

        // Initialize PWA support
        app.initPWA();

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
                            // Secure: Create img element to avoid XSS
                            const img = document.createElement('img');
                            img.src = user.profile_photo;
                            img.alt = 'Profile';
                            avatar.innerHTML = '';
                            avatar.appendChild(img);
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
            }, CONFIG.PROMO_DELAY);
        }

        // 4. Detect Android device and offer APK
        app.detectAndroidDevice();
        
        // 5. Initialize quotes on auth screen
        app.updateAuthQuote();
        
        // 6. Show daily motivation card (if not dismissed today)
        app.showDailyMotivation();
    },

    /* --- QUOTE MANAGEMENT --- */
    updateAuthQuote: () => {
        const quote = getRandomQuote();
        const textEl = document.getElementById('auth-quote-text');
        const authorEl = document.getElementById('auth-quote-author');
        if (textEl) textEl.textContent = `"${quote.text}"`;
        if (authorEl) authorEl.textContent = `— ${quote.author}`;
    },
    
    updateResultQuote: () => {
        const quote = getRandomQuote();
        const textEl = document.getElementById('result-quote-text');
        const authorEl = document.getElementById('result-quote-author');
        if (textEl) textEl.textContent = `"${quote.text}"`;
        if (authorEl) authorEl.textContent = `— ${quote.author}`;
    },
    
    showDailyMotivation: () => {
        const today = new Date().toDateString();
        const lastShown = localStorage.getItem('motivationShownDate');
        
        // Show once per day
        if (lastShown !== today) {
            setTimeout(() => {
                const card = document.getElementById('daily-motivation-card');
                if (card) {
                    const quote = getRandomQuote();
                    const textEl = document.getElementById('motivation-text');
                    const authorEl = document.getElementById('motivation-author');
                    if (textEl) textEl.textContent = `"${quote.text}"`;
                    if (authorEl) authorEl.textContent = `— ${quote.author}`;
                    card.style.display = 'block';
                }
            }, 3000); // Show after 3 seconds
        }
    },
    
    dismissMotivation: () => {
        const card = document.getElementById('daily-motivation-card');
        if (card) {
            card.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                card.style.display = 'none';
                const today = new Date().toDateString();
                localStorage.setItem('motivationShownDate', today);
            }, 300);
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
        // Load current profile data
        const userData = localStorage.getItem('user_data');
        const username = localStorage.getItem('username') || 'Student';
        const email = localStorage.getItem('user_email') || '';
        
        // Populate profile fields
        document.getElementById('profile-name').value = username;
        
        if (userData) {
            try {
                const user = JSON.parse(userData);
                if (user.full_name) document.getElementById('profile-name').value = user.full_name;
                if (user.class_course) document.getElementById('profile-class').value = user.class_course;
                if (user.bio) document.getElementById('profile-bio').value = user.bio;
                
                // Update profile photo if available
                if (user.profile_photo) {
                    const photoDisplay = document.getElementById('profile-photo-display');
                    if (photoDisplay) {
                        const img = document.createElement('img');
                        img.src = user.profile_photo;
                        img.alt = 'Profile';
                        img.style.width = '100%';
                        img.style.height = '100%';
                        img.style.objectFit = 'cover';
                        photoDisplay.innerHTML = '';
                        photoDisplay.appendChild(img);
                    }
                }
            } catch (e) {
                console.error('Error parsing user data:', e);
            }
        }
        
        // Set language selector
        document.getElementById('profile-language').value = app.state.language;
        
        // Set email display
        if (email) {
            document.getElementById('profile-email-display').textContent = email;
        }
        
        // Close profile menu and show profile view
        const menu = document.getElementById('profile-menu');
        if (menu) menu.style.display = 'none';
        
        document.getElementById('profile-view').style.display = 'block';
    },

    closeProfile: () => {
        document.getElementById('profile-view').style.display = 'none';
    },

    saveProfile: () => {
        // Get profile data
        const name = document.getElementById('profile-name').value.trim();
        const classCourse = document.getElementById('profile-class').value.trim();
        const language = document.getElementById('profile-language').value;
        const bio = document.getElementById('profile-bio').value.trim();
        
        // Validation
        if (!name || name.length < 2) {
            utils.showNotification('Name must be at least 2 characters long', 'error');
            return;
        }
        
        // Update state
        app.state.user.name = name;
        localStorage.setItem('username', name);
        
        // Update user data
        let userData = {};
        try {
            const existing = localStorage.getItem('user_data');
            if (existing) userData = JSON.parse(existing);
        } catch (e) {}
        
        userData.full_name = name;
        userData.class_course = classCourse;
        userData.bio = bio;
        
        localStorage.setItem('user_data', JSON.stringify(userData));
        
        // Update language if changed
        if (language !== app.state.language) {
            app.setLanguage(language);
        }
        
        // Update display name in header
        const userDisplay = document.getElementById('user-display');
        if (userDisplay) userDisplay.innerText = name;
        
        utils.showNotification('✓ Profile updated successfully!', 'success');
        
        // Close profile after a short delay
        setTimeout(() => {
            app.closeProfile();
        }, 1000);
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
            utils.showNotification(error.message || 'Google Sign-In failed. Please try regular login.');
        }
    },
    
    handleGoogleResponse: async (response) => {
        const btn = document.getElementById('google-signin-btn');
        const originalText = btn.innerHTML; // Store original content
        
        try {
            const idToken = response.credential;
            
            // Show loading state
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
            
            // Update profile photo if available (secure way)
            if (data.user.profile_photo) {
                const avatar = document.getElementById('user-avatar');
                const img = document.createElement('img');
                img.src = data.user.profile_photo;
                img.alt = 'Profile';
                avatar.innerHTML = '';
                avatar.appendChild(img);
            }
            
            // Show success message and redirect
            setTimeout(() => {
                app.showTopic();
            }, 300);
            
        } catch (error) {
            console.error('Google authentication error:', error);
            utils.showNotification('Failed to sign in with Google. Please try again.');
            // Restore button
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    },
    
    login: async () => {
        const username = document.getElementById('username-input').value;
        const password = document.getElementById('password-input').value;

        if (!username || !password) {
            utils.showNotification("Please enter credentials");
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
                    const img = document.createElement('img');
                    img.src = data.user.profile_photo;
                    img.alt = 'Profile';
                    avatar.innerHTML = '';
                    avatar.appendChild(img);
                }
            }

            document.getElementById('user-display').innerText = username;
            app.showTopic();

        } catch (e) {
            utils.showNotification(e.message);
        }
    },

    guestLogin: () => {
        app.state.token = "guest_token_placeholder";
        localStorage.setItem('token', "guest_token_placeholder");
        app.state.user.name = "Guest User";
        document.getElementById('user-display').innerText = "Guest User";
        app.showTopic();
        utils.showNotification("Welcome, Guest! Progress will not be saved permanently.");
    },

    // Toggle password visibility
    togglePasswordVisibility: () => {
        const passwordInput = document.getElementById('password-input');
        const toggleIcon = document.getElementById('password-toggle-icon');
        const toggleBtn = document.getElementById('toggle-password');
        
        if (passwordInput && toggleIcon && toggleBtn) {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                toggleIcon.className = 'bi bi-eye-slash';
                toggleBtn.setAttribute('aria-label', 'Hide password');
            } else {
                passwordInput.type = 'password';
                toggleIcon.className = 'bi bi-eye';
                toggleBtn.setAttribute('aria-label', 'Show password');
            }
        }
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
            utils.showNotification("Please enter a valid topic (at least 2 characters).", "error");
            document.getElementById('topic-input').focus();
            return;
        }
        
        if (numQ < 1 || numQ > 50) {
            utils.showNotification("Please enter a valid number of questions (1-50).", "error");
            document.getElementById('q-count').focus();
            return;
        }

        // Use enhanced loading indicator with animated steps
        utils.showLoadingSteps('loading-topic', [
            '⏳ Understanding topic',
            '⏳ Selecting difficulty',
            '⏳ Generating questions',
            '⏳ Finalizing quiz'
        ]);

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
            utils.showNotification("Error: " + e.message, "error");
        } finally {
            utils.hideLoading('loading-topic');
        }
    },

    // --- FILE QUIZ ---
    generateFileQuiz: async () => {
        if (!app.state.uploadedFile) {
            utils.showNotification("Please upload a file first.", "error");
            return;
        }

        const numQ = parseInt(document.getElementById('file-q-count').value);
        const diff = document.getElementById('file-difficulty-select').value;
        const lang = document.getElementById('file-language-select').value;
        
        // Validate number of questions
        if (numQ < 1 || numQ > 50) {
            utils.showNotification("Please enter a valid number of questions (1-50).", "error");
            document.getElementById('file-q-count').focus();
            return;
        }
        
        // Validate file size (max 10MB for performance)
        if (app.state.uploadedFile.size > 10 * 1024 * 1024) {
            utils.showNotification("File is too large. Please upload a file smaller than 10MB.", "error");
            return;
        }

        utils.showLoadingSteps('loading-file', [
            '⏳ Reading file',
            '⏳ Extracting content',
            '⏳ Generating questions',
            '⏳ Creating quiz'
        ]);

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
            utils.showNotification("Error: " + e.message);
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
        
        // Update result quote
        app.updateResultQuote();
    },

    shareQuiz: () => {
        // Simple clipboard share
        const text = `I just scored ${Math.round((app.state.score / app.state.questions.length) * 100)}% on a QuizAI lesson! 🚀`;
        navigator.clipboard.writeText(text).then(() => utils.showNotification("Result copied to clipboard!"));
    },

    /* --- TUTOR --- */
    sendTutorMessage: async () => {
        const input = document.getElementById('tutor-input');
        const msg = input.value.trim();
        
        // Validation
        if (!msg) return;
        if (msg.length > 2000) {
            utils.showNotification("Message is too long. Please keep it under 2000 characters.");
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
            utils.showNotification("Please enter a valid topic (at least 2 characters).");
            document.getElementById('ppt-topic').focus();
            return;
        }
        
        // Check for valid number after parsing
        if (isNaN(slides) || slides < 3 || slides > 30) {
            utils.showNotification("Please enter a valid number of slides (3-30).");
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

            utils.showNotification("Notes Downloaded! 📝");

        } catch (e) {
            utils.showNotification("Error: " + e.message);
        } finally {
            utils.hideLoading('ppt-loading');
        }
    },

    /* --- ONBOARDING MODAL --- */
    showOnboarding: () => {
        const modal = document.getElementById('onboarding-modal');
        if (modal) modal.style.display = 'flex';
    },

    closeOnboarding: () => {
        const modal = document.getElementById('onboarding-modal');
        if (modal) modal.style.display = 'none';
        localStorage.setItem('onboarding_completed', 'true');
    },

    startLearning: () => {
        app.closeOnboarding();
        // If not logged in, show auth
        if (!app.state.token) {
            app.showAuth();
        }
    },

    /* --- PWA INSTALL --- */
    deferredPrompt: null,

    initPWA: () => {
        // Listen for beforeinstallprompt event
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            app.deferredPrompt = e;
            
            // Show PWA banner if user hasn't dismissed it
            if (!localStorage.getItem('pwa_dismissed')) {
                const banner = document.getElementById('pwa-banner');
                if (banner) {
                    setTimeout(() => {
                        banner.style.display = 'flex';
                    }, CONFIG.PWA_BANNER_DELAY);
                }
            }
        });

        // Listen for successful installation
        window.addEventListener('appinstalled', () => {
            console.log('PWA installed successfully');
            app.dismissPWA();
        });
        
        // Online/Offline detection
        const offlineIndicator = document.getElementById('offline-indicator');
        
        window.addEventListener('online', () => {
            console.log('Back online');
            if (offlineIndicator) offlineIndicator.style.display = 'none';
        });
        
        window.addEventListener('offline', () => {
            console.log('Gone offline');
            if (offlineIndicator) offlineIndicator.style.display = 'flex';
        });
        
        // Check initial status
        if (!navigator.onLine && offlineIndicator) {
            offlineIndicator.style.display = 'flex';
        }
    },

    installPWA: async () => {
        if (!app.deferredPrompt) {
            utils.showNotification('PWA installation is not available on this device/browser.');
            return;
        }

        app.deferredPrompt.prompt();
        const { outcome } = await app.deferredPrompt.userChoice;
        
        if (outcome === 'accepted') {
            console.log('User accepted PWA installation');
        } else {
            console.log('User dismissed PWA installation');
        }
        
        app.deferredPrompt = null;
        app.dismissPWA();
    },

    dismissPWA: () => {
        const banner = document.getElementById('pwa-banner');
        if (banner) banner.style.display = 'none';
        localStorage.setItem('pwa_dismissed', 'true');
    },

    /* --- APK DOWNLOAD --- */
    showAPKModal: () => {
        const modal = document.getElementById('apk-modal');
        if (modal) modal.style.display = 'flex';
    },

    closeAPKModal: () => {
        const modal = document.getElementById('apk-modal');
        if (modal) modal.style.display = 'none';
    },

    detectAndroidDevice: () => {
        const isAndroid = /Android/i.test(navigator.userAgent);
        if (isAndroid && !localStorage.getItem('apk_dismissed')) {
            // Show APK download option after configured delay
            setTimeout(() => {
                app.showAPKModal();
            }, CONFIG.APK_MODAL_DELAY);
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
