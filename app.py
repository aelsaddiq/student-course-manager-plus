from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lab8-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lab8.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # basic id
    username = db.Column(db.String(80), unique=True, nullable=False)  # login name
    password = db.Column(db.String(255), nullable=False)  # hashed password now
    full_name = db.Column(db.String(120), nullable=False)  # actual name shown in app
    role = db.Column(db.String(20), nullable=False)  # student teacher or admin

    taught_courses = db.relationship('Course', backref='teacher', lazy=True)  # teacher's classes
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)  # student's classes

    def __str__(self):
        return f"{self.full_name} ({self.role})"  # nicer labels in admin

    def __repr__(self):
        return self.__str__()


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # course id
    name = db.Column(db.String(120), nullable=False)  # course name
    time = db.Column(db.String(120), nullable=False)  # meeting time
    capacity = db.Column(db.Integer, nullable=False)  # max seats
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # linked teacher

    enrollments = db.relationship(
        'Enrollment',
        backref='course',
        lazy=True,
        cascade='all, delete-orphan'
    )  # deleting course removes enrollments too

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # enrollment id
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # linked student
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)  # linked course
    grade = db.Column(db.Float, nullable=True, default=None)  # None = not graded yet

    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='unique_student_course'),
    )  # prevents same class twice

    def __str__(self):
        return f"{self.student.full_name} - {self.course.name}"

    def __repr__(self):
        return self.__str__()


SAMPLE_DATA = [
    {
        'name': 'Math 101',
        'teacher': 'Ralph Jenkins',
        'time': 'MWF 10:00-10:50 AM',
        'capacity': 8,
        'students': [
            ('Jose Santos', 92),
            ('Betty Brown', 65),
            ('John Stuart', 86),
            ('Li Cheng', 77),
        ],
    },
    {
        'name': 'Physics 121',
        'teacher': 'Susan Walker',
        'time': 'TR 11:00-11:50 AM',
        'capacity': 10,
        'students': [
            ('Nancy Little', 53),
            ('Li Cheng', 85),
            ('Mindy Norris', 94),
            ('John Stuart', 91),
            ('Betty Brown', 88),
        ],
    },
    {
        'name': 'CS 106',
        'teacher': 'Ammon Hepworth',
        'time': 'MWF 2:00-2:50 PM',
        'capacity': 10,
        'students': [
            ('Aditya Ranganath', 93),
            ('Yi Wen Chen', 85),
            ('Nancy Little', 57),
            ('Mindy Norris', 68),
        ],
    },
    {
        'name': 'CS 162',
        'teacher': 'Ammon Hepworth',
        'time': 'TR 3:00-3:50 PM',
        'capacity': 4,
        'students': [
            ('Aditya Ranganath', 99),
            ('Nancy Little', 87),
            ('Yi Wen Chen', 92),
            ('John Stuart', 67),
        ],
    },
]


def seed_data():
    if User.query.first():
        return  # skip if db already has data

    admin_user = User(
        username='admin',
        password=generate_password_hash('admin123'),
        full_name='Admin User',
        role='admin'
    )
    db.session.add(admin_user)

    for course_data in SAMPLE_DATA:
        teacher_name = course_data['teacher'].strip()
        teacher_username = teacher_name.lower().replace(' ', '.')
        teacher = User.query.filter_by(username=teacher_username).first()

        if not teacher:
            teacher = User(
                username=teacher_username,
                password=generate_password_hash('teacher123'),
                full_name=teacher_name,
                role='teacher'
            )
            db.session.add(teacher)

    db.session.commit()

    for course_data in SAMPLE_DATA:
        teacher = User.query.filter_by(
            full_name=course_data['teacher'].strip(),
            role='teacher'
        ).first()

        course = Course(
            name=course_data['name'],
            time=course_data['time'],
            capacity=course_data['capacity'],
            teacher_id=teacher.id,
        )
        db.session.add(course)
        db.session.flush()

        for student_name, grade in course_data['students']:
            cleaned_name = student_name.strip()
            student_username = cleaned_name.lower().replace(' ', '.')
            student = User.query.filter_by(username=student_username).first()

            if not student:
                student = User(
                    username=student_username,
                    password=generate_password_hash('student123'),
                    full_name=cleaned_name,
                    role='student'
                )
                db.session.add(student)
                db.session.flush()

            enrollment = Enrollment(
                student_id=student.id,
                course_id=course.id,
                grade=float(grade)
            )
            db.session.add(enrollment)

    db.session.commit()


def current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return db.session.get(User, user_id)


def login_required(role=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = current_user()

            if not user:
                flash('Please log in first.')
                return redirect(url_for('login'))

            if role and user.role != role:
                flash('You do not have permission to view that page.')
                return redirect(url_for('dashboard'))

            return func(*args, **kwargs)
        return wrapper
    return decorator


@app.context_processor
def inject_user():
    return {'current_user': current_user()}


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Logged in successfully.')
            return redirect(url_for('dashboard'))

        flash('Invalid username or password.')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))


@app.route('/toggle_theme')
def toggle_theme():
    current = session.get('theme', 'light')
    session['theme'] = 'dark' if current == 'light' else 'light'
    return redirect(request.referrer or url_for('dashboard'))


@app.route('/dashboard')
@login_required()
def dashboard():
    user = current_user()

    if user.role == 'student':
        return redirect(url_for('student_dashboard'))

    if user.role == 'teacher':
        return redirect(url_for('teacher_dashboard'))

    return redirect('/admin/')


