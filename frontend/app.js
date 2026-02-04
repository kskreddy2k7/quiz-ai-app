const quizForm = document.getElementById("quiz-form");
const quizMessage = document.getElementById("quiz-message");
const quizResults = document.getElementById("quiz-results");
const quizSummary = document.getElementById("quiz-summary");
const generateBtn = document.getElementById("generate-btn");
const scrollChat = document.getElementById("scroll-chat");
const loadingScreen = document.getElementById("loading-screen");
const loadingMessage = document.getElementById("loading-message");
const chatForm = document.getElementById("chat-form");
const chatWindow = document.getElementById("chat-window");
const chatTips = document.getElementById("chat-tips");
const fileHint = document.getElementById("file-hint");
const filePreview = document.getElementById("file-preview");
const connectionStatus = document.getElementById("connection-status");
const chatStatus = document.getElementById("chat-status");
const savedDoubts = document.getElementById("saved-doubts");
const savedQuizzes = document.getElementById("saved-quizzes");
const streakCount = document.getElementById("streak-count");
const progressScore = document.getElementById("progress-score");
const motivationMessage = document.getElementById("motivation-message");

const loadingMessages = [
  "Warming up your brain 🧠✨",
  "Your AI tutor is getting ready 🤖📚",
  "Turning doubts into clarity… 🚀",
];

let loadingIndex = 0;
const STORAGE_KEYS = {
  doubts: "quizai_saved_doubts",
  quizzes: "quizai_saved_quizzes",
  streak: "quizai_streak",
  lastActive: "quizai_last_active",
};

const rotateLoadingMessage = () => {
  loadingIndex = (loadingIndex + 1) % loadingMessages.length;
  loadingMessage.textContent = loadingMessages[loadingIndex];
};

const showLoading = () => {
  loadingScreen.classList.add("active");
  loadingMessage.textContent = loadingMessages[loadingIndex];
  loadingScreen.timer = setInterval(rotateLoadingMessage, 1800);
};

const hideLoading = () => {
  loadingScreen.classList.remove("active");
  clearInterval(loadingScreen.timer);
};

const getSavedItems = (key) => JSON.parse(localStorage.getItem(key) || "[]");
const setSavedItems = (key, items) => localStorage.setItem(key, JSON.stringify(items));

const updateStreak = () => {
  const today = new Date();
  const todayKey = today.toISOString().slice(0, 10);
  const lastActive = localStorage.getItem(STORAGE_KEYS.lastActive);
  let streak = Number(localStorage.getItem(STORAGE_KEYS.streak) || 0);

  if (lastActive !== todayKey) {
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);
    const yesterdayKey = yesterday.toISOString().slice(0, 10);
    streak = lastActive === yesterdayKey ? streak + 1 : 1;
    localStorage.setItem(STORAGE_KEYS.streak, String(streak));
    localStorage.setItem(STORAGE_KEYS.lastActive, todayKey);
  }

  streakCount.textContent = `${streak} day${streak === 1 ? "" : "s"}`;
};

const updateProgress = () => {
  const doubts = getSavedItems(STORAGE_KEYS.doubts);
  const quizzes = getSavedItems(STORAGE_KEYS.quizzes);
  const score = doubts.length * 5 + quizzes.length * 10;
  progressScore.textContent = `${score} XP`;
};

const updateMotivation = () => {
  const messages = [
    "Every doubt solved is a step closer to mastery! 🚀",
    "Small quizzes today, big victories tomorrow! 🏆",
    "Your brain loves consistency—keep the streak alive! 🔥",
    "Curiosity is your superpower. Keep asking! ✨",
  ];
  const pick = messages[Math.floor(Math.random() * messages.length)];
  motivationMessage.textContent = pick;
};

const renderSaved = () => {
  const doubts = getSavedItems(STORAGE_KEYS.doubts);
  const quizzes = getSavedItems(STORAGE_KEYS.quizzes);

  savedDoubts.innerHTML = doubts.length
    ? doubts
        .slice(0, 5)
        .map(
          (item) => `
          <div class="vault-card">
            <strong>${item.subject} • ${item.date}</strong>
            <p>${item.question}</p>
            <p>✨ ${item.response}</p>
          </div>
        `,
        )
        .join("")
    : "<p class='muted'>No doubts saved yet.</p>";

  savedQuizzes.innerHTML = quizzes.length
    ? quizzes
        .slice(0, 5)
        .map(
          (item) => `
          <div class="vault-card">
            <strong>${item.topic} • ${item.difficulty}</strong>
            <p>${item.questions.length} questions • ${item.date}</p>
          </div>
        `,
        )
        .join("")
    : "<p class='muted'>No quizzes saved yet.</p>";
};

const updateConnectivity = () => {
  const online = navigator.onLine;
  const statusText = online ? "Online" : "Offline 📡";
  connectionStatus.textContent = statusText;
  chatStatus.textContent = statusText;
  connectionStatus.classList.toggle("offline", !online);
  chatStatus.classList.toggle("offline", !online);

  quizForm.querySelector("button[type='submit']").disabled = !online;
  chatForm.querySelector("button[type='submit']").disabled = !online;
};

