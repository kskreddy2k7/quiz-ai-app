
// PWA logic
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    console.log("PWA Install prompt ready");
});

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(reg => console.log('SW Registered'))
            .catch(err => console.log('SW Failed', err));
    });
}

console.log("S Quiz Logic Loaded");

// Debug Helper
function debugLog(message) {
    console.log(message);
}

// NOTE: We keep inline onclick handlers in the HTML for simplicity as requested, 
// but we also add a listener here just in case.
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM Loaded - Verifying Elements");
    const topicBtn = document.getElementById('topicBtn');
    if (topicBtn) console.log("Topic Button Found");
});

async function generateTopicQuiz() {
    console.log("Generate Topic Quiz called");


    const topic = document.getElementById('topic').value;
    const difficulty = document.getElementById('difficulty').value;
    const language = document.getElementById('language').value;
    const num_questions = parseInt(document.getElementById('num_questions').value);

    if (!topic) {
        alert('Please enter a topic!');
        return;
    }

    // UI Feedback
    const btn = document.getElementById('topicBtn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '⏳ Generating...';
    }

    showLoading('topic');
    const resultDiv = document.getElementById('topicResult');
    if (resultDiv) resultDiv.innerHTML = '';

    try {
        console.log("Sending request to /generate_topic...");
        const response = await fetch('/generate_topic', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, difficulty, language, num_questions })
        });

        console.log("Response status:", response.status);
        if (!response.ok) {
            throw new Error(`Server Error: ${response.status}`);
        }

        const data = await response.json();
        console.log("Data received:", data);

        if (data.error) {
            showError('topic', data.error);
        } else {
            displayQuiz('topic', data.questions);
        }
    } catch (error) {
        console.error("Fetch Error:", error);
        showError('topic', `Failed: ${error.message}`);
    } finally {
        hideLoading('topic');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '🚀 Generate Quiz';
        }
    }
}

async function generateFileQuiz() {
    console.log("File Button Clicked!");
    const fileInput = document.getElementById('fileInput');
    const difficulty = document.getElementById('fileDifficulty').value;
    const num_questions = parseInt(document.getElementById('fileNumQuestions').value);

    if (!fileInput.files[0]) {
        alert('Please select a file!');
        return;
    }

    if (num_questions < 1 || num_questions > 100) {
        alert('Please enter a number between 1 and 100!');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('difficulty', difficulty);
    formData.append('num_questions', num_questions);

    showLoading('file');

    try {
        const response = await fetch('/generate_file', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            showError('file', data.error);
        } else {
            const fileInfo = document.getElementById('fileInfo');
            if (fileInfo) {
                fileInfo.style.display = 'block';
                fileInfo.textContent = `✅ Processed: ${data.filename} (${data.text_length} characters)`;
            }
            displayQuiz('file', data.questions);
        }
    } catch (error) {
        showError('file', error.message);
    } finally {
        hideLoading('file');
    }
}

async function getTeacherHelp() {
    const task = document.getElementById('teacherTask').value;
    const topic = document.getElementById('teacherTopic').value;
    const details = document.getElementById('teacherDetails').value;

    if (!topic) {
        alert('Please enter a topic!');
        return;
    }

    showLoading('teacher');

    try {
        const response = await fetch('/teacher_help', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task, topic, details })
        });

        const data = await response.json();

        if (data.error) {
            showError('teacher', data.error);
        } else {
            displayTeacherHelp(data.response);
        }
    } catch (error) {
        showError('teacher', error.message);
    } finally {
        hideLoading('teacher');
    }
}

async function getAIHelp() {
    const question = document.getElementById('helpQuestion').value;
    const style = document.getElementById('helpStyle').value;

    if (!question) {
        alert('Please enter a question!');
        return;
    }

    showLoading('help');

    try {
        const response = await fetch('/ai_help', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, style })
        });

        const data = await response.json();

        if (data.error) {
            showError('help', data.error);
        } else {
            displayAIHelp(data.response);
        }
    } catch (error) {
        showError('help', error.message);
    } finally {
        hideLoading('help');
    }
}

