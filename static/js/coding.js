/**
 * coding.js - Coding Problem Tracker Interactions
 * Handles add/edit modal population and live filters.
 */

function openEditProblemModal(id, title, platform, language, difficulty, status, url, notes) {
  const form = document.getElementById("editProblemForm");
  if (!form) return;

  form.action = `/coding/edit/${id}`;
  document.getElementById("edit_title").value = title || "";
  document.getElementById("edit_platform").value = platform || "LeetCode";
  document.getElementById("edit_language").value = language || "Python";
  document.getElementById("edit_difficulty").value = difficulty || "Medium";
  document.getElementById("edit_status").value = status || "Solved";
  document.getElementById("edit_problem_url").value = url || "";
  document.getElementById("edit_notes").value = notes || "";

  openModal("editProblemModal");
}
