/**
 * interview.js - Interview Preparation Hub Interactions
 * Handles accordion expansion, category tabs, and instantaneous keyword search.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Accordion Toggle
  const cardHeaders = document.querySelectorAll(".interview-card-header");
  cardHeaders.forEach((header) => {
    header.addEventListener("click", () => {
      const card = header.closest(".interview-card");
      if (card) {
        card.classList.toggle("open");
      }
    });
  });

  // Client-side quick filter search (instant response)
  const searchInput = document.getElementById("interviewSearchInput");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const query = e.target.value.toLowerCase().trim();
      const cards = document.querySelectorAll(".interview-card");

      cards.forEach((card) => {
        const text = card.textContent.toLowerCase();
        if (text.includes(query)) {
          card.style.display = "block";
        } else {
          card.style.display = "none";
        }
      });
    });
  }
});
