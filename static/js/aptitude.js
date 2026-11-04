/**
 * aptitude.js - Interactive Aptitude Test Engine
 * Manages question navigation, timer, option selection, submission, and instant explanations.
 */

let currentQuestionIndex = 0;
let userAnswers = {}; // { questionId: 'A' | 'B' | 'C' | 'D' }
let timerInterval = null;
let secondsElapsed = 0;

document.addEventListener("DOMContentLoaded", () => {
  const quizContainer = document.getElementById("quizContainer");
  if (!quizContainer) return;

  // Start timer
  startTimer();

  // Setup Option clicks
  setupOptionListeners();

  // Navigation buttons
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");
  const submitBtn = document.getElementById("submitQuizBtn");

  if (prevBtn) {
    prevBtn.addEventListener("click", () => navigateQuestion(-1));
  }
  if (nextBtn) {
    nextBtn.addEventListener("click", () => navigateQuestion(1));
  }
  if (submitBtn) {
    submitBtn.addEventListener("click", confirmAndSubmitQuiz);
  }

  // Update initial view
  updateQuestionView();
});

function startTimer() {
  const timerDisplay = document.getElementById("timerDisplay");
  if (!timerDisplay) return;

  timerInterval = setInterval(() => {
    secondsElapsed++;
    const mins = Math.floor(secondsElapsed / 60)
      .toString()
      .padStart(2, "0");
    const secs = (secondsElapsed % 60).toString().padStart(2, "0");
    timerDisplay.textContent = `${mins}:${secs}`;
  }, 1000);
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
  }
}

function setupOptionListeners() {
  const optionItems = document.querySelectorAll(".option-item");
  optionItems.forEach((item) => {
    item.addEventListener("click", () => {
      const qCard = item.closest(".question-card");
      if (!qCard) return;

      const qId = qCard.getAttribute("data-question-id");
      const selectedOption = item.getAttribute("data-option");

      // Deselect siblings
      qCard.querySelectorAll(".option-item").forEach((el) => {
        el.classList.remove("selected");
      });

      // Select this
      item.classList.add("selected");
      userAnswers[qId] = selectedOption;

      // Update question indicator button if exists
      const indicator = document.getElementById(`nav-dot-${qId}`);
      if (indicator) {
        indicator.classList.add("answered");
      }
    });
  });
}

function navigateQuestion(direction) {
  const cards = document.querySelectorAll(".question-card");
  if (!cards.length) return;

  cards[currentQuestionIndex].style.display = "none";
  currentQuestionIndex += direction;

  if (currentQuestionIndex < 0) currentQuestionIndex = 0;
  if (currentQuestionIndex >= cards.length) currentQuestionIndex = cards.length - 1;

  updateQuestionView();
}

function jumpToQuestion(index) {
  const cards = document.querySelectorAll(".question-card");
  if (index < 0 || index >= cards.length) return;

  cards[currentQuestionIndex].style.display = "none";
  currentQuestionIndex = index;
  updateQuestionView();
}

function updateQuestionView() {
  const cards = document.querySelectorAll(".question-card");
  if (!cards.length) return;

  cards.forEach((c, idx) => {
    c.style.display = idx === currentQuestionIndex ? "block" : "none";
  });

  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");
  const submitBtn = document.getElementById("submitQuizBtn");
  const currentNum = document.getElementById("currentQuestionNum");

  if (currentNum) {
    currentNum.textContent = currentQuestionIndex + 1;
  }

  if (prevBtn) {
    prevBtn.disabled = currentQuestionIndex === 0;
    prevBtn.style.opacity = currentQuestionIndex === 0 ? "0.5" : "1";
  }

  if (nextBtn) {
    if (currentQuestionIndex === cards.length - 1) {
      nextBtn.style.display = "none";
      if (submitBtn) submitBtn.style.display = "inline-flex";
    } else {
      nextBtn.style.display = "inline-flex";
      if (submitBtn) submitBtn.style.display = "none";
    }
  }
}

async function confirmAndSubmitQuiz() {
  const cards = document.querySelectorAll(".question-card");
  const total = cards.length;
  const answeredCount = Object.keys(userAnswers).length;

  if (answeredCount < total) {
    const confirmMsg = `You have answered ${answeredCount} out of ${total} questions. Are you sure you want to finish the test?`;
    if (!confirm(confirmMsg)) return;
  }

  stopTimer();

  const quizCategory = document
    .getElementById("quizContainer")
    .getAttribute("data-category");

  try {
    const res = await fetch("/aptitude/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        category: quizCategory,
        answers: userAnswers,
        time_taken: secondsElapsed,
      }),
    });

    const data = await res.json();
    if (!data.success) {
      alert("Submission error: " + (data.error || "Unknown"));
      return;
    }

    renderQuizResults(data);
  } catch (err) {
    console.error("Submission failed:", err);
    alert("An error occurred while submitting your quiz. Please try again.");
  }
}

function renderQuizResults(data) {
  // Hide test interface, show results view
  document.getElementById("quizTestingView").style.display = "none";
  const resultsView = document.getElementById("quizResultsView");
  resultsView.style.display = "block";

  // Summary scores
  document.getElementById("resScore").textContent = data.score;
  document.getElementById("resTotal").textContent = data.total_questions;
  document.getElementById("resPercentage").textContent = `${data.percentage}%`;

  const reviewList = document.getElementById("feedbackReviewList");
  reviewList.innerHTML = "";

  data.feedback.forEach((item, idx) => {
    const card = document.createElement("div");
    card.className = `feedback-card ${item.is_correct ? "correct" : "incorrect"}`;

    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.75rem;">
        <span style="font-weight:700; color:var(--navy-dark);">Question ${idx + 1} (${item.topic})</span>
        <span class="badge ${item.is_correct ? "badge-selected" : "badge-rejected"}">
          ${item.is_correct ? '<i class="fas fa-check"></i> Correct' : '<i class="fas fa-times"></i> Incorrect'}
        </span>
      </div>
      <p style="font-weight:600; font-size:1.05rem; margin-bottom:1rem; color:var(--navy-dark);">${item.question}</p>
      
      <div style="display:grid; grid-template-columns: 1fr 1fr; gap:1rem; margin-bottom:1rem; font-size:0.9rem;">
        <div style="padding:0.75rem; border-radius:var(--radius-sm); background:${item.is_correct ? '#ecfdf5' : '#fef2f2'}; border:1px solid ${item.is_correct ? '#a7f3d0' : '#fecaca'};">
          <strong style="color:var(--text-muted); display:block; font-size:0.75rem; text-transform:uppercase;">Your Answer</strong>
          <span style="font-weight:700;">Option ${item.user_answer || "Not Answered"}</span>
        </div>
        <div style="padding:0.75rem; border-radius:var(--radius-sm); background:#f0fdfa; border:1px solid #99f6e4;">
          <strong style="color:var(--text-muted); display:block; font-size:0.75rem; text-transform:uppercase;">Correct Answer</strong>
          <span style="font-weight:700; color:#0f766e;">Option ${item.correct_option}: ${item.correct_answer_text}</span>
        </div>
      </div>

      <div class="explanation-box">
        <strong style="color:var(--teal-primary); display:flex; align-items:center; gap:0.4rem; margin-bottom:0.4rem;">
          <i class="fas fa-lightbulb"></i> Step-by-Step Solution & Explanation:
        </strong>
        <p style="line-height:1.6;">${item.explanation}</p>
      </div>
    `;
    reviewList.appendChild(card);
  });

  // Scroll to top of results
  window.scrollTo({ top: 0, behavior: "smooth" });
}
