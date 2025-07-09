from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User, UserRole
from ..models.course import Course, Lesson
from ..models.submission import Exercise, Submission, SubmissionStatus, ExerciseType
from .. import db
from .course_routes import teacher_required # Import decorator từ course_routes

exercise_bp = Blueprint('exercise_bp', __name__)


# 1. API tạo một bài tập mới cho một bài giảng (chỉ cho Teacher)
# URL này thể hiện rõ quan hệ: exercise nằm trong lesson
@exercise_bp.route('/lessons/<int:lesson_id>/exercises', methods=['POST'])
@teacher_required
def create_exercise_for_lesson(lesson_id):
    lesson = db.session.get(Lesson, lesson_id)
    if not lesson:
        return jsonify({"error": "Không tìm thấy bài giảng"}), 404

    # Kiểm tra xem giảng viên có phải là người tạo ra khóa học chứa bài giảng này không
    current_teacher_id = get_jwt_identity()
    if lesson.course.teacher_id != current_teacher_id:
        return jsonify({"error": "Không có quyền thêm bài tập vào bài giảng này"}), 403

    data = request.get_json()
    exercise_type_str = data.get('exercise_type')
    
    # Chuyển đổi string từ request thành Enum
    try:
        exercise_type = ExerciseType(exercise_type_str)
    except ValueError:
        return jsonify({"error": f"Loại bài tập không hợp lệ: {exercise_type_str}"}), 400

    new_exercise = Exercise(
        title=data.get('title'),
        description=data.get('description'),
        exercise_type=exercise_type,
        test_cases=data.get('test_cases', {}), # Dùng cho việc chấm code tự động
        lesson_id=lesson_id
    )
    db.session.add(new_exercise)
    db.session.commit()
    
    return jsonify({"message": "Tạo bài tập thành công", "exercise_id": new_exercise.id}), 201


# 2. API để một sinh viên nộp bài cho một bài tập
@exercise_bp.route('/exercises/<int:exercise_id>/submit', methods=['POST'])
@jwt_required()
def submit_exercise(exercise_id):
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    # Chỉ sinh viên mới được nộp bài
    if user.role != UserRole.STUDENT:
        return jsonify({"error": "Chỉ sinh viên mới có thể nộp bài"}), 403
    
    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return jsonify({"error": "Không tìm thấy bài tập"}), 404

    data = request.get_json()
    content = data.get('content')

    # Tìm xem sinh viên đã nộp bài này chưa, nếu có thì cập nhật, không thì tạo mới
    submission = Submission.query.filter_by(student_id=current_user_id, exercise_id=exercise_id).first()
    
    if submission:
        # Cập nhật bài nộp cũ
        submission.content = content
        submission.status = SubmissionStatus.SUBMITTED
    else:
        # Tạo bài nộp mới
        submission = Submission(
            content=content,
            status=SubmissionStatus.SUBMITTED,
            student_id=current_user_id,
            exercise_id=exercise_id
        )
        db.session.add(submission)
    
    db.session.commit()
    
    # TODO: Kích hoạt một tiến trình chấm điểm tự động ở đây
    # Ví dụ: auto_grade.delay(submission.id)

    return jsonify({
        "message": "Nộp bài thành công!",
        "submission_id": submission.id,
        "status": submission.status.value
    })


# 3. API để xem một bài nộp cụ thể
# Chỉ sinh viên nộp bài hoặc giảng viên của khóa học mới được xem
@exercise_bp.route('/submissions/<int:submission_id>', methods=['GET'])
@jwt_required()
def get_submission(submission_id):
    submission = db.session.get(Submission, submission_id)
    if not submission:
        return jsonify({"error": "Không tìm thấy bài nộp"}), 404

    current_user_id = get_jwt_identity()
    
    # Kiểm tra quyền truy cập
    teacher_of_course = submission.exercise.lesson.course.creator
    if submission.student_id != current_user_id and teacher_of_course.id != current_user_id:
        return jsonify({"error": "Không có quyền xem bài nộp này"}), 403

    return jsonify({
        "id": submission.id,
        "content": submission.content,
        "score": submission.score,
        "feedback": submission.feedback,
        "status": submission.status.value,
        "student_id": submission.student_id
    })