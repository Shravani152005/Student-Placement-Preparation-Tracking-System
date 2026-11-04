"""
app.py - Main Flask Application for Student Placement Preparation & Tracking System
Implements authentication, dashboard metrics, aptitude testing, coding problem tracking,
job CRM application pipeline, interview preparation, and student profiles.
"""

import os
from functools import wraps
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, jsonify, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
import database

app = Flask(__name__)
# Secret key for session signing
app.secret_key = os.environ.get("SECRET_KEY", "placement_prep_super_secret_key_2026")


# --- AUTHENTICATION HELPER & DECORATOR ---

def login_required(f):
    """Decorator to require login on protected student pages."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "student_id" not in session:
            flash("Please sign in to access your placement dashboard.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_current_student():
    """Injects current logged-in student into all templates for navbar/sidebar."""
    if "student_id" in session:
        student = database.get_student_by_id(session["student_id"])
        return {"current_student": student}
    return {"current_student": None}


# --- 1. HOME & LANDING PAGE ---

@app.route("/")
def index():
    """Public SaaS landing page with features, statistics, and call-to-actions."""
    if "student_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


# --- 2. AUTHENTICATION (REGISTER, LOGIN, LOGOUT) ---

@app.route("/register", methods=["GET", "POST"])
def register():
    """Handles student registration with validation and password hashing."""
    if "student_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        college = request.form.get("college", "").strip()
        branch = request.form.get("branch", "Computer Science & Engineering").strip()
        grad_year = request.form.get("grad_year", "2026").strip()
        target_role = request.form.get("target_role", "Software Development Engineer").strip()

        # Input Validation
        if not name or not email or not password or not college:
            flash("Please fill in all required fields (Name, Email, Password, College).", "danger")
            return render_template("auth/register.html", form_data=request.form)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("auth/register.html", form_data=request.form)

        if password != confirm_password:
            flash("Passwords do not match. Please verify.", "danger")
            return render_template("auth/register.html", form_data=request.form)

        # Check existing student
        existing_student = database.get_student_by_email(email)
        if existing_student:
            flash("An account with this email address already exists. Please log in.", "danger")
            return redirect(url_for("login"))

        try:
            conn = database.get_db()
            cursor = conn.cursor()
            pwd_hash = generate_password_hash(password)
            
            cursor.execute("""
            INSERT INTO students (name, email, password_hash, college, branch, grad_year, target_role)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, email, pwd_hash, college, branch, int(grad_year) if grad_year.isdigit() else 2026, target_role))
            student_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # Log registration activity
            database.log_activity(student_id, "profile", "Created student account and completed initial setup")

            # Set session
            session["student_id"] = student_id
            session["student_name"] = name
            flash(f"Welcome to Placement Tracker, {name}! Your account has been created successfully.", "success")
            return redirect(url_for("dashboard"))

        except Exception as e:
            flash(f"Error during registration: {str(e)}", "danger")
            return render_template("auth/register.html", form_data=request.form)

    return render_template("auth/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles student authentication and session establishment."""
    if "student_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password.", "warning")
            return render_template("auth/login.html")

        student = database.get_student_by_email(email)
        if not student or not check_password_hash(student["password_hash"], password):
            flash("Invalid email or password. Please check your credentials.", "danger")
            return render_template("auth/login.html")

        # Success: Set session
        session["student_id"] = student["id"]
        session["student_name"] = student["name"]
        flash(f"Welcome back, {student['name']}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("auth/login.html")


@app.route("/logout")
def logout():
    """Terminates student session and redirects to login."""
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("login"))


# --- 3. DASHBOARD ---

@app.route("/dashboard")
@login_required
def dashboard():
    """Student central SaaS dashboard with live metrics, charts, and activity feed."""
    student_id = session["student_id"]
    student = database.get_student_by_id(student_id)
    if not student:
        session.clear()
        return redirect(url_for("login"))

    metrics = database.get_dashboard_metrics(student_id)

    # Get recent coding problems (last 4)
    conn = database.get_db()
    recent_coding = conn.execute("""
        SELECT * FROM coding_problems
        WHERE student_id = ?
        ORDER BY id DESC LIMIT 4
    """, (student_id,)).fetchall()

    # Get recent job applications (last 4)
    recent_jobs = conn.execute("""
        SELECT * FROM job_applications
        WHERE student_id = ?
        ORDER BY id DESC LIMIT 4
    """, (student_id,)).fetchall()
    conn.close()

    return render_template(
        "dashboard/index.html",
        student=student,
        metrics=metrics,
        recent_coding=recent_coding,
        recent_jobs=recent_jobs
    )


