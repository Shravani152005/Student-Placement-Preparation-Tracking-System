# Student Placement Preparation & Tracking System (PlacementTrack)

A modern, responsive, SaaS-grade web application built to empower college students to systematically prepare for campus recruitment drives, practice aptitude tests, track coding problem milestones, manage job application stages, and monitor overall placement readiness.

---

## 🌟 Highlights & Key Features

1. **Modern SaaS Landing Page**
   - High-converting hero presentation with dark navy, white, and teal color scheme.
   - Live preparation statistics counter (30+ questions, 5 categories, 5 job stages).
   - Module breakdown, 3-step workflow, and instant access buttons.

2. **Secure Student Authentication & Sessions**
   - Student registration with full validation: Name, Email, Password, College, Branch, Graduation Year, and Target Job Role.
   - Passwords cryptographically hashed using PBKDF2/SHA-256 via Werkzeug (`generate_password_hash`).
   - Session-based access control protecting all student features (`@login_required`).
   - Quick **1-Click Demo Login** button pre-filled with `demo@student.edu`.

3. **Placement Analytics Dashboard**
   - Welcome banner with student name, graduation batch, and target role.
   - Dynamic metric cards: Aptitude tests attempted, coding challenges solved, job applications, and shortlisted offers.
   - **Composite Placement Readiness Score (0 - 100%)**: Dynamically calculated across aptitude accuracy, coding solved volume, interview preparation, and job application tracking.
   - **Interactive Chart.js Visualizations**:
     - *Aptitude Score Performance Progression* (Smooth line chart with teal gradient).
     - *Job Application Pipeline Breakdown* (Color-coded doughnut chart).
     - *Coding Solved by Difficulty* (Horizontal bar chart).
   - Live activity timeline tracking test completions, job updates, and coding milestones.

4. **Aptitude Practice Engine**
   - 30 pre-seeded placement questions across:
     - **Quantitative Aptitude**: Time & Work, Percentages, Profit & Loss, Speed & Distance, Averages, Compound Interest, Probability, etc.
     - **Logical Reasoning**: Number Series, Blood Relations, Coding-Decoding, Syllogisms, Seating Arrangement, Direction Sense.
     - **Verbal Ability**: Synonyms, Antonyms, Sentence Correction, Idioms, Error Spotting, Comprehension.
   - Full mock test mode (15 randomized mixed questions).
   - Interactive quiz interface: Live timer, question counter, 4 clickable options (A, B, C, D), and review before submission.
   - **Automated Instant Evaluation**: Shows exact score, percentage, user's answer vs. correct answer, and **detailed step-by-step mathematical/logical explanations**.
   - All results permanently stored in SQLite per student.

5. **Coding Practice Tracker**
   - Log coding problems solved across LeetCode, HackerRank, GeeksforGeeks, CodeChef, and Codeforces.
   - Records title, platform, language (Python, Java, C++, C, JavaScript), difficulty (Easy, Medium, Hard), status (Solved, In Progress, Need Revision), URL, and personal algorithmic notes.
   - Fast multi-criteria filtering: By Difficulty, Status, Language, and real-time Search.
   - In-place quick status change dropdown (`🟢 Solved`, `🟡 In Progress`, `🔴 Need Revision`).
   - Add, Edit, and Delete modals.

6. **Job Application Tracker (Recruitment CRM)**
   - Track campus and off-campus recruitment pipelines.
   - Fields: Company Name, Role, Drive Type (On-Campus, Off-Campus, Remote, Hybrid), CTC/Package, Application Date, Career Link, and Interview Notes.
   - Standard 5-stage pipeline: `Applied` ➔ `Shortlisted` ➔ `Interview` ➔ `Selected (Offer)` ➔ `Rejected`.
   - Direct stage update dropdown and full CRUD (Add, Edit, Delete).
   - Application conversion metrics counter.

