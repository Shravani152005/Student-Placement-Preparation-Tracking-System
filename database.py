"""
database.py - SQLite Database Management & Seed Data
Handles database initialization, schema creation, seeding of realistic placement questions,
and provides helper functions for CRUD operations.
"""

import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

DB_NAME = "placement_system.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, DB_NAME)


def get_db():
    """Returns a thread-safe connection to the SQLite database with Row factory and WAL mode."""
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 20000")
    return conn


def init_db():
    """Initializes tables and seeds initial aptitude and interview questions."""
    conn = get_db()
    cursor = conn.cursor()

    # 1. Students Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        college TEXT NOT NULL,
        branch TEXT DEFAULT 'Computer Science & Engineering',
        grad_year INTEGER DEFAULT 2026,
        cgpa REAL DEFAULT 8.0,
        phone TEXT DEFAULT '',
        bio TEXT DEFAULT '',
        target_role TEXT DEFAULT 'Software Development Engineer',
        linkedin TEXT DEFAULT '',
        github TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Aptitude Questions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aptitude_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL, -- Quantitative, Logical Reasoning, Verbal Ability
        topic TEXT NOT NULL,
        question_text TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_option TEXT NOT NULL, -- 'A', 'B', 'C', 'D'
        explanation TEXT NOT NULL,
        difficulty TEXT DEFAULT 'Medium'
    )
    """)

    # 3. Aptitude Test Results Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aptitude_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        score INTEGER NOT NULL,
        total_questions INTEGER NOT NULL,
        percentage REAL NOT NULL,
        time_taken_seconds INTEGER DEFAULT 0,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    # 4. Coding Problems Tracker Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS coding_problems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        platform TEXT DEFAULT 'LeetCode', -- LeetCode, HackerRank, CodeChef, GeeksforGeeks, Codeforces
        language TEXT DEFAULT 'Python', -- Python, Java, C++, C, JavaScript
        difficulty TEXT DEFAULT 'Medium', -- Easy, Medium, Hard
        status TEXT DEFAULT 'Solved', -- Solved, In Progress, Need Revision
        problem_url TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    # 5. Job Applications Tracker Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        company_name TEXT NOT NULL,
        job_role TEXT NOT NULL,
        application_date DATE NOT NULL,
        job_url TEXT DEFAULT '',
        location_type TEXT DEFAULT 'On-Campus', -- On-Campus, Off-Campus, Remote, Hybrid
        ctc TEXT DEFAULT 'Not Disclosed',
        status TEXT DEFAULT 'Applied', -- Applied, Shortlisted, Interview, Selected, Rejected
        notes TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    # 6. Interview Questions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interview_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL, -- Java, Python, SQL, OOPs, HR, DSA
        topic TEXT NOT NULL,
        question_text TEXT NOT NULL,
        answer_text TEXT NOT NULL,
        difficulty TEXT DEFAULT 'Medium',
        tips TEXT DEFAULT ''
    )
    """)

    # 7. Student Interview Progress (Bookmark / Mastered status)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_interview_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        is_mastered INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(student_id, question_id),
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES interview_questions(id) ON DELETE CASCADE
    )
    """)

    # 8. Activity Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        activity_type TEXT NOT NULL, -- 'aptitude', 'coding', 'job', 'interview', 'profile'
        description TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    conn.commit()

    # Seed aptitude & interview questions if empty
    cursor.execute("SELECT COUNT(*) FROM aptitude_questions")
    if cursor.fetchone()[0] == 0:
        seed_aptitude_questions(conn)

    cursor.execute("SELECT COUNT(*) FROM interview_questions")
    if cursor.fetchone()[0] == 0:
        seed_interview_questions(conn)

    # Seed demo student if no students exist
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        seed_demo_student(conn)

    conn.close()


def log_activity(student_id, activity_type, description):
    """Utility to log student action in the activity feed."""
    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO activity_logs (student_id, activity_type, description) VALUES (?, ?, ?)",
            (student_id, activity_type, description)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging activity: {e}")


def seed_demo_student(conn):
    """Creates a sample demo student with initial data for instant evaluation."""
    cursor = conn.cursor()
    demo_password_hash = generate_password_hash("demo123")
    
    cursor.execute("""
    INSERT INTO students (name, email, password_hash, college, branch, grad_year, cgpa, phone, bio, target_role, linkedin, github)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Rahul Sharma",
        "demo@student.edu",
        demo_password_hash,
        "National Institute of Technology",
        "Computer Science & Engineering",
        2026,
        8.85,
        "+91 98765 43210",
        "Aspiring Software Development Engineer enthusiastic about Algorithms, Full-Stack Systems, and Distributed Computing.",
        "Software Engineer / Backend Developer",
        "https://linkedin.com/in/rahul-sharma-demo",
        "https://github.com/rahul-sharma-demo"
    ))
    student_id = cursor.lastrowid

    # Seed some sample coding problems
    sample_problems = [
        (student_id, "Two Sum", "LeetCode", "Python", "Easy", "Solved", "https://leetcode.com/problems/two-sum/", "Used hash map for O(n) lookup time."),
        (student_id, "Longest Substring Without Repeating Characters", "LeetCode", "Java", "Medium", "Solved", "https://leetcode.com/problems/longest-substring-without-repeating-characters/", "Sliding window technique with HashSet."),
        (student_id, "Merge K Sorted Lists", "LeetCode", "C++", "Hard", "In Progress", "https://leetcode.com/problems/merge-k-sorted-lists/", "Min-heap / priority queue approach."),
        (student_id, "Reverse a Linked List", "GeeksforGeeks", "Java", "Easy", "Solved", "https://geeksforgeeks.org/problems/reverse-a-linked-list/", "Iterative with 3 pointers (prev, curr, next)."),
        (student_id, "Trapping Rain Water", "LeetCode", "Python", "Hard", "Need Revision", "https://leetcode.com/problems/trapping-rain-water/", "Two pointer method beats 98% memory."),
        (student_id, "Binary Tree Level Order Traversal", "LeetCode", "Python", "Medium", "Solved", "https://leetcode.com/problems/binary-tree-level-order-traversal/", "BFS using Queue / collections.deque.")
    ]
    cursor.executemany("""
    INSERT INTO coding_problems (student_id, title, platform, language, difficulty, status, problem_url, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_problems)

    # Seed some sample job applications
    sample_jobs = [
        (student_id, "Google", "Associate Software Engineer", "2026-10-15", "https://careers.google.com", "On-Campus", "32 LPA", "Shortlisted", "Online Assessment cleared. Round 1 scheduled next week."),
        (student_id, "Microsoft", "Software Engineer - Campus", "2026-10-18", "https://careers.microsoft.com", "On-Campus", "28 LPA", "Interview", "Technical round completed, awaiting HR round call."),
        (student_id, "Amazon", "SDE-1", "2026-10-05", "https://amazon.jobs", "Off-Campus", "24 LPA", "Applied", "Applied through employee referral."),
        (student_id, "Atlassian", "Graduate Developer", "2026-09-28", "https://atlassian.com/careers", "Remote", "35 LPA", "Selected", "Offer letter received! CTC 35 LPA with joining bonus."),
        (student_id, "Goldman Sachs", "Engineering Analyst", "2026-09-15", "https://goldmansachs.com/careers", "On-Campus", "22 LPA", "Rejected", "Aptitude cut-off was very high.")
    ]
    cursor.executemany("""
    INSERT INTO job_applications (student_id, company_name, job_role, application_date, job_url, location_type, ctc, status, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_jobs)

    # Seed sample aptitude results
    sample_results = [
        (student_id, "Quantitative", 8, 10, 80.0, 480),
        (student_id, "Logical Reasoning", 9, 10, 90.0, 420),
        (student_id, "Verbal Ability", 7, 10, 70.0, 360)
    ]
    cursor.executemany("""
    INSERT INTO aptitude_results (student_id, category, score, total_questions, percentage, time_taken_seconds)
    VALUES (?, ?, ?, ?, ?, ?)
    """, sample_results)

    # Seed activity logs
    sample_logs = [
        (student_id, "job", "Added application for Google - Associate Software Engineer (Shortlisted)"),
        (student_id, "coding", "Solved coding problem: 'Binary Tree Level Order Traversal' in Python"),
        (student_id, "aptitude", "Scored 90% in Logical Reasoning practice test"),
        (student_id, "job", "Updated status of Atlassian application to Selected!"),
        (student_id, "interview", "Mastered 5 Technical & HR interview questions")
    ]
    cursor.executemany("""
    INSERT INTO activity_logs (student_id, activity_type, description)
    VALUES (?, ?, ?)
    """, sample_logs)

    conn.commit()


def seed_aptitude_questions(conn):
    """Seeds standard campus placement aptitude questions across 3 main categories."""
    cursor = conn.cursor()
    questions = [
        # --- QUANTITATIVE APTITUDE ---
        (
            "Quantitative", "Time & Work",
            "A can complete a piece of work in 12 days, and B can complete the same work in 18 days. If they work together, in how many days will they finish the work?",
            "7.2 days", "8 days", "6.5 days", "9 days",
            "A",
            "Work done by A in 1 day = 1/12. Work done by B in 1 day = 1/18. Together in 1 day = 1/12 + 1/18 = (3+2)/36 = 5/36. Total days = 36/5 = 7.2 days.",
            "Easy"
        ),
        (
            "Quantitative", "Percentages",
            "If the price of petrol increases by 25%, by what percentage must a person reduce consumption so that overall expenditure remains the same?",
            "20%", "25%", "16.66%", "30%",
            "A",
            "Reduction % = [R / (100 + R)] * 100 = [25 / 125] * 100 = 1/5 * 100 = 20%.",
            "Easy"
        ),
        (
            "Quantitative", "Profit & Loss",
            "A shopkeeper sells an article for ₹840 making a profit of 20%. What was the cost price of the article?",
            "₹680", "₹700", "₹720", "₹750",
            "B",
            "Selling Price (SP) = CP * (1 + Profit%/100). 840 = CP * 1.20 => CP = 840 / 1.2 = ₹700.",
            "Easy"
        ),
        (
            "Quantitative", "Speed, Distance & Time",
            "A train 180 meters long is running at a speed of 54 km/h. How much time will it take to pass an electric pole?",
            "10 seconds", "12 seconds", "15 seconds", "18 seconds",
            "B",
            "Speed in m/s = 54 * (5/18) = 15 m/s. Time = Distance / Speed = 180 m / 15 m/s = 12 seconds.",
            "Medium"
        ),
        (
            "Quantitative", "Averages",
            "The average age of 24 students and their class teacher is 16 years. If the teacher's age is excluded, the average reduces by 1 year. What is the teacher's age?",
            "38 years", "40 years", "42 years", "45 years",
            "B",
            "Total sum with teacher = 25 * 16 = 400. Total sum without teacher = 24 * 15 = 360. Teacher's age = 400 - 360 = 40 years.",
            "Medium"
        ),
        (
            "Quantitative", "Simple & Compound Interest",
            "What will be the compound interest on ₹10,000 for 2 years at 10% per annum, compounded annually?",
            "₹2,000", "₹2,100", "₹2,210", "₹2,050",
            "B",
            "Amount = P(1 + r/100)^t = 10000 * (1.1)^2 = 10000 * 1.21 = ₹12,100. CI = 12100 - 10000 = ₹2,100.",
            "Medium"
        ),
        (
            "Quantitative", "Ratios & Proportions",
            "Two numbers are in the ratio 3 : 5. If 8 is added to each number, the ratio becomes 2 : 3. What is the larger number?",
            "30", "40", "50", "25",
            "B",
            "Let numbers be 3x and 5x. (3x + 8)/(5x + 8) = 2/3 => 3(3x + 8) = 2(5x + 8) => 9x + 24 = 10x + 16 => x = 8. Larger number = 5 * 8 = 40.",
            "Medium"
        ),
        (
            "Quantitative", "Permutations & Combinations",
            "In how many different ways can the letters of the word 'LEADER' be arranged?",
            "720", "360", "120", "480",
            "B",
            "Total letters = 6. Letter 'E' repeats 2 times. Total arrangements = 6! / 2! = 720 / 2 = 360.",
            "Hard"
        ),
        (
            "Quantitative", "Probability",
            "Two dice are thrown simultaneously. What is the probability of getting two numbers whose product is even?",
            "1/4", "3/4", "1/2", "5/6",
            "B",
            "Product is odd only when both dice show odd numbers. Odd numbers = {1, 3, 5} (3 choices each). Odd outcomes = 3 * 3 = 9. Total outcomes = 36. P(Odd) = 9/36 = 1/4. Therefore, P(Even) = 1 - 1/4 = 3/4.",
            "Hard"
        ),
        (
            "Quantitative", "Pipes & Cisterns",
            "Pipe A can fill a tank in 20 hours while Pipe B can fill it in 30 hours. Both pipes are opened together. How long will they take to fill the tank?",
            "10 hours", "12 hours", "15 hours", "18 hours",
            "B",
            "Combined 1 hour work = 1/20 + 1/30 = (3+2)/60 = 5/60 = 1/12. Hence the tank is filled in 12 hours.",
            "Easy"
        ),

        # --- LOGICAL REASONING ---
        (
            "Logical Reasoning", "Number Series",
            "Find the next number in the sequence: 3, 7, 15, 31, 63, ?",
            "95", "127", "128", "131",
            "B",
            "Pattern: Each term is 2 * previous term + 1. (3*2+1=7, 7*2+1=15, 15*2+1=31, 31*2+1=63, 63*2+1=127).",
            "Easy"
        ),
        (
            "Logical Reasoning", "Blood Relations",
            "Pointing to a photograph, Rohit said, 'She is the daughter of the only son of my grandfather.' How is the girl in the photograph related to Rohit?",
            "Sister", "Cousin", "Aunt", "Mother",
            "A",
            "'Only son of my grandfather' = Rohit's father. 'Daughter of Rohit's father' = Rohit's sister.",
            "Easy"
        ),
        (
            "Logical Reasoning", "Coding - Decoding",
            "In a certain code, 'COMPUTER' is written as 'RFUVQNPC'. How is 'MEDICINE' written in that code?",
            "EOJDJEFM", "EOJDEJFM", "MFEJDJOE", "EOJDJEFB",
            "A",
            "Reverse the word and shift each letter by +1, keeping outer letters swapped or reverse shifted: MEDICINE -> Last letter E becomes first, first letter M becomes last, intermediate letters incremented by +1: E-O-J-D-J-E-F-M.",
            "Medium"
        ),
        (
            "Logical Reasoning", "Direction Sense",
            "A person walks 10 km North, turns right and walks 6 km, then turns right again and walks 10 km. How far and in what direction is he from the starting point?",
            "6 km East", "6 km West", "10 km East", "16 km North",
            "A",
            "Starting at (0,0), walking North goes to (0,10), right to (6,10), then South 10 km to (6,0). He is 6 km East of the origin.",
            "Easy"
        ),
        (
            "Logical Reasoning", "Syllogisms",
            "Statements: All cats are animals. All animals are mammals.\nConclusions:\nI. All cats are mammals.\nII. Some mammals are cats.",
            "Only conclusion I follows", "Only conclusion II follows", "Both conclusions I and II follow", "Neither follows",
            "C",
            "Since Cats is a subset of Animals, and Animals is a subset of Mammals, Cats is a subset of Mammals (I follows). Since Cats exist inside Mammals, some mammals are cats (II follows). Both follow.",
            "Medium"
        ),
        (
            "Logical Reasoning", "Seating Arrangement",
            "Five friends P, Q, R, S, T are sitting in a row facing North. R is sitting in the center. P is to the immediate left of R. S is at the extreme right end. Where is Q?",
            "Immediate left of P", "Immediate right of R", "Extreme left end or right end", "Between R and S",
            "A",
            "Row of 5: Positions 1, 2, 3, 4, 5. Center is pos 3 (R). Pos 2 is immediate left of R (P). Pos 5 is extreme right (S). That leaves pos 1 and pos 4 for Q and T. If Q is at pos 1, Q is immediate left of P.",
            "Medium"
        ),
        (
            "Logical Reasoning", "Analogies",
            "Clock : Time :: Thermometer : ?",
            "Heat", "Radiation", "Temperature", "Energy",
            "C",
            "A clock measures time; a thermometer measures temperature.",
            "Easy"
        ),
        (
            "Logical Reasoning", "Statement & Assumptions",
            "Statement: 'Join our institute for guaranteed 100% placement training.' - An advertisement.\nAssumptions:\nI. Students look for placement training after graduation.\nII. An advertisement attracts candidates.",
            "Only assumption I is implicit", "Only assumption II is implicit", "Both I and II are implicit", "Neither is implicit",
            "B",
            "An entity gives an advertisement believing that ads attract people (Assumption II is implicit). Assumption I specifies 'after graduation', which is not assumed in the advertisement.",
            "Hard"
        ),
        (
            "Logical Reasoning", "Odd One Out",
            "Identify the odd one out: 27, 64, 125, 216, 343, 512, 729, 1000",
            "64", "27", "216", "None of these (All are cubes)",
            "D",
            "All given numbers are perfect cubes: 3^3=27, 4^3=64, 5^3=125, 6^3=216, 7^3=343, 8^3=512, 9^3=729, 10^3=1000.",
            "Medium"
        ),
        (
            "Logical Reasoning", "Data Sufficiency",
            "Is X an even integer?\nStatement 1: 3X is an even integer.\nStatement 2: X/2 is an integer.",
            "Statement 1 alone is sufficient", "Statement 2 alone is sufficient", "Both statements together are needed", "Either statement alone is sufficient",
            "D",
            "From statement 1: 3 * X is even => since 3 is odd, X must be even. Sufficient. From statement 2: X/2 is integer => X is divisible by 2 => X is even. Sufficient. Either alone is sufficient.",
            "Hard"
        ),

        # --- VERBAL ABILITY ---
        (
            "Verbal Ability", "Synonyms",
            "Choose the word nearest in meaning to: 'CANDID'",
            "Deceitful", "Frank", "Reserved", "Shy",
            "B",
            "'Candid' means truthful, straightforward, and frank in speech or expression.",
            "Easy"
        ),
        (
            "Verbal Ability", "Antonyms",
            "Choose the word most opposite in meaning to: 'METICULOUS'",
            "Careless", "Thorough", "Detailed", "Scrupulous",
            "A",
            "'Meticulous' means showing great attention to detail. Its opposite is 'Careless' or 'Sloppy'.",
            "Easy"
        ),
        (
            "Verbal Ability", "Sentence Correction",
            "Choose the grammatically correct option: 'Neither the manager nor the employees _____ present at the meeting.'",
            "was", "were", "is", "are been",
            "B",
            "When subjects are joined by 'neither... nor', the verb agrees with the closer subject ('employees', which is plural, so 'were').",
            "Medium"
        ),
        (
            "Verbal Ability", "Idioms & Phrases",
            "What does the idiom 'To burn the midnight oil' mean?",
            "To waste resources carelessly", "To work or study late into the night", "To start a fire accidentally", "To sleep early",
            "B",
            "'Burning the midnight oil' means to read, study, or work late into the night.",
            "Easy"
        ),
        (
            "Verbal Ability", "Fill in the Blanks",
            "The committee could not reach a decision because there was no _____ among the members.",
            "discord", "consensus", "dispute", "apathy",
            "B",
            "'Consensus' means a general agreement among a group of people.",
            "Medium"
        ),
        (
            "Verbal Ability", "Spotting Errors",
            "Find the part with the error: (A) One of the student / (B) in our university / (C) won the prestigious award / (D) No error",
            "A", "B", "C", "D",
            "A",
            "The phrase 'one of the' is always followed by a plural noun: 'One of the students', not 'One of the student'.",
            "Medium"
        ),
        (
            "Verbal Ability", "Vocabulary in Context",
            "The scientist's theory was so _____ that even his peers had difficulty understanding it.",
            "lucid", "abstruse", "transparent", "trivial",
            "B",
            "'Abstruse' means difficult to understand or obscure.",
            "Hard"
        ),
        (
            "Verbal Ability", "Active & Passive Voice",
            "Convert to passive voice: 'The team completed the software project before the deadline.'",
            "The software project was completed by the team before the deadline.",
            "The software project is completed by the team before the deadline.",
            "The software project had been completed before the deadline.",
            "The deadline was met when the project was completed.",
            "A",
            "Past simple 'completed' converts to 'was completed + by subject'.",
            "Easy"
        ),
        (
            "Verbal Ability", "One Word Substitution",
            "A person who knows and speaks many languages is called a:",
            "Polyglot", "Philanthropist", "Monoglot", "Ambivalent",
            "A",
            "A 'polyglot' is someone who speaks or understands several languages.",
            "Easy"
        ),
        (
            "Verbal Ability", "Reading Comprehension",
            "Which of the following best defines an 'analogy' in written literature?",
            "A direct comparison using 'like' or 'as'",
            "A comparison between two things for explanation or clarification",
            "An exaggeration for dramatic effect",
            "A repetition of consonant sounds",
            "B",
            "An analogy is a cognitive comparison between two things that highlights similarities to explain a concept.",
            "Medium"
        )
    ]

    cursor.executemany("""
    INSERT INTO aptitude_questions (category, topic, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, difficulty)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, questions)
    conn.commit()


def seed_interview_questions(conn):
    """Seeds top technical (Java, Python, SQL, OOPs, DSA) and HR interview questions with sample model answers."""
    cursor = conn.cursor()
    questions = [
        # --- JAVA ---
        (
            "Java", "Core Java & Memory",
            "What is the difference between JDK, JRE, and JVM?",
            "JVM (Java Virtual Machine) executes Java bytecode. JRE (Java Runtime Environment) = JVM + core class libraries needed to run Java programs. JDK (Java Development Kit) = JRE + development tools (compiler javac, debugger, javadoc).",
            "Easy",
            "Remember JDK is for developing, JRE is for running, JVM is the virtual execution engine."
        ),
        (
            "Java", "OOP & Strings",
            "Why is the String class immutable in Java?",
            "Strings are immutable for:\n1. Security: Strings are used in class loading, network connections, file paths, and database URLs.\n2. String Constant Pool (SCP): Reusing string literals saves memory.\n3. Thread Safety: Immutable objects are inherently thread-safe without synchronization.\n4. HashCode Caching: The hashCode is calculated once and cached for Map lookups.",
            "Medium",
            "Mention String Constant Pool and Security as the two primary architectural reasons."
        ),
        (
            "Java", "Collections & Concurrency",
            "What is the difference between HashMap and ConcurrentHashMap?",
            "HashMap is non-synchronized and not thread-safe. Multiple threads modifying it can cause race conditions. ConcurrentHashMap achieves thread safety through segment-level locking / CAS (Compare-And-Swap) operations and synchronized buckets, allowing simultaneous reads and bucket-level concurrent writes without locking the entire map.",
            "Hard",
            "Highlight that ConcurrentHashMap locks only the specific bucket/node, not the entire table."
        ),
        (
            "Java", "Exception Handling",
            "What is the difference between checked and unchecked exceptions?",
            "Checked exceptions (e.g., IOException, SQLException) are verified at compile-time and must be either caught with try-catch or declared with throws. Unchecked exceptions inherit from RuntimeException (e.g., NullPointerException, ArrayIndexOutOfBoundsException) and are not checked at compile-time.",
            "Easy",
            "Give practical examples like FileNotFoundException (checked) vs NullPointerException (unchecked)."
        ),

        # --- PYTHON ---
        (
            "Python", "Memory & Execution",
            "What is the Global Interpreter Lock (GIL) in CPython?",
            "The GIL is a mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecode simultaneously in a single process. While this makes single-threaded execution fast and C extensions simple, it limits CPU-bound multi-threading. For CPU parallelism in Python, the multiprocessing module or process pools are preferred.",
            "Medium",
            "State clearly that I/O-bound tasks still benefit from threading, but CPU-bound tasks require multiprocessing."
        ),
        (
            "Python", "Data Structures",
            "What is the difference between a list and a tuple in Python?",
            "1. Mutability: Lists are mutable (elements can be added, updated, removed); Tuples are immutable.\n2. Syntax: Lists use square brackets [], tuples use parentheses ().\n3. Performance & Memory: Tuples consume less memory and have faster allocation because of fixed size.\n4. Hashability: Tuples containing immutable items can be used as dictionary keys; lists cannot.",
            "Easy",
            "Emphasize that tuples are hashable (can be dict keys) while lists cannot."
        ),
        (
            "Python", "Decorators & Generators",
            "What are Python Generators and what is the 'yield' keyword?",
            "Generators are functions that return an iterator and yield items one at a time on-demand using the 'yield' statement instead of returning a full collection. They maintain state between calls and achieve lazy evaluation, drastically reducing memory usage when processing large datasets or streams.",
            "Medium",
            "Mention O(1) memory complexity vs O(N) when loading millions of rows into a list."
        ),
        (
            "Python", "Advanced Concepts",
            "What is the difference between deepcopy and shallow copy in Python?",
            "A shallow copy (copy.copy()) constructs a new compound object and inserts references to the original nested objects. A deep copy (copy.deepcopy()) recursively copies all nested objects, creating independent duplicates so mutations to nested elements don't reflect in the original.",
            "Medium",
            "Give the example of a list containing another inner list."
        ),

        # --- SQL & DATABASES ---
        (
            "SQL", "Querying & Joins",
            "What are the different types of SQL Joins?",
            "1. INNER JOIN: Returns records that have matching values in both tables.\n2. LEFT JOIN: Returns all records from the left table and matched records from the right table (NULL if no match).\n3. RIGHT JOIN: Returns all records from the right table and matched from left.\n4. FULL OUTER JOIN: Returns all records when there is a match in either table.\n5. CROSS JOIN: Returns Cartesian product of both tables.",
            "Easy",
            "Draw a quick mental Venn diagram when explaining joins."
        ),
        (
            "SQL", "Database Indexing",
            "How do Database Indexes work and what are their trade-offs?",
            "An index is a data structure (typically B-Tree or Hash) that allows fast lookups without scanning every row of a table (changing O(n) table scans to O(log n) tree searches). Trade-offs: Indexes consume disk storage and slow down INSERT, UPDATE, and DELETE operations because indexes must be updated on write.",
            "Medium",
            "Mention the B-Tree structure and the write penalty trade-off."
        ),
        (
            "SQL", "Transactions & ACID",
            "Explain the ACID properties in database management systems.",
            "A - Atomicity: All operations in a transaction succeed, or all are rolled back.\nC - Consistency: Database transitions from one valid state to another, respecting all constraints.\nI - Isolation: Concurrent transactions do not interfere with each other.\nD - Durability: Committed changes survive system crashes and power failures.",
            "Medium",
            "Use a bank fund transfer example (Debit Account A, Credit Account B) to explain Atomicity."
        ),
        (
            "SQL", "Advanced Queries",
            "How do you find the Nth highest salary in a SQL table?",
            "Using DENSE_RANK() window function:\nSELECT salary FROM (\n  SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) as rnk\n  FROM employees\n) WHERE rnk = N;\nOr with LIMIT / OFFSET:\nSELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET N-1;",
            "Medium",
            "Mention why DENSE_RANK is preferred over ROW_NUMBER (handles duplicate salaries correctly)."
        ),

        # --- OOPS CONCEPTS ---
        (
            "OOPs", "Core Principles",
            "Explain the 4 fundamental pillars of Object-Oriented Programming.",
            "1. Encapsulation: Bundling data (attributes) and methods that operate on that data into a single unit (class) while restricting direct access using access modifiers (private, protected).\n2. Abstraction: Hiding internal complex implementation details and showing only essential features to the user (interfaces, abstract classes).\n3. Inheritance: Mechanism where a child class acquires properties and behaviors of a parent class, promoting code reuse.\n4. Polymorphism: Ability of an object to take many forms (Compile-time: Method Overloading; Runtime: Method Overriding).",
            "Easy",
            "Use real-life examples like a car dashboard (abstraction) or steering wheel (polymorphism)."
        ),
        (
            "OOPs", "Design Principles",
            "What are the SOLID principles?",
            "S - Single Responsibility: A class should have only one reason to change.\nO - Open/Closed: Software entities should be open for extension, but closed for modification.\nL - Liskov Substitution: Subtypes must be substitutable for their base types.\nI - Interface Segregation: Clients shouldn't be forced to depend on interfaces they do not use.\nD - Dependency Inversion: High-level modules should depend on abstractions, not concrete implementations.",
            "Hard",
            "State each letter clearly with a one-sentence definition."
        ),
        (
            "OOPs", "Polymorphism",
            "What is the difference between Method Overloading and Method Overriding?",
            "Method Overloading (Compile-Time / Static Polymorphism): Multiple methods in the same class have the same name but different parameter lists (count, types, order). Return type alone is insufficient.\nMethod Overriding (Run-Time / Dynamic Polymorphism): A subclass provides a specific implementation of a method already defined in its superclass with the exact same name, return type, and parameter list.",
            "Easy",
            "Remember Overloading = same class, different signatures; Overriding = parent-child relationship, same signature."
        ),

        # --- HR & BEHAVIORAL QUESTIONS ---
        (
            "HR", "Self Introduction",
            "Tell me about yourself.",
            "Sample Structure (Present - Past - Future):\n'Good morning/afternoon. I am Rahul Sharma, currently completing my B.Tech in Computer Science at NIT with a CGPA of 8.8. Over the past three years, I have built a strong foundation in Data Structures, Algorithms, and Full-Stack Development.\nRecently, I developed a scalable Student Placement Preparation & Tracking platform with Flask and SQLite, and solved 200+ LeetCode problems.\nI am passionate about building resilient backend systems and am eager to contribute my problem-solving skills to your team while learning from industry veterans.'",
            "Easy",
            "Keep it under 90 seconds. Focus 70% on relevant technical projects, skills, and future goals, not personal life."
        ),
        (
            "HR", "Strengths & Weaknesses",
            "What are your greatest strength and your greatest weakness?",
            "Strength: 'My analytical problem-solving and persistence. When faced with a complex bug or new technology, I break it down systematically and enjoy seeing it through to resolution.'\nWeakness: 'In the past, I sometimes hesitated to delegate tasks during group college projects because I wanted everything to be pixel-perfect. However, I recognized this and learned to communicate requirements clearly and trust my teammates, which significantly improved our project delivery time.'",
            "Medium",
            "Always pick a genuine professional weakness and immediately describe the active steps you are taking to overcome it."
        ),
        (
            "HR", "Company Fit",
            "Why do you want to join our company?",
            "Model Answer: 'I have closely followed your company's work, especially how you recently expanded your cloud-native developer infrastructure. What excites me most is your culture of engineering excellence, continuous learning, and ownership. At this stage of my career, I want to be in an environment where I can be challenged with real-world scale and contribute meaningfully to products used by millions.'",
            "Easy",
            "Do your research beforehand. Mention specific products, recent tech releases, or engineering blog posts of the company."
        ),
        (
            "HR", "Conflict Resolution",
            "Describe a time you had a conflict with a teammate and how you resolved it.",
            "Use STAR method (Situation, Task, Action, Result):\n- Situation: During our final semester capstone project, my teammate and I disagreed on whether to use SQL or MongoDB.\n- Task: We needed to finalize the database architecture without delaying our milestone deadline.\n- Action: Instead of arguing, I proposed we benchmark both by listing our core query patterns (structured relational data vs flexible documents). We found 85% of our entities had strict relational schemas.\n- Result: My teammate agreed SQL was better suited. We delivered the project on time and scored top marks.",
            "Hard",
            "Demonstrate emotional intelligence, data-driven decisions, and that you place the team goal above personal ego."
        ),
        (
            "HR", "Long-term Vision",
            "Where do you see yourself in 5 years?",
            "Model Answer: 'In five years, I see myself as a seasoned software engineer with deep technical domain expertise in distributed systems and architecture. I want to have led significant feature deliveries from concept to production, mentored junior developers, and taken on technical design responsibilities. Ultimately, I want to be recognized as a reliable, high-impact engineer within the company.'",
            "Medium",
            "Show ambition and loyalty without sounding unrealistic (avoid saying 'I will be the CEO' or 'I will start my own startup')."
        )
    ]

    cursor.executemany("""
    INSERT INTO interview_questions (category, topic, question_text, answer_text, difficulty, tips)
    VALUES (?, ?, ?, ?, ?, ?)
    """, questions)
    conn.commit()


# --- DATABASE QUERY HELPERS ---

def get_student_by_id(student_id):
    """Retrieves student record by id."""
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    conn.close()
    return student


def get_student_by_email(email):
    """Retrieves student record by email."""
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE email = ?", (email.strip().lower(),)).fetchone()
    conn.close()
    return student


def get_dashboard_metrics(student_id):
    """
    Computes all dynamic dashboard metrics for a student from database records:
    - Total aptitude questions attempted & average percentage
    - Total coding problems completed, pending, and total
    - Total job applications, shortlisted, interview, selected, rejected
    - Overall placement preparation readiness score (0 - 100%)
    - Recent activities
    """
    conn = get_db()
    cursor = conn.cursor()

    # 1. Aptitude Stats
    cursor.execute("""
        SELECT COUNT(*), COALESCE(SUM(total_questions), 0), COALESCE(AVG(percentage), 0)
        FROM aptitude_results
        WHERE student_id = ?
    """, (student_id,))
    aptitude_tests_count, total_aptitude_attempted, avg_aptitude_pct = cursor.fetchone()

    # 2. Coding Stats
    cursor.execute("""
        SELECT 
            COUNT(*),
            COALESCE(SUM(CASE WHEN status = 'Solved' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN status = 'Need Revision' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN difficulty = 'Easy' AND status = 'Solved' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN difficulty = 'Medium' AND status = 'Solved' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN difficulty = 'Hard' AND status = 'Solved' THEN 1 ELSE 0 END), 0)
        FROM coding_problems
        WHERE student_id = ?
    """, (student_id,))
    (total_coding, coding_solved, coding_in_progress, coding_revision,
     coding_easy_solved, coding_med_solved, coding_hard_solved) = cursor.fetchone()

    # 3. Job Stats
    cursor.execute("""
        SELECT 
            COUNT(*),
            COALESCE(SUM(CASE WHEN status = 'Applied' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN status = 'Shortlisted' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN status = 'Interview' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN status = 'Selected' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END), 0)
        FROM job_applications
        WHERE student_id = ?
    """, (student_id,))
    (total_jobs, jobs_applied, jobs_shortlisted, jobs_interview, jobs_selected, jobs_rejected) = cursor.fetchone()

    # 4. Interview Progress Stats
    cursor.execute("""
        SELECT COUNT(*)
        FROM student_interview_progress
        WHERE student_id = ? AND is_mastered = 1
    """, (student_id,))
    interview_mastered = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM interview_questions")
    total_interview_questions = cursor.fetchone()[0] or 20

    # 5. Calculate Placement Readiness Score (0 to 100)
    # Balanced weighting:
    # Aptitude accuracy (30 pts), Coding progress (35 pts), Interview prep (20 pts), Job tracking activity (15 pts)
    aptitude_component = min(30.0, (avg_aptitude_pct / 100.0) * 30.0) if aptitude_tests_count > 0 else 0.0
    coding_target = 30 # standard benchmark for placement preparation
    coding_component = min(35.0, (coding_solved / max(1, coding_target)) * 35.0)
    interview_component = min(20.0, (interview_mastered / max(1, total_interview_questions)) * 20.0)
    job_component = min(15.0, (total_jobs / 10.0) * 15.0)
    readiness_score = round(aptitude_component + coding_component + interview_component + job_component, 1)

    # 6. Recent Activity Logs (last 6)
    cursor.execute("""
        SELECT activity_type, description, created_at
        FROM activity_logs
        WHERE student_id = ?
        ORDER BY id DESC
        LIMIT 6
    """, (student_id,))
    recent_activities = cursor.fetchall()

    # 7. Aptitude Quiz Score History for Trend Chart
    cursor.execute("""
        SELECT category, score, total_questions, percentage, completed_at
        FROM aptitude_results
        WHERE student_id = ?
        ORDER BY id ASC
        LIMIT 10
    """, (student_id,))
    aptitude_history = cursor.fetchall()

    conn.close()

    return {
        "aptitude_tests_count": aptitude_tests_count,
        "total_aptitude_attempted": total_aptitude_attempted,
        "avg_aptitude_pct": round(avg_aptitude_pct, 1),
        "total_coding": total_coding,
        "coding_solved": coding_solved,
        "coding_in_progress": coding_in_progress,
        "coding_revision": coding_revision,
        "coding_easy_solved": coding_easy_solved,
        "coding_med_solved": coding_med_solved,
        "coding_hard_solved": coding_hard_solved,
        "total_jobs": total_jobs,
        "jobs_applied": jobs_applied,
        "jobs_shortlisted": jobs_shortlisted,
        "jobs_interview": jobs_interview,
        "jobs_selected": jobs_selected,
        "jobs_rejected": jobs_rejected,
        "interview_mastered": interview_mastered,
        "total_interview_questions": total_interview_questions,
        "readiness_score": min(100.0, readiness_score),
        "recent_activities": recent_activities,
        "aptitude_history": aptitude_history
    }
