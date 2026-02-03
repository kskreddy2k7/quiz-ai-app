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

const loadingMessages = [
  "Warming up your brain 🧠✨",
  "Your AI tutor is getting ready 🤖📚",
  "Turning doubts into clarity… 🚀",
];

let loadingIndex = 0;

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

  showLoading();
  quizForm.querySelector("button[type='submit']").disabled = true;

  try {
    const response = await fetch("/api/quiz/generate", {
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
  const input = chatForm.querySelector("input");
  const message = input.value.trim();

  if (!message) {
    return;
  }

  appendMessage(message, "user");
  input.value = "";
  chatTips.innerHTML = "";

  showLoading();
  chatForm.querySelector("button[type='submit']").disabled = true;

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
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
  } catch (error) {
    appendMessage(`⚠️ ${error.message}`, "bot");
  } finally {
    hideLoading();
    chatForm.querySelector("button[type='submit']").disabled = false;
  }
});

quizForm.querySelector("input[type='file']").addEventListener("change", (event) => {
  const file = event.target.files[0];
  fileHint.textContent = file ? `Selected: ${file.name}` : "No file selected.";
});