@app.route("/api/dashboard-charts")
@login_required
def dashboard_charts_api():
    """Provides dynamic JSON data for dashboard Chart.js widgets."""
    student_id = session["student_id"]
    metrics = database.get_dashboard_metrics(student_id)

    # Job status distribution
    job_labels = ["Applied", "Shortlisted", "Interview", "Selected", "Rejected"]
    job_data = [
        metrics["jobs_applied"],
        metrics["jobs_shortlisted"],
        metrics["jobs_interview"],
        metrics["jobs_selected"],
        metrics["jobs_rejected"]
    ]

    # Coding difficulty breakdown
    coding_labels = ["Easy Solved", "Medium Solved", "Hard Solved", "In Progress", "Need Revision"]
    coding_data = [
        metrics["coding_easy_solved"],
        metrics["coding_med_solved"],
        metrics["coding_hard_solved"],
        metrics["coding_in_progress"],
        metrics["coding_revision"]
    ]

    # Aptitude history
    apt_labels = []
    apt_scores = []
    for test in metrics["aptitude_history"]:
        formatted_date = test["completed_at"][:10] if test["completed_at"] else "Test"
        apt_labels.append(f"{test['category']} ({formatted_date})")
        apt_scores.append(test["percentage"])

    if not apt_scores:
        apt_labels = ["No Tests Yet"]
        apt_scores = [0]

    return jsonify({
        "job_distribution": {
            "labels": job_labels,
            "data": job_data
        },
        "coding_distribution": {
            "labels": coding_labels,
            "data": coding_data
        },
        "aptitude_trend": {
            "labels": apt_labels,
            "data": apt_scores
        },
        "readiness_score": metrics["readiness_score"]
    })


# --- 4. APTITUDE PRACTICE ---

@app.route("/aptitude")
@login_required
def aptitude_index():
    """Aptitude practice hub showing topic cards, category stats, and previous test history."""
    student_id = session["student_id"]
    conn = database.get_db()

    # Get test history for student
    history = conn.execute("""
        SELECT * FROM aptitude_results
        WHERE student_id = ?
        ORDER BY id DESC
    """, (student_id,)).fetchall()

    # Category stats
    stats_query = conn.execute("""
        SELECT 
            category,
            COUNT(*) as test_count,
            COALESCE(AVG(percentage), 0) as avg_score,
            MAX(percentage) as best_score
        FROM aptitude_results
        WHERE student_id = ?
        GROUP BY category
    """, (student_id,)).fetchall()

    category_stats = {row["category"]: dict(row) for row in stats_query}

    # Available questions count per category
    q_counts = conn.execute("""
        SELECT category, COUNT(*) as count
        FROM aptitude_questions
        GROUP BY category
    """).fetchall()
    q_count_map = {row["category"]: row["count"] for row in q_counts}

    conn.close()

    return render_template(
        "aptitude/index.html",
        history=history,
        category_stats=category_stats,
        q_count_map=q_count_map
    )


@app.route("/aptitude/practice")
@login_required
def aptitude_practice():
    """Interactive aptitude quiz test room."""
    category = request.args.get("category", "Quantitative").strip()
    limit = int(request.args.get("limit", 10))

    conn = database.get_db()
    if category.lower() == "all" or category.lower() == "mixed":
        questions = conn.execute("""
            SELECT * FROM aptitude_questions
            ORDER BY RANDOM()
            LIMIT ?
        """, (limit,)).fetchall()
        display_category = "Comprehensive Mixed Test"
    else:
        questions = conn.execute("""
            SELECT * FROM aptitude_questions
            WHERE category = ?
            ORDER BY RANDOM()
            LIMIT ?
        """, (category, limit)).fetchall()
        display_category = category

    conn.close()

    if not questions:
        flash(f"No questions found for category: {category}", "warning")
        return redirect(url_for("aptitude_index"))

    return render_template(
        "aptitude/practice.html",
        questions=questions,
        category=display_category,
        total_questions=len(questions)
    )