@app.route('/student')
@login_required(role='student')
def student_dashboard():
    user = current_user()
    query = request.args.get('q', '').strip()
    teacher_filter = request.args.get('teacher', '').strip()

    my_enrollments = Enrollment.query.filter_by(student_id=user.id).all()
    enrolled_course_ids = {e.course_id for e in my_enrollments}

    courses_query = Course.query
    if query:
        courses_query = courses_query.filter(Course.name.ilike(f'%{query}%'))
    if teacher_filter:
        courses_query = courses_query.join(User, Course.teacher_id == User.id).filter(User.full_name == teacher_filter)

    all_courses = courses_query.order_by(Course.name).all()
    teacher_names = [name for (name,) in db.session.query(User.full_name).filter_by(role='teacher').order_by(User.full_name).all()]

    course_counts = {
        course.id: Enrollment.query.filter_by(course_id=course.id).count()
        for course in all_courses
    }

    graded_values = [e.grade for e in my_enrollments if e.grade is not None]
    average_grade = round(sum(graded_values) / len(graded_values), 2) if graded_values else None

    return render_template(
        'student.html',
        enrollments=my_enrollments,
        all_courses=all_courses,
        enrolled_course_ids=enrolled_course_ids,
        course_counts=course_counts,
        teacher_names=teacher_names,
        search_query=query,
        teacher_filter=teacher_filter,
        average_grade=average_grade
    )


@app.post('/enroll/<int:course_id>')
@login_required(role='student')
def enroll(course_id):
    user = current_user()
    course = Course.query.get_or_404(course_id)

    already_enrolled = Enrollment.query.filter_by(
        student_id=user.id,
        course_id=course.id
    ).first()

    if already_enrolled:
        flash('You are already enrolled in that class.')
        return redirect(url_for('student_dashboard'))

    enrolled_count = Enrollment.query.filter_by(course_id=course.id).count()

    if enrolled_count >= course.capacity:
        flash('That class is already full.')
        return redirect(url_for('student_dashboard'))

    enrollment = Enrollment(student_id=user.id, course_id=course.id, grade=None)
    db.session.add(enrollment)
    db.session.commit()

    flash(f'Added {course.name}.')
    return redirect(url_for('student_dashboard'))


@app.post('/drop/<int:enrollment_id>')
@login_required(role='student')
def drop_class(enrollment_id):
    user = current_user()
    enrollment = Enrollment.query.get_or_404(enrollment_id)

    if enrollment.student_id != user.id:
        flash('You cannot drop that class.')
        return redirect(url_for('student_dashboard'))

    course_name = enrollment.course.name
    db.session.delete(enrollment)
    db.session.commit()
    flash(f'Dropped {course_name}.')
    return redirect(url_for('student_dashboard'))


@app.route('/teacher')
@login_required(role='teacher')
def teacher_dashboard():
    user = current_user()
    courses = Course.query.filter_by(teacher_id=user.id).order_by(Course.name).all()

    course_counts = {
        course.id: Enrollment.query.filter_by(course_id=course.id).count()
        for course in courses
    }

    return render_template('teacher.html', courses=courses, course_counts=course_counts)


@app.route('/teacher/course/<int:course_id>')
@login_required(role='teacher')
def teacher_course(course_id):
    user = current_user()
    course = Course.query.get_or_404(course_id)

    if course.teacher_id != user.id:
        flash('That is not one of your courses.')
        return redirect(url_for('teacher_dashboard'))

    enrollments = Enrollment.query.filter_by(course_id=course.id).all()
    return render_template('teacher_course.html', course=course, enrollments=enrollments)


@app.post('/teacher/update_grade/<int:enrollment_id>')
@login_required(role='teacher')
def update_grade(enrollment_id):
    user = current_user()
    enrollment = Enrollment.query.get_or_404(enrollment_id)

    if enrollment.course.teacher_id != user.id:
        flash('You cannot edit grades for that course.')
        return redirect(url_for('teacher_dashboard'))

    raw_grade = request.form.get('grade', '').strip()

    if raw_grade == '':
        enrollment.grade = None
        db.session.commit()
        flash(f'Cleared grade for {enrollment.student.full_name}.')
        return redirect(url_for('teacher_course', course_id=enrollment.course_id))

    try:
        grade = float(raw_grade)
    except ValueError:
        flash('Please enter a valid number for the grade.')
        return redirect(url_for('teacher_course', course_id=enrollment.course_id))

    enrollment.grade = grade
    db.session.commit()

    flash(f'Updated grade for {enrollment.student.full_name}.')
    return redirect(url_for('teacher_course', course_id=enrollment.course_id))


class SecureAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        user = current_user()

        if not user or user.role != 'admin':
            flash('Admin access only.')
            return redirect(url_for('login'))

        return self.render('admin/index.html')


class SecureModelView(ModelView):
    def is_accessible(self):
        user = current_user()
        return bool(user and user.role == 'admin')

    def inaccessible_callback(self, name, **kwargs):
        flash('Admin access only.')
        return redirect(url_for('login'))


class UserAdminView(SecureModelView):
    column_exclude_list = ['password']  # hide hashed passwords in table


admin = Admin(app, name='School Admin', index_view=SecureAdminIndexView())
admin.add_view(UserAdminView(User, db.session))
admin.add_view(SecureModelView(Course, db.session))
admin.add_view(SecureModelView(Enrollment, db.session))


with app.app_context():
    db.create_all()
    seed_data()


if __name__ == '__main__':
    app.run(debug=True)
