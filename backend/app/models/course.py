from datetime import datetime
from .. import db

# ĐỊNH NGHĨA BẢNG TRUNG GIAN CHO QUAN HỆ NHIỀU-NHIỀU
# Bảng này kết nối User (sinh viên) và Course (khóa học)
enrollments = db.Table('enrollments',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True),
    db.Column('enrolled_at', db.DateTime, default=datetime.utcnow)
)


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Foreign Key tới giảng viên tạo khóa học
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Quan hệ 1-n: Một khóa học có nhiều bài giảng
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Course {self.title}>'


class Lesson(db.Model):
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    attachment_url = db.Column(db.String(300), nullable=True)
    order = db.Column(db.Integer, nullable=False)
    
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    # Quan hệ 1-n: Một bài giảng có nhiều bài tập
    exercises = db.relationship('Exercise', backref='lesson', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Lesson {self.title}>'