@app.route("/aptitude/submit", methods=["POST"])
@login_required
def aptitude_submit():
    """
    Evaluates submitted aptitude quiz responses.
    Calculates score, stores results, logs student activity, and returns explanations.
    """
    student_id = session["student_id"]
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Invalid request payload"}), 400

    category = data.get("category", "Aptitude Practice")
    answers = data.get("answers", {})  # { question_id_str: 'A' / 'B' / 'C' / 'D' }
    time_taken = int(data.get("time_taken", 0))

    conn = database.get_db()
    cursor = conn.cursor()

    total_questions = len(answers)
    if total_questions == 0:
        return jsonify({"success": False, "error": "No answers submitted"}), 400

    score = 0
    feedback = []

    for q_id_str, user_ans in answers.items():
        try:
            q_id = int(q_id_str)
        except ValueError:
            continue

        q = cursor.execute("SELECT * FROM aptitude_questions WHERE id = ?", (q_id,)).fetchone()
        if q:
            is_correct = (user_ans.strip().upper() == q["correct_option"].strip().upper())
            if is_correct:
                score += 1
            feedback.append({
                "id": q["id"],
                "question": q["question_text"],
                "topic": q["topic"],
                "user_answer": user_ans.strip().upper(),
                "correct_option": q["correct_option"],
                "correct_answer_text": q[f"option_{q['correct_option'].lower()}"],
                "is_correct": is_correct,
                "explanation": q["explanation"]
            })

    percentage = round((score / total_questions) * 100, 1)

    # Save to database
    cursor.execute("""
        INSERT INTO aptitude_results (student_id, category, score, total_questions, percentage, time_taken_seconds)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (student_id, category, score, total_questions, percentage, time_taken))
    conn.commit()
    conn.close()

    # Log activity
    database.log_activity(
        student_id,
        "aptitude",
        f"Completed {category} practice test: Scored {score}/{total_questions} ({percentage}%)"
    )

    return jsonify({
        "success": True,
        "score": score,
        "total_questions": total_questions,
        "percentage": percentage,
        "feedback": feedback
    })


# --- 5. CODING PRACTICE TRACKER ---

@app.route("/coding")
@login_required
def coding_index():
    """Coding problems tracker with search, filters, difficulty statistics, and problem list."""
    student_id = session["student_id"]
    difficulty_filter = request.args.get("difficulty", "all")
    status_filter = request.args.get("status", "all")
    language_filter = request.args.get("language", "all")
    search_query = request.args.get("q", "").strip()

    conn = database.get_db()

    query = "SELECT * FROM coding_problems WHERE student_id = ?"
    params = [student_id]

    if difficulty_filter != "all":
        query += " AND difficulty = ?"
        params.append(difficulty_filter)
    if status_filter != "all":
        query += " AND status = ?"
        params.append(status_filter)
    if language_filter != "all":
        query += " AND language = ?"
        params.append(language_filter)
    if search_query:
        query += " AND (title LIKE ? OR notes LIKE ? OR platform LIKE ?)"
        term = f"%{search_query}%"
        params.extend([term, term, term])

    query += " ORDER BY id DESC"
    problems = conn.execute(query, params).fetchall()

    # Overall stats for summary cards
    stats = conn.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Solved' THEN 1 ELSE 0 END) as solved,
            SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
            SUM(CASE WHEN status = 'Need Revision' THEN 1 ELSE 0 END) as revision,
            SUM(CASE WHEN difficulty = 'Easy' AND status = 'Solved' THEN 1 ELSE 0 END) as easy_solved,
            SUM(CASE WHEN difficulty = 'Medium' AND status = 'Solved' THEN 1 ELSE 0 END) as med_solved,
            SUM(CASE WHEN difficulty = 'Hard' AND status = 'Solved' THEN 1 ELSE 0 END) as hard_solved
        FROM coding_problems
        WHERE student_id = ?
    """, (student_id,)).fetchone()

    conn.close()

    return render_template(
        "coding/index.html",
        problems=problems,
        stats=stats,
        difficulty_filter=difficulty_filter,
        status_filter=status_filter,
        language_filter=language_filter,
        search_query=search_query
    )


@app.route("/coding/add", methods=["POST"])
@login_required
def coding_add():
    """Adds a new coding problem to the student's tracker."""
    student_id = session["student_id"]
    title = request.form.get("title", "").strip()
    platform = request.form.get("platform", "LeetCode").strip()
    language = request.form.get("language", "Python").strip()
    difficulty = request.form.get("difficulty", "Medium").strip()
    status = request.form.get("status", "Solved").strip()
    problem_url = request.form.get("problem_url", "").strip()
    notes = request.form.get("notes", "").strip()

    if not title:
        flash("Problem name/title is required.", "danger")
        return redirect(url_for("coding_index"))

    conn = database.get_db()
    conn.execute("""
        INSERT INTO coding_problems (student_id, title, platform, language, difficulty, status, problem_url, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (student_id, title, platform, language, difficulty, status, problem_url, notes))
    conn.commit()
    conn.close()

    database.log_activity(student_id, "coding", f"Logged coding problem: '{title}' ({difficulty}, {status})")
    flash(f"Problem '{title}' added to your tracker!", "success")
    return redirect(url_for("coding_index"))


@app.route("/coding/edit/<int:problem_id>", methods=["POST"])
@login_required
def coding_edit(problem_id):
    """Updates an existing coding problem."""
    student_id = session["student_id"]
    title = request.form.get("title", "").strip()
    platform = request.form.get("platform", "LeetCode").strip()
    language = request.form.get("language", "Python").strip()
    difficulty = request.form.get("difficulty", "Medium").strip()
    status = request.form.get("status", "Solved").strip()
    problem_url = request.form.get("problem_url", "").strip()
    notes = request.form.get("notes", "").strip()

    if not title:
        flash("Problem title cannot be empty.", "danger")
        return redirect(url_for("coding_index"))

    conn = database.get_db()
    conn.execute("""
        UPDATE coding_problems
        SET title = ?, platform = ?, language = ?, difficulty = ?, status = ?, problem_url = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND student_id = ?
    """, (title, platform, language, difficulty, status, problem_url, notes, problem_id, student_id))
    conn.commit()
    conn.close()

    flash(f"Problem '{title}' updated successfully.", "success")
    return redirect(url_for("coding_index"))


@app.route("/coding/toggle-status/<int:problem_id>", methods=["POST"])
@login_required
def coding_toggle_status(problem_id):
    """Quickly updates problem status (e.g. from table action button)."""
    student_id = session["student_id"]
    new_status = request.form.get("status", "Solved").strip()

    conn = database.get_db()
    conn.execute("""
        UPDATE coding_problems
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND student_id = ?
    """, (new_status, problem_id, student_id))
    conn.commit()
    conn.close()

    flash(f"Problem status updated to '{new_status}'.", "info")
    return redirect(url_for("coding_index"))


@app.route("/coding/delete/<int:problem_id>", methods=["POST"])
@login_required
def coding_delete(problem_id):
    """Deletes a coding problem from student's record."""
    student_id = session["student_id"]
    conn = database.get_db()
    conn.execute("DELETE FROM coding_problems WHERE id = ? AND student_id = ?", (problem_id, student_id))
    conn.commit()
    conn.close()

    flash("Coding problem removed from tracker.", "info")
    return redirect(url_for("coding_index"))


# --- 6. JOB APPLICATION TRACKER ---

@app.route("/jobs")
@login_required
def jobs_index():
    """Job application CRM pipeline tracking applications, stages, CTC, and statistics."""
    student_id = session["student_id"]
    status_filter = request.args.get("status", "all")
    search_query = request.args.get("q", "").strip()

    conn = database.get_db()

    query = "SELECT * FROM job_applications WHERE student_id = ?"
    params = [student_id]

    if status_filter != "all":
        query += " AND status = ?"
        params.append(status_filter)
    if search_query:
        query += " AND (company_name LIKE ? OR job_role LIKE ? OR notes LIKE ?)"
        term = f"%{search_query}%"
        params.extend([term, term, term])

    query += " ORDER BY application_date DESC, id DESC"
    applications = conn.execute(query, params).fetchall()

    # Job Statistics
    stats = conn.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Applied' THEN 1 ELSE 0 END) as applied,
            SUM(CASE WHEN status = 'Shortlisted' THEN 1 ELSE 0 END) as shortlisted,
            SUM(CASE WHEN status = 'Interview' THEN 1 ELSE 0 END) as interview,
            SUM(CASE WHEN status = 'Selected' THEN 1 ELSE 0 END) as selected,
            SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END) as rejected
        FROM job_applications
        WHERE student_id = ?
    """, (student_id,)).fetchone()

    conn.close()

    return render_template(
        "jobs/index.html",
        applications=applications,
        stats=stats,
        status_filter=status_filter,
        search_query=search_query
    )


@app.route("/jobs/add", methods=["POST"])
@login_required
def jobs_add():
    """Adds a new job application to student's pipeline."""
    student_id = session["student_id"]
    company_name = request.form.get("company_name", "").strip()
    job_role = request.form.get("job_role", "").strip()
    application_date = request.form.get("application_date", datetime.today().strftime('%Y-%m-%d'))
    job_url = request.form.get("job_url", "").strip()
    location_type = request.form.get("location_type", "On-Campus").strip()
    ctc = request.form.get("ctc", "Not Disclosed").strip()
    status = request.form.get("status", "Applied").strip()
    notes = request.form.get("notes", "").strip()

    if not company_name or not job_role:
        flash("Company name and job role are required.", "danger")
        return redirect(url_for("jobs_index"))

    conn = database.get_db()
    conn.execute("""
        INSERT INTO job_applications (student_id, company_name, job_role, application_date, job_url, location_type, ctc, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (student_id, company_name, job_role, application_date, job_url, location_type, ctc, status, notes))
    conn.commit()
    conn.close()

    database.log_activity(student_id, "job", f"Added job application for {company_name} - {job_role} ({status})")
    flash(f"Application for {company_name} ({job_role}) added successfully!", "success")
    return redirect(url_for("jobs_index"))


@app.route("/jobs/edit/<int:job_id>", methods=["POST"])
@login_required
def jobs_edit(job_id):
    """Updates an existing job application record."""
    student_id = session["student_id"]
    company_name = request.form.get("company_name", "").strip()
    job_role = request.form.get("job_role", "").strip()
    application_date = request.form.get("application_date", "").strip()
    job_url = request.form.get("job_url", "").strip()
    location_type = request.form.get("location_type", "On-Campus").strip()
    ctc = request.form.get("ctc", "Not Disclosed").strip()
    status = request.form.get("status", "Applied").strip()
    notes = request.form.get("notes", "").strip()

    if not company_name or not job_role:
        flash("Company name and job role cannot be empty.", "danger")
        return redirect(url_for("jobs_index"))

    conn = database.get_db()
    conn.execute("""
        UPDATE job_applications
        SET company_name = ?, job_role = ?, application_date = ?, job_url = ?,
            location_type = ?, ctc = ?, status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND student_id = ?
    """, (company_name, job_role, application_date, job_url, location_type, ctc, status, notes, job_id, student_id))
    conn.commit()
    conn.close()

    database.log_activity(student_id, "job", f"Updated application status for {company_name} to {status}")
    flash(f"Application for {company_name} updated successfully.", "success")
    return redirect(url_for("jobs_index"))


@app.route("/jobs/status/<int:job_id>", methods=["POST"])
@login_required
def jobs_update_status(job_id):
    """Quickly updates application status from pipeline view."""
    student_id = session["student_id"]
    new_status = request.form.get("status", "Applied").strip()

    conn = database.get_db()
    conn.execute("""
        UPDATE job_applications
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND student_id = ?
    """, (new_status, job_id, student_id))
    conn.commit()
    conn.close()

    flash(f"Application stage updated to '{new_status}'.", "info")
    return redirect(url_for("jobs_index"))


@app.route("/jobs/delete/<int:job_id>", methods=["POST"])
@login_required
def jobs_delete(job_id):
    """Deletes an application from pipeline."""
    student_id = session["student_id"]
    conn = database.get_db()
    conn.execute("DELETE FROM job_applications WHERE id = ? AND student_id = ?", (job_id, student_id))
    conn.commit()
    conn.close()

    flash("Job application deleted.", "info")
    return redirect(url_for("jobs_index"))


# --- 7. INTERVIEW PREPARATION ---

@app.route("/interview")
@login_required
def interview_index():
    """Curated technical and HR interview questions organized by categories."""
    student_id = session["student_id"]
    category_filter = request.args.get("category", "all")
    search_query = request.args.get("q", "").strip()

    conn = database.get_db()

    query = """
        SELECT i.*, COALESCE(p.is_mastered, 0) as is_mastered
        FROM interview_questions i
        LEFT JOIN student_interview_progress p
            ON i.id = p.question_id AND p.student_id = ?
        WHERE 1=1
    """
    params = [student_id]

    if category_filter != "all":
        query += " AND i.category = ?"
        params.append(category_filter)
    if search_query:
        query += " AND (i.question_text LIKE ? OR i.answer_text LIKE ? OR i.topic LIKE ?)"
        term = f"%{search_query}%"
        params.extend([term, term, term])

    query += " ORDER BY i.category, i.id"
    questions = conn.execute(query, params).fetchall()

    # Category summary counts
    cat_summary = conn.execute("""
        SELECT 
            i.category,
            COUNT(i.id) as total,
            COALESCE(SUM(CASE WHEN p.is_mastered = 1 THEN 1 ELSE 0 END), 0) as mastered
        FROM interview_questions i
        LEFT JOIN student_interview_progress p
            ON i.id = p.question_id AND p.student_id = ?
        GROUP BY i.category
    """, (student_id,)).fetchall()

    conn.close()

    return render_template(
        "interview/index.html",
        questions=questions,
        cat_summary=cat_summary,
        category_filter=category_filter,
        search_query=search_query
    )


@app.route("/interview/toggle-mastered/<int:question_id>", methods=["POST"])
@login_required
def interview_toggle_mastered(question_id):
    """Toggles student's mastered status on an interview question."""
    student_id = session["student_id"]
    conn = database.get_db()
    cursor = conn.cursor()

    row = cursor.execute("""
        SELECT is_mastered FROM student_interview_progress
        WHERE student_id = ? AND question_id = ?
    """, (student_id, question_id)).fetchone()

    if row is None:
        new_val = 1
        cursor.execute("""
            INSERT INTO student_interview_progress (student_id, question_id, is_mastered)
            VALUES (?, ?, 1)
        """, (student_id, question_id))
    else:
        new_val = 0 if row["is_mastered"] == 1 else 1
        cursor.execute("""
            UPDATE student_interview_progress
            SET is_mastered = ?, updated_at = CURRENT_TIMESTAMP
            WHERE student_id = ? AND question_id = ?
        """, (new_val, student_id, question_id))

    conn.commit()
    conn.close()

    status_msg = "Marked as Mastered!" if new_val == 1 else "Unmarked question."
    flash(status_msg, "success" if new_val == 1 else "info")
    return redirect(request.referrer or url_for("interview_index"))


# --- 8. PROFILE PAGE ---

@app.route("/profile")
@login_required
def profile_index():
    """Student profile view with academic details and preparation statistics."""
    student_id = session["student_id"]
    student = database.get_student_by_id(student_id)
    metrics = database.get_dashboard_metrics(student_id)

    return render_template(
        "profile/index.html",
        student=student,
        metrics=metrics
    )


@app.route("/profile/update", methods=["POST"])
@login_required
def profile_update():
    """Updates student profile information."""
    student_id = session["student_id"]
    name = request.form.get("name", "").strip()
    college = request.form.get("college", "").strip()
    branch = request.form.get("branch", "").strip()
    grad_year = request.form.get("grad_year", "2026").strip()
    cgpa = request.form.get("cgpa", "8.0").strip()
    phone = request.form.get("phone", "").strip()
    bio = request.form.get("bio", "").strip()
    target_role = request.form.get("target_role", "").strip()
    linkedin = request.form.get("linkedin", "").strip()
    github = request.form.get("github", "").strip()

    if not name or not college:
        flash("Full name and College name are required.", "danger")
        return redirect(url_for("profile_index"))

    conn = database.get_db()
    conn.execute("""
        UPDATE students
        SET name = ?, college = ?, branch = ?, grad_year = ?, cgpa = ?,
            phone = ?, bio = ?, target_role = ?, linkedin = ?, github = ?
        WHERE id = ?
    """, (
        name, college, branch,
        int(grad_year) if grad_year.isdigit() else 2026,
        float(cgpa) if cgpa.replace('.', '', 1).isdigit() else 8.0,
        phone, bio, target_role, linkedin, github, student_id
    ))
    conn.commit()
    conn.close()

    # Update session name if changed
    session["student_name"] = name
    database.log_activity(student_id, "profile", "Updated student profile details")
    flash("Profile updated successfully!", "success")
    return redirect(url_for("profile_index"))


@app.route("/profile/change-password", methods=["POST"])
@login_required
def profile_change_password():
    """Securely updates student password."""
    student_id = session["student_id"]
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if len(new_password) < 6:
        flash("New password must be at least 6 characters long.", "danger")
        return redirect(url_for("profile_index"))

    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for("profile_index"))

    student = database.get_student_by_id(student_id)
    if not check_password_hash(student["password_hash"], current_password):
        flash("Incorrect current password.", "danger")
        return redirect(url_for("profile_index"))

    conn = database.get_db()
    conn.execute("UPDATE students SET password_hash = ? WHERE id = ?", (generate_password_hash(new_password), student_id))
    conn.commit()
    conn.close()

    flash("Password changed successfully!", "success")
    return redirect(url_for("profile_index"))


# --- APPLICATION ENTRY POINT ---

if __name__ == "__main__":
    # Ensure database tables and initial seed data exist
    database.init_db()
    print("=" * 60)
    print("Student Placement Preparation & Tracking System")
    print("Server starting on http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host="127.0.0.1", port=5000)
