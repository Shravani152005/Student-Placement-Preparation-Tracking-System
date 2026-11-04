"""
test_app.py - Automated End-to-End Test Suite for Student Placement Preparation & Tracking System
Tests all user authentication, dashboard metrics, aptitude test scoring, coding problem tracking,
job CRM pipeline, interview preparation, and profile management workflows.
"""

import unittest
import os
import sys

# Ensure application module can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
import database


class PlacementSystemTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and ensure test database state."""
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

        # Initialize and seed database
        database.init_db()

    def test_01_homepage_renders(self):
        """Test landing page loads successfully for public users."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Placement", response.data)
        self.assertIn(b"Crack Your Dream Placement", response.data)

    def test_02_demo_login(self):
        """Test authenticating with pre-seeded demo student credentials."""
        response = self.client.post("/login", data={
            "email": "demo@student.edu",
            "password": "demo123"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Rahul Sharma", response.data)
        self.assertIn(b"Placement Dashboard", response.data)

    def test_03_login_failure(self):
        """Test authentication rejection with invalid password."""
        response = self.client.post("/login", data={
            "email": "demo@student.edu",
            "password": "wrongpassword"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid email or password", response.data)

    def test_04_student_registration(self):
        """Test registering a new student with full details."""
        test_email = f"test_student_{os.getpid()}@college.edu"
        response = self.client.post("/register", data={
            "name": "Pooja Patel",
            "email": test_email,
            "password": "securepassword123",
            "confirm_password": "securepassword123",
            "college": "IIT Bombay",
            "branch": "Computer Science & Engineering",
            "grad_year": "2026",
            "target_role": "Backend Engineer"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Pooja Patel", response.data)

        # Verify in DB
        student = database.get_student_by_email(test_email)
        self.assertIsNotNone(student)
        self.assertEqual(student["college"], "IIT Bombay")

    def test_05_unauthorized_access_redirect(self):
        """Test that protected pages redirect to login for guests."""
        # Clear session
        with self.client.session_transaction() as sess:
            sess.clear()

        endpoints = ["/dashboard", "/aptitude", "/coding", "/jobs", "/interview", "/profile"]
        for ep in endpoints:
            response = self.client.get(ep, follow_redirects=False)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.headers["Location"])

    def test_06_dashboard_metrics(self):
        """Test dashboard metrics calculation and API endpoint."""
        # Login demo student
        self.client.post("/login", data={"email": "demo@student.edu", "password": "demo123"})
        
        response = self.client.get("/api/dashboard-charts")
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("job_distribution", json_data)
        self.assertIn("coding_distribution", json_data)
        self.assertIn("readiness_score", json_data)
        self.assertGreaterEqual(json_data["readiness_score"], 0)

    def test_07_aptitude_quiz_submission(self):
        """Test submitting aptitude test answers and calculating score."""
        self.client.post("/login", data={"email": "demo@student.edu", "password": "demo123"})
        
        # Fetch 2 questions from DB to simulate user submission
        conn = database.get_db()
        questions = conn.execute("SELECT id, correct_option FROM aptitude_questions LIMIT 2").fetchall()
        conn.close()

        q1 = questions[0]
        q2 = questions[1]

        # Submit: 1 correct answer and 1 deliberately wrong answer
        wrong_opt = "B" if q2["correct_option"] != "B" else "C"
        submission = {
            "category": "Quantitative",
            "answers": {
                str(q1["id"]): q1["correct_option"],
                str(q2["id"]): wrong_opt
            },
            "time_taken": 45
        }

        response = self.client.post(
            "/aptitude/submit",
            json=submission,
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 200)
        res_data = response.get_json()
        self.assertTrue(res_data["success"])
        self.assertEqual(res_data["score"], 1)
        self.assertEqual(res_data["total_questions"], 2)
        self.assertEqual(res_data["percentage"], 50.0)
        self.assertEqual(len(res_data["feedback"]), 2)

    def test_08_coding_crud_operations(self):
        """Test adding, editing, status toggling, and deleting a coding problem."""
        self.client.post("/login", data={"email": "demo@student.edu", "password": "demo123"})

        # 1. Add Problem
        add_res = self.client.post("/coding/add", data={
            "title": "Subarray Sum Equals K",
            "platform": "LeetCode",
            "language": "Python",
            "difficulty": "Medium",
            "status": "In Progress",
            "problem_url": "https://leetcode.com/problems/subarray-sum-equals-k/",
            "notes": "Hash map with cumulative prefix sum."
        }, follow_redirects=True)
        self.assertEqual(add_res.status_code, 200)
        self.assertIn(b"Subarray Sum Equals K", add_res.data)

        # Get inserted problem ID
        conn = database.get_db()
        prob = conn.execute("SELECT * FROM coding_problems WHERE title = 'Subarray Sum Equals K'").fetchone()
        conn.close()
        self.assertIsNotNone(prob)
        prob_id = prob["id"]

        # 2. Toggle Status to Solved
        toggle_res = self.client.post(f"/coding/toggle-status/{prob_id}", data={
            "status": "Solved"
        }, follow_redirects=True)
        self.assertEqual(toggle_res.status_code, 200)

        # 3. Edit Problem
        edit_res = self.client.post(f"/coding/edit/{prob_id}", data={
            "title": "Subarray Sum Equals K (Optimized)",
            "platform": "LeetCode",
            "language": "Java",
            "difficulty": "Medium",
            "status": "Solved",
            "problem_url": "https://leetcode.com/problems/subarray-sum-equals-k/",
            "notes": "Optimal O(N) time and O(N) space."
        }, follow_redirects=True)
        self.assertEqual(edit_res.status_code, 200)
        self.assertIn(b"Subarray Sum Equals K (Optimized)", edit_res.data)

        # 4. Delete Problem
        del_res = self.client.post(f"/coding/delete/{prob_id}", follow_redirects=True)
        self.assertEqual(del_res.status_code, 200)
        self.assertNotIn(b"Subarray Sum Equals K (Optimized)", del_res.data)

    def test_09_job_crm_crud_operations(self):
        """Test adding, updating stage, editing, and deleting a job application."""
        self.client.post("/login", data={"email": "demo@student.edu", "password": "demo123"})

        # 1. Add Job Application
        add_res = self.client.post("/jobs/add", data={
            "company_name": "Salesforce",
            "job_role": "Member of Technical Staff",
            "application_date": "2026-11-01",
            "location_type": "On-Campus",
            "ctc": "30 LPA",
            "status": "Applied",
            "job_url": "https://salesforce.com/careers",
            "notes": "Applied on university portal."
        }, follow_redirects=True)
        self.assertEqual(add_res.status_code, 200)
        self.assertIn(b"Salesforce", add_res.data)

        # Find job id
        conn = database.get_db()
        job = conn.execute("SELECT * FROM job_applications WHERE company_name = 'Salesforce'").fetchone()
        conn.close()
        self.assertIsNotNone(job)
        job_id = job["id"]

        # 2. Update Stage to Shortlisted
        status_res = self.client.post(f"/jobs/status/{job_id}", data={"status": "Shortlisted"}, follow_redirects=True)
        self.assertEqual(status_res.status_code, 200)

        # 3. Edit Application
        edit_res = self.client.post(f"/jobs/edit/{job_id}", data={
            "company_name": "Salesforce India",
            "job_role": "MTS - Software Engineer",
            "application_date": "2026-11-01",
            "location_type": "Hybrid",
            "ctc": "32 LPA",
            "status": "Interview",
            "job_url": "https://salesforce.com/careers",
            "notes": "Passed Round 1 coding challenge."
        }, follow_redirects=True)
        self.assertEqual(edit_res.status_code, 200)
        self.assertIn(b"Salesforce India", edit_res.data)

        # 4. Delete Job Application
        del_res = self.client.post(f"/jobs/delete/{job_id}", follow_redirects=True)
        self.assertEqual(del_res.status_code, 200)
        self.assertNotIn(b"Salesforce India", del_res.data)

    def test_10_interview_preparation_features(self):
        """Test browsing questions and toggling mastered bookmark."""
        self.client.post("/login", data={"email": "demo@student.edu", "password": "demo123"})

        # Load interview page
        response = self.client.get("/interview?category=Java")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"JVM", response.data)

        # Toggle mastered status on question 1
        toggle_res = self.client.post("/interview/toggle-mastered/1", follow_redirects=True)
        self.assertEqual(toggle_res.status_code, 200)

    def test_11_profile_update(self):
        """Test updating profile information and changing password."""
        self.client.post("/login", data={"email": "demo@student.edu", "password": "demo123"})

        # Update profile
        update_res = self.client.post("/profile/update", data={
            "name": "Rahul Sharma (Updated)",
            "college": "National Institute of Technology Trichy",
            "branch": "Computer Science & Engineering",
            "grad_year": "2026",
            "cgpa": "9.1",
            "phone": "+91 99999 88888",
            "bio": "Updated bio text for placement season.",
            "target_role": "Staff Software Engineer",
            "linkedin": "https://linkedin.com/in/demo",
            "github": "https://github.com/demo"
        }, follow_redirects=True)
        self.assertEqual(update_res.status_code, 200)
        self.assertIn(b"Rahul Sharma (Updated)", update_res.data)


if __name__ == "__main__":
    unittest.main()
