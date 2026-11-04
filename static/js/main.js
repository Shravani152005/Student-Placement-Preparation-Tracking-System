/**
 * main.js - Core UI helpers for Placement Preparation & Tracking System
 * Handles sidebar toggling, modal operations, alert dismissals, and responsive behaviors.
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Mobile Sidebar Toggle
  const mobileToggle = document.getElementById("mobileToggle");
  const sidebar = document.getElementById("sidebar");

  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener("click", () => {
      sidebar.classList.toggle("mobile-open");
    });

    // Close when clicking outside on mobile
    document.addEventListener("click", (e) => {
      if (
        window.innerWidth <= 768 &&
        !sidebar.contains(e.target) &&
        !mobileToggle.contains(e.target) &&
        sidebar.classList.contains("mobile-open")
      ) {
        sidebar.classList.remove("mobile-open");
      }
    });
  }

  // 2. Alert Dismissal
  const alertCloses = document.querySelectorAll(".alert-close");
  alertCloses.forEach((btn) => {
    btn.addEventListener("click", () => {
      const alert = btn.closest(".alert");
      if (alert) {
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 250);
      }
    });
  });

  // Auto-dismiss success alerts after 5 seconds
  const autoAlerts = document.querySelectorAll(".alert-success, .alert-info");
  autoAlerts.forEach((alert) => {
    setTimeout(() => {
      if (alert && alert.parentElement) {
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 250);
      }
    }, 5000);
  });
});

// Modal Helpers
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add("show");
    document.body.style.overflow = "hidden";
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove("show");
    document.body.style.overflow = "auto";
  }
}

// Close modal if user clicks on backdrop
window.addEventListener("click", (e) => {
  if (e.target.classList.contains("modal-backdrop")) {
    e.target.classList.remove("show");
    document.body.style.overflow = "auto";
  }
});
