/**
 * jobs.js - Job Application CRM Tracker Interactions
 * Handles add/edit modal population, dynamic stage updates, and form pre-fills.
 */

function openEditJobModal(id, company, role, date, url, location, ctc, status, notes) {
  const form = document.getElementById("editJobForm");
  if (!form) return;

  form.action = `/jobs/edit/${id}`;
  document.getElementById("edit_company_name").value = company || "";
  document.getElementById("edit_job_role").value = role || "";
  document.getElementById("edit_application_date").value = date || "";
  document.getElementById("edit_job_url").value = url || "";
  document.getElementById("edit_location_type").value = location || "On-Campus";
  document.getElementById("edit_ctc").value = ctc || "Not Disclosed";
  document.getElementById("edit_job_status").value = status || "Applied";
  document.getElementById("edit_job_notes").value = notes || "";

  openModal("editJobModal");
}
