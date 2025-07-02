import enum
from datetime import datetime
from .. import db

class ExerciseType(enum.Enum):
    CODE = 'code'
    MULTIPLE_CHOICE = 'multiple_choice'
    FILE_UPLOAD = 'file_upload'

class SubmissionStatus(enum.Enum):
    DRAFT = 'draft'
    SUBMITTED = 'submitted'
    GRADED = 'graded'

class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    exercise_type = db.Column(db.Enum(ExerciseType), nullable=False)
    
    # Dùng JSON để lưu test cases hoặc các lựa chọn trắc nghiệm
    test_cases = db.Column(db.JSON, nullable=True)
    
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    
    # Quan hệ 1-n: Một bài tập có nhiều bài nộp
    submissions = db.relationship('Submission', backref='exercise', lazy='dynamic', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Exercise {self.title}>'


class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)
    score = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(SubmissionStatus), nullable=False, default=SubmissionStatus.DRAFT)
    
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)

    def __repr__(self):
        return f'<Submission {self.id}>'