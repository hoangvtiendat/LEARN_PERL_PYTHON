import enum
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
# Quan trọng: Import bảng trung gian 'enrollments' từ file course.py
from .course import enrollments

class UserRole(enum.Enum):
    STUDENT = 'student'
    TEACHER = 'teacher'
    ADMIN = 'admin'

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    student_code = db.Column(db.String(20), unique=True, nullable=True, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    
    
    two_fa_enabled = db.Column(db.Boolean, default=False)
    two_fa_secret = db.Column(db.String(255), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- CÁC MỐI QUAN HỆ ---

    # 1-n: Giảng viên có thể tạo nhiều khóa học
    courses_created = db.relationship('Course', backref='creator', lazy='dynamic', foreign_keys='Course.teacher_id')
    
    # 1-n: Sinh viên có thể nộp nhiều bài tập
    submissions = db.relationship('Submission', backref='student', lazy='dynamic', foreign_keys='Submission.student_id')

    # n-n: Sinh viên có thể tham gia nhiều khóa học
    enrolled_courses = db.relationship(
        'Course', 
        secondary=enrollments,
        backref=db.backref('enrolled_students', lazy='dynamic'), 
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class UserLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    action = db.Column(db.String(50))
    detail = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)