7. **Curated Interview Preparation Hub**
   - Categorized repository of top corporate placement interview questions:
     - **Java**: JVM/JRE/JDK, String Immutability, Memory, ConcurrentHashMap, Checked vs Unchecked Exceptions.
     - **Python**: GIL, Lists vs Tuples, Generators/Yield, Deep vs Shallow Copy.
     - **SQL**: Joins, B-Tree Indexing trade-offs, ACID transactions, Nth highest salary.
     - **OOPs**: 4 Pillars, SOLID principles, Overloading vs Overriding.
     - **HR & Behavioral**: "Tell me about yourself", Strengths/Weaknesses, Why this company?, Conflict resolution using STAR method.
   - Interactive accordion cards that smoothly reveal model answers and **Interviewer Pro-Tips**.
   - Student **"Mark as Mastered"** toggle button that persists progress and contributes to readiness score.
   - Live client-side instant search filter.

8. **Student Profile Management**
   - View and update academic details, CGPA, department, graduation year, target placement role, phone number, and career bio.
   - Add links to LinkedIn and GitHub profiles.
   - Placement Readiness Meter with animated progress bar.
   - Secure password update form.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.x, Flask 3.1
- **Database**: SQLite3 (Standard Python Library, zero external DB configuration required)
- **Frontend**: HTML5, CSS3 (Modern Flexbox, CSS Grid, Custom Variables), Vanilla JavaScript (ES6+)
- **Charts & Visualizations**: Chart.js 4 (via CDN)
- **Icons & Typography**: Font Awesome 6, Plus Jakarta Sans, JetBrains Mono

---

## 📁 Project Directory Structure

```
placement_prep_system/
│
├── app.py                      # Flask routes, authentication decorator, business logic & API
├── database.py                 # SQLite schema, WAL mode, seeds (30 Aptitude Qs, 20 Interview Qs, Demo Student)
├── requirements.txt            # Python dependencies (Flask, Werkzeug)
├── test_app.py                 # Automated test suite (11 end-to-end tests)
├── README.md                   # Complete documentation and setup guide
│
├── static/
│   ├── css/
│   │   ├── style.css           # Global design system, dark navy/teal palette, sidebar, tables, modals
│   │   ├── dashboard.css       # Analytics widgets, cards, aptitude quiz styles, accordions, profile meter
│   │   └── landing.css         # SaaS landing page styles, hero gradients, stats banner, features grid
│   └── js/
│       ├── main.js             # Mobile sidebar toggle, alert dismissal, modal dialog helpers
│       ├── dashboard.js        # Dynamic Chart.js visualizations (Aptitude trend, Job CRM donut, Coding bar)
│       ├── aptitude.js         # Interactive test runner, stopwatch timer, score calculator, explanation renderer
│       ├── coding.js           # Coding tracker modal populate & status handlers
│       ├── jobs.js             # Job CRM modal populate & status handlers
│       └── interview.js        # Accordion toggles and real-time question search
│
└── templates/
    ├── base.html               # Base HTML skeleton with CDNs and meta headers
    ├── dashboard_base.html     # SaaS app shell (Sidebar, Topbar, Readiness pill, User chip)
    ├── index.html              # High-converting public Landing Page
    ├── auth/
    │   ├── login.html          # Student Login with 1-click Demo Fill
    │   └── register.html       # Student Registration with input validation
    ├── dashboard/
    │   └── index.html          # Central Dashboard (Metrics, Charts, Activities, Quick Actions)
    ├── aptitude/
    │   ├── index.html          # Aptitude Categories, Topic Counts & Test History
    │   └── practice.html       # Interactive Quiz Environment & Step-by-Step Solutions
    ├── coding/
    │   └── index.html          # Algorithmic Coding Problem Tracker
    ├── jobs/
    │   └── index.html          # Job Application CRM Pipeline
    ├── interview/
    │   └── interview.html      # Technical & HR Interview Question Bank
    └── profile/
        └── index.html          # Student Academic Profile & Security Settings
```

---

## 🚀 Beginner-Friendly Setup & Execution Guide

Follow these exact steps in your terminal (PowerShell, Command Prompt, or Terminal):

### Step 1: Open Terminal & Navigate to Project Folder
```powershell
cd C:\Users\BSRAV\Desktop\PROJECTS\placement_prep_system
```

### Step 2: (Optional but Recommended) Create & Activate a Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Or on Windows (Command Prompt):
.\venv\Scripts\activate.bat
```

### Step 3: Install Required Packages
```powershell
pip install -r requirements.txt
```
*(Only Flask and Werkzeug are required; SQLite is already built into Python!)*

### Step 4: Run the Application
```powershell
python app.py
```

The database (`placement_system.db`) will automatically initialize and seed on the first run.
You will see output similar to:
```
============================================================
Student Placement Preparation & Tracking System
Server starting on http://127.0.0.1:5000
============================================================
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Step 5: Open in Your Browser
Open your web browser (Chrome, Edge, Firefox, Brave) and visit:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 Login Credentials

### 1. Ready-To-Use Demo Account
You can immediately evaluate the platform with pre-populated realistic placement records:
- **Email:** `demo@student.edu`
- **Password:** `demo123`
*(On the login screen, simply click the **"⚡ Auto-fill Demo"** button to fill these credentials with one click).*

### 2. Create Your Own Student Account
Click **"Register"** or **"Get Started Free"**, enter your college name, branch, graduation year, target job role, and password to initialize a clean, personal tracking database.

---

## 🧪 Running Automated Unit & Integration Tests

The project includes an automated test suite verifying all 11 core functional flows:
```powershell
python test_app.py
```

Expected output:
```
...........
----------------------------------------------------------------------
Ran 11 tests in ~2.2s

OK
```

---

## 📊 Database Architecture

The SQLite database (`placement_system.db`) consists of 8 interconnected tables:

| Table Name | Description | Key Columns |
| :--- | :--- | :--- |
| `students` | Student accounts & profiles | `id`, `name`, `email`, `password_hash`, `college`, `branch`, `grad_year`, `cgpa`, `target_role` |
| `aptitude_questions` | Pre-seeded aptitude bank | `id`, `category` (Quantitative, Logical, Verbal), `topic`, `question_text`, `option_a..d`, `correct_option`, `explanation` |
| `aptitude_results` | Student test records | `id`, `student_id`, `category`, `score`, `total_questions`, `percentage`, `time_taken_seconds`, `completed_at` |
| `coding_problems` | Problem tracker entries | `id`, `student_id`, `title`, `platform`, `language`, `difficulty`, `status`, `problem_url`, `notes` |
| `job_applications` | Placement CRM records | `id`, `student_id`, `company_name`, `job_role`, `application_date`, `location_type`, `ctc`, `status`, `notes` |
| `interview_questions` | Technical & HR question repository | `id`, `category` (Java, Python, SQL, OOPs, HR), `topic`, `question_text`, `answer_text`, `tips` |
| `student_interview_progress`| Bookmarks / mastered status | `student_id`, `question_id`, `is_mastered`, `updated_at` |
| `activity_logs` | Audit feed for student dashboard | `student_id`, `activity_type`, `description`, `created_at` |

---

## 🎨 Color Palette Reference

- **Dark Navy**: `#0B192C` (Primary sidebar, brand cards, high contrast)
- **Deep Slate**: `#0F172A` / `#1E293B` (Body background, surface elements)
- **Teal / Cyan**: `#0D9488` / `#14B8A6` / `#2DD4BF` (Action buttons, brand accents, chart gradients)
- **Card White**: `#FFFFFF` (Content surfaces, cards, crisp tables)
- **Subtle Slate**: `#F8FAFC` / `#F1F5F9` (Background layers, hover states)