const renderQuiz = (data) => {
  quizResults.classList.remove("empty");
  quizResults.innerHTML = "";
  quizSummary.innerHTML = `
    <span>Topic: ${data.topic}</span>
    <span>Difficulty: ${data.difficulty}</span>
    <span>Total Questions: ${data.questions.length}</span>
  `;

  data.questions.forEach((question, index) => {
    const card = document.createElement("article");
    card.className = "quiz-card";

    const heading = document.createElement("h3");
    heading.textContent = `${index + 1}. ${question.question}`;

    const list = document.createElement("ul");
    question.options.forEach((option) => {
      const item = document.createElement("li");
      item.textContent = option;
      if (option === question.answer) {
        item.classList.add("answer");
      }
      list.appendChild(item);
    });

    const explanation = document.createElement("div");
    explanation.className = "explanation";
    explanation.textContent = `Explanation:\n${question.explanation}`;

    const incorrect = document.createElement("ul");
    incorrect.innerHTML = question.incorrect_explanations
      .map((item) => `<li>❌ ${item.option} — ${item.reason}</li>`)
      .join("");

    card.appendChild(heading);
    card.appendChild(list);
    card.appendChild(explanation);
    card.appendChild(incorrect);

    quizResults.appendChild(card);
  });
};

quizForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  quizMessage.textContent = "";
  quizMessage.classList.remove("success");

  const formData = new FormData(quizForm);
  const textValue = formData.get("text").trim();
  const fileValue = formData.get("file");

  if (!textValue && (!fileValue || !fileValue.name)) {
    quizMessage.textContent = "Please paste notes or upload a file first.";
    return;
  }

  if (!navigator.onLine) {
    quizMessage.textContent = "📡 You are offline. Review saved quizzes instead.";
    return;
  }

  showLoading();
  quizForm.querySelector("button[type='submit']").disabled = true;

  try {
    const response = await fetch("/api/generate_quiz", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Unable to generate quiz.");
    }

    const data = await response.json();
    renderQuiz(data);
    quizMessage.textContent = "✅ Quiz generated successfully!";
    quizMessage.classList.add("success");

    const quizzes = getSavedItems(STORAGE_KEYS.quizzes);
    quizzes.unshift({
      topic: data.topic,
      difficulty: data.difficulty,
      questions: data.questions,
      date: new Date().toLocaleDateString(),
    });
    setSavedItems(STORAGE_KEYS.quizzes, quizzes.slice(0, 20));
    updateStreak();
    updateProgress();
    renderSaved();
  } catch (error) {
    quizMessage.textContent = error.message;
    quizResults.classList.add("empty");
    quizResults.innerHTML = `<p>⚠️ ${error.message}</p>`;
  } finally {
    hideLoading();
    quizForm.querySelector("button[type='submit']").disabled = false;
  }
});

generateBtn.addEventListener("click", () => {
  document.getElementById("quiz-panel").scrollIntoView({ behavior: "smooth" });
});

scrollChat.addEventListener("click", () => {
  document.getElementById("chat-panel").scrollIntoView({ behavior: "smooth" });
});

const appendMessage = (text, role = "bot") => {
  const bubble = document.createElement("div");
  bubble.className = `chat-message ${role}`;
  bubble.innerHTML = `<p>${text.replace(/\n/g, "<br />")}</p>`;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
};

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = chatForm.querySelector("input[name='message']");
  const message = input.value.trim();
  const subject = chatForm.querySelector("select[name='subject']").value;
  const fileInput = chatForm.querySelector("input[type='file']");
  const hasFile = fileInput.files.length > 0;

  if (!message && !hasFile) {
    return;
  }

  appendMessage(message || "Uploaded a file for explanation ✨", "user");
  input.value = "";
  chatTips.innerHTML = "";

  if (!navigator.onLine) {
    appendMessage("📡 You are offline. Review saved doubts in the Study Vault.", "bot");
    return;
  }

  showLoading();
  chatForm.querySelector("button[type='submit']").disabled = true;

  try {
    const formData = new FormData(chatForm);
    formData.set("subject", subject);

    const response = await fetch("/api/ask_doubt", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Unable to fetch tutor response.");
    }

    const data = await response.json();
    appendMessage(data.response, "bot");
    if (data.tips?.length) {
      chatTips.innerHTML = data.tips.map((tip) => `💡 ${tip}`).join("<br />");
    }

    const doubts = getSavedItems(STORAGE_KEYS.doubts);
    doubts.unshift({
      question: message || "File-based question",
      response: data.response,
      subject,
      date: new Date().toLocaleDateString(),
    });
    setSavedItems(STORAGE_KEYS.doubts, doubts.slice(0, 20));
    updateStreak();
    updateProgress();
    renderSaved();
  } catch (error) {
    appendMessage(`⚠️ ${error.message}`, "bot");
  } finally {
    hideLoading();
    chatForm.querySelector("button[type='submit']").disabled = false;
  }
});

quizForm.querySelector("input[type='file']").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  fileHint.textContent = file ? `Selected: ${file.name}` : "No file selected.";
  filePreview.classList.remove("active");
  filePreview.textContent = "";

  if (!file || !navigator.onLine) {
    return;
  }

  try {
    const uploadData = new FormData();
    uploadData.append("file", file);
    const response = await fetch("/api/upload_file", {
      method: "POST",
      body: uploadData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Unable to read the file.");
    }

    const data = await response.json();
    const summary = data.summary || "File ready for quiz generation.";
    quizForm.querySelector("textarea[name='text']").value = data.extracted_text || "";
    filePreview.textContent = `✨ Extracted summary: ${summary}`;
    filePreview.classList.add("active");
  } catch (error) {
    filePreview.textContent = `⚠️ ${error.message}`;
    filePreview.classList.add("active");
  }
});

updateConnectivity();
updateStreak();
updateProgress();
updateMotivation();
renderSaved();

window.addEventListener("online", updateConnectivity);
window.addEventListener("offline", updateConnectivity);