function showLoading(tab) {
    const loading = document.getElementById(tab + 'Loading');
    if (loading) loading.style.display = 'block';

    const error = document.getElementById(tab + 'Error');
    if (error) error.style.display = 'none';

    const result = document.getElementById(tab + 'Result');
    if (result) result.innerHTML = '';

    const btn = document.getElementById(tab + 'Btn');
    if (btn) btn.disabled = true;
}

function hideLoading(tab) {
    const loading = document.getElementById(tab + 'Loading');
    if (loading) loading.style.display = 'none';

    const btn = document.getElementById(tab + 'Btn');
    if (btn) btn.disabled = false;
}

function showError(tab, message) {
    const error = document.getElementById(tab + 'Error');
    if (error) {
        error.textContent = '❌ ' + message;
        error.style.display = 'block';
    }
}

let currentQuestions = [];
let userAnswers = {};

function displayQuiz(tab, questions) {
    if (!questions || !Array.isArray(questions)) {
        showError(tab, "Invalid quiz data received. Please try again.");
        console.error("Invalid questions data:", questions);
        return;
    }

    if (questions.length === 0) {
        showError(tab, "AI generated 0 questions. Try a different topic.");
        return;
    }

    console.log(`Rendering ${questions.length} questions for tab: ${tab}`);

    currentQuestions = questions;
    userAnswers = {};

    const resultDiv = document.getElementById(tab + 'Result');
    if (!resultDiv) return;

    resultDiv.innerHTML = '';
    resultDiv.style.display = 'block'; // Ensure it's visible

    questions.forEach((q, index) => {
        const card = document.createElement('div');
        card.className = 'question-card';
        card.id = `q-card-${index}`;
        card.style.display = 'block';
        card.style.opacity = '1';
        card.style.zIndex = '100';
        card.style.position = 'relative';

        // Defensive checks to prevent crashes if AI data is incomplete
        const prompt = q.prompt || "No question text available";
        const choices = Array.isArray(q.choices) ? q.choices : [];
        const explanation = q.explanation || "No explanation provided.";

        let html = `
            <div class="question-text">
                <strong>Q${index + 1}:</strong> ${prompt}
            </div>
            <div class="options-container">
        `;

        choices.forEach((choice, i) => {
            // Safe string handling for HTML attributes
            const safeChoice = String(choice).replace(/'/g, "\\'").replace(/"/g, "&quot;");
            html += `
                <div class="option" onclick="selectOption(${index}, '${safeChoice}', this)">
                    ${String.fromCharCode(65 + i)}) ${choice}
                </div>
            `;
        });

        html += `</div>`; // End options-container

        // Add hidden result sections
        html += `
            <div class="explanation hidden" id="exp-${index}">
                <div class="explanation-title">💡 Explanation:</div>
                ${explanation}
            </div>
        `;

        if (q.wrong_explanations && typeof q.wrong_explanations === 'object') {
            html += `<div class="wrong-explanations-group hidden" id="wrong-exp-${index}">`;
            for (const [option, exp] of Object.entries(q.wrong_explanations)) {
                html += `
                    <div class="wrong-explanation">
                        <strong>❌ Why "${option}" is wrong:</strong><br>
                        ${exp}
                    </div>
                `;
            }
            html += `</div>`;
        }

        card.innerHTML = html;
        resultDiv.appendChild(card);
    });

    // Add submit button
    const submitBtn = document.createElement('button');
    submitBtn.id = 'submit-quiz-btn';
    submitBtn.style.marginTop = '30px';
    submitBtn.textContent = '✅ Submit Quiz & Get Results';
    submitBtn.onclick = () => checkQuiz(tab);
    resultDiv.appendChild(submitBtn);
}

function selectOption(qIndex, choice, element) {
    // Already submitted? Don't allow changes
    const btn = document.getElementById('submit-quiz-btn');
    if (btn && btn.classList.contains('hidden')) return;

    userAnswers[qIndex] = choice;

    // UI Update
    const container = element.parentElement;
    container.querySelectorAll('.option').forEach(opt => opt.classList.remove('selected'));
    element.classList.add('selected');
}

