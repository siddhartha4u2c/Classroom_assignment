import os
from datetime import datetime
from flask import Flask, redirect, url_for, request, send_from_directory
from flask_login import LoginManager, current_user

from config import Config
from models import db, User, Assignment, Submission

from flask_sqlalchemy import SQLAlchemy

# app.py
from flask import Flask
from config import Config
from extensions import db  # import the single db instance
from routes import *
from models import *
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)  # initialize db with app
db = SQLAlchemy()
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_teacher:
            return redirect(url_for('teacher_dashboard'))
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            from flask_login import login_user
            login_user(user)
            next_page = request.args.get('next') or url_for('index')
            return redirect(next_page)
        from flask import flash
        flash('Invalid email or password.', 'error')
    return __render('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        from flask import flash
        email = request.form.get('email', '').strip()
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student')
        if not email or not name or not password:
            flash('Please fill all fields.', 'error')
            return __render('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return __render('register.html')
        if role not in ('student', 'teacher'):
            role = 'student'
        user = User(email=email, name=name, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return __render('register.html')


@app.route('/logout')
def logout():
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('login'))


# ---------- Teacher routes ----------
@app.route('/teacher')
def teacher_dashboard():
    if not current_user.is_authenticated or not current_user.is_teacher:
        return redirect(url_for('login'))
    assignments = Assignment.query.filter_by(created_by_id=current_user.id).order_by(Assignment.created_at.desc()).all()
    return __render('teacher_dashboard.html', assignments=assignments)


@app.route('/teacher/assignments/new', methods=['GET', 'POST'])
def create_assignment():
    if not current_user.is_authenticated or not current_user.is_teacher:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        due = request.form.get('due_date')
        max_marks = request.form.get('max_marks', 100, type=int)
        if not title:
            from flask import flash
            flash('Title is required.', 'error')
            return __render('assignment_form.html', assignment=None)
        due_dt = None
        if due:
            try:
                due_dt = datetime.fromisoformat(due.replace('Z', '+00:00'))
            except Exception:
                try:
                    due_dt = datetime.strptime(due, '%Y-%m-%dT%H:%M')
                except Exception:
                    pass
        a = Assignment(
            title=title,
            description=description or None,
            created_by_id=current_user.id,
            due_date=due_dt,
            max_marks=max(0, min(1000, max_marks))
        )
        db.session.add(a)
        db.session.commit()
        from flask import flash
        flash('Assignment created.', 'success')
        return redirect(url_for('teacher_dashboard'))
    return __render('assignment_form.html', assignment=None)


@app.route('/teacher/assignments/<int:aid>/edit', methods=['GET', 'POST'])
def edit_assignment(aid):
    if not current_user.is_authenticated or not current_user.is_teacher:
        return redirect(url_for('login'))
    a = Assignment.query.get_or_404(aid)
    if a.created_by_id != current_user.id:
        from flask import abort
        abort(403)
    if request.method == 'POST':
        a.title = request.form.get('title', '').strip() or a.title
        a.description = request.form.get('description', '').strip() or a.description
        due = request.form.get('due_date')
        if due:
            try:
                a.due_date = datetime.fromisoformat(due.replace('Z', '+00:00'))
            except Exception:
                try:
                    a.due_date = datetime.strptime(due, '%Y-%m-%dT%H:%M')
                except Exception:
                    pass
        a.max_marks = request.form.get('max_marks', a.max_marks, type=int)
        a.max_marks = max(0, min(1000, a.max_marks))
        db.session.commit()
        from flask import flash
        flash('Assignment updated.', 'success')
        return redirect(url_for('teacher_dashboard'))
    return __render('assignment_form.html', assignment=a)


@app.route('/teacher/assignments/<int:aid>/submissions')
def list_submissions(aid):
    if not current_user.is_authenticated or not current_user.is_teacher:
        return redirect(url_for('login'))
    a = Assignment.query.get_or_404(aid)
    if a.created_by_id != current_user.id:
        from flask import abort
        abort(403)
    subs = Submission.query.filter_by(assignment_id=aid).order_by(Submission.submitted_at.desc()).all()
    return __render('submissions_list.html', assignment=a, submissions=subs)


@app.route('/teacher/submissions/<int:sid>/download')
def download_submission_file(sid):
    if not current_user.is_authenticated or not current_user.is_teacher:
        return redirect(url_for('login'))
    sub = Submission.query.get_or_404(sid)
    if sub.assignment.created_by_id != current_user.id or not sub.file_path:
        from flask import abort
        abort(404)
    path = os.path.join(app.config['UPLOAD_FOLDER'], sub.file_path)
    if not os.path.isfile(path):
        from flask import abort
        abort(404)
    return send_from_directory(app.config['UPLOAD_FOLDER'], sub.file_path, as_attachment=True, download_name=sub.file_path.split('_')[-1] if '_' in sub.file_path else sub.file_path)


@app.route('/teacher/submissions/<int:sid>/evaluate', methods=['GET', 'POST'])
def evaluate_submission(sid):
    if not current_user.is_authenticated or not current_user.is_teacher:
        return redirect(url_for('login'))
    sub = Submission.query.get_or_404(sid)
    if sub.assignment.created_by_id != current_user.id:
        from flask import abort
        abort(403)
    if request.method == 'POST':
        sub.marks = request.form.get('marks', type=float)
        sub.feedback = request.form.get('feedback', '').strip()
        sub.evaluated_at = datetime.utcnow()
        sub.evaluated_by_id = current_user.id
        db.session.commit()
        from flask import flash
        flash('Submission evaluated.', 'success')
        return redirect(url_for('list_submissions', aid=sub.assignment_id))
    return __render('evaluate_submission.html', submission=sub)


# ---------- Student routes ----------
@app.route('/student')
def student_dashboard():
    if not current_user.is_authenticated or not current_user.is_student:
        return redirect(url_for('login'))
    assignments = Assignment.query.order_by(Assignment.created_at.desc()).all()
    my_submission_ids = {s.assignment_id for s in current_user.submissions}
    return __render('student_dashboard.html', assignments=assignments, my_submission_ids=my_submission_ids)


@app.route('/student/assignments/<int:aid>')
def view_assignment(aid):
    if not current_user.is_authenticated or not current_user.is_student:
        return redirect(url_for('login'))
    a = Assignment.query.get_or_404(aid)
    sub = Submission.query.filter_by(assignment_id=aid, student_id=current_user.id).first()
    return __render('view_assignment.html', assignment=a, submission=sub)


@app.route('/student/assignments/<int:aid>/submit', methods=['GET', 'POST'])
def submit_assignment(aid):
    if not current_user.is_authenticated or not current_user.is_student:
        return redirect(url_for('login'))
    a = Assignment.query.get_or_404(aid)
    existing = Submission.query.filter_by(assignment_id=aid, student_id=current_user.id).first()
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        file_path = None
        if 'file' in request.files:
            f = request.files['file']
            if f and f.filename:
                from werkzeug.utils import secure_filename
                ext = os.path.splitext(secure_filename(f.filename))[1] or '.bin'
                file_path = f"sub_{current_user.id}_{aid}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{ext}"
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], file_path))
        if existing:
            existing.content = content or existing.content
            if file_path:
                if existing.file_path and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], existing.file_path)):
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], existing.file_path))
                    except OSError:
                        pass
                existing.file_path = file_path
            existing.submitted_at = datetime.utcnow()
            db.session.commit()
        else:
            sub = Submission(
                assignment_id=aid,
                student_id=current_user.id,
                content=content or None,
                file_path=file_path
            )
            db.session.add(sub)
            db.session.commit()
        from flask import flash
        flash('Assignment submitted.', 'success')
        return redirect(url_for('view_assignment', aid=aid))
    return __render('submit_assignment.html', assignment=a, submission=existing)


def __render(template, **kwargs):
    from flask import render_template
    return render_template(template, **kwargs)


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
