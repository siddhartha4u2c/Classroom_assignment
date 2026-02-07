# EduRoom – Classroom Website

A simple classroom web app where **teachers** create and evaluate assignments and **students** view and submit them.

## Features

- **Registration & login** – Sign up as a student or teacher
- **Teachers**: Create assignments (title, description, due date, max marks), edit them, view all submissions, and evaluate with marks and feedback
- **Students**: See all assignments, submit text and/or file attachments, view grades and feedback
- **File uploads** – Students can attach files (e.g. PDF, DOC, images); teachers can download them when evaluating

## Setup

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python app.py
   ```
4. Open **http://127.0.0.1:5000** in your browser.

## Usage

1. **Register** – Create an account and choose role: Student or Teacher.
2. **Log in** – You’re taken to the teacher dashboard or student dashboard based on your role.
3. **Teachers**: Use “Create assignment” to add an assignment, then “View submissions” to see and evaluate student work.
4. **Students**: Open an assignment, click “Submit assignment” to add your response and/or a file, then check back for marks and feedback.

Data is stored in `classroom.db` (SQLite). Uploaded files are saved in the `uploads/` folder.

## Deploy globally

To host the app on the internet so anyone can access it, see **[DEPLOYMENT.md](DEPLOYMENT.md)** for step-by-step instructions (Render, Railway, or your own server).
Available on https://classroom-assignment-whg1.onrender.com/login