function checkQuiz(tab) {
    if (Object.keys(userAnswers).length < currentQuestions.length) {
        if (!confirm('You haven\'t answered all questions. Submit anyway?')) return;
    }

    let score = 0;
    currentQuestions.forEach((q, index) => {
        const isCorrect = userAnswers[index] === q.answer;
        if (isCorrect) score++;

        const card = document.getElementById(`q-card-${index}`);
        const options = card.querySelectorAll('.option');

        options.forEach(opt => {
            const fullText = opt.textContent.trim();
            // Robust splitting: Handles cases where ") " might be missing or different
            const separatorIndex = fullText.indexOf(') ');
            const optText = separatorIndex !== -1 ? fullText.substring(separatorIndex + 2).trim() : fullText;

            if (optText === q.answer) {
                opt.classList.add('correct');
                opt.innerHTML += ' ✅ (Correct)';
            } else if (userAnswers[index] === optText) {
                opt.classList.add('wrong');
                opt.innerHTML += ' ❌ (Your Choice)';
            }
            opt.classList.remove('selected');
        });

        // Reveal explanations
        const exp = document.getElementById(`exp-${index}`);
        if (exp) exp.classList.remove('hidden');

        const wrongExp = document.getElementById(`wrong-exp-${index}`);
        if (wrongExp) wrongExp.classList.remove('hidden');
    });



    // Show score summary
    const resultDiv = document.getElementById(tab + 'Result');
    const summary = document.createElement('div');
    summary.className = 'score-summary';
    const percent = Math.round((score / currentQuestions.length) * 100);
    summary.innerHTML = `
        <h1 style="margin:0; font-size: 3rem;">${percent}%</h1>
        <p style="font-size: 1.5rem;">Score: ${score} / ${currentQuestions.length}</p>
        <div class="creator-badge" style="background: rgba(255,255,255,0.2); margin-bottom: 15px;">
            ${score === currentQuestions.length ? '🌟 PERFECT! 🌟' : score > currentQuestions.length / 2 ? '👏 GREAT JOB! 👏' : '📚 Keep Learning! 📚'}
        </div>
        <div class="btn-group" style="justify-content: center;">
            <button class="share-btn" onclick="shareQuiz(${percent})">📢 Share with Friends</button>
        </div>
    `;
    resultDiv.insertBefore(summary, resultDiv.firstChild);

    // Hide submit button
    const submitBtn = document.getElementById('submit-quiz-btn');
    if (submitBtn) submitBtn.classList.add('hidden');

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
async function shareQuiz(score, topic = "a Quiz") {
    const text = "🚀 I just scored " + score + "% on " + topic + " in the S Quiz AI Academy! Can you beat me? 🎓✨";
    const url = window.location.href;

    if (navigator.share) {
        try {
            await navigator.share({
                title: 'S Quiz Result',
                text: text,
                url: url
            });
        } catch (err) {
            console.log('Share failed:', err);
        }
    } else {
        const dummy = document.createElement("textarea");
        document.body.appendChild(dummy);
        dummy.value = text + " " + url;
        dummy.select();
        document.execCommand("copy");
        document.body.removeChild(dummy);
        alert("Score & Link copied to clipboard! Share it with your friends! 🚀");
    }
}

function displayTeacherHelp(response) {
    const resultDiv = document.getElementById('teacherResult');
    if (resultDiv) {
        resultDiv.innerHTML = `
            <div class="card" style="margin-top: 30px; background: rgba(255,255,255,0.2);">
                <h3 style="margin-bottom: 20px;">📋 AI Assistant Response</h3>
                <div style="white-space: pre-wrap; line-height: 1.8;">${response}</div>
            </div>
        `;
    }
}

function displayAIHelp(response) {
    const resultDiv = document.getElementById('helpResult');
    if (resultDiv) {
        resultDiv.innerHTML = `
            <div class="card" style="margin-top: 30px; background: rgba(255,255,255,0.2);">
                <h3 style="margin-bottom: 20px;">💬 AI Response</h3>
                <div style="white-space: pre-wrap; line-height: 1.8;">${response}</div>
            </div>
        `;
    }
}
