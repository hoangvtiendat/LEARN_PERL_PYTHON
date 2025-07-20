from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User, UserRole
from ..models.course import Course, Lesson
from ..models.submission import Exercise, Submission
from .. import db
from datetime import datetime
import io
import sys
from contextlib import redirect_stdout

exercise_bp = Blueprint('exercise_bp', __name__)

# ==================== FC06: QUẢN LÝ BÀI TẬP ====================

@exercise_bp.route('/lessons/<int:lesson_id>/exercises', methods=['POST'])
@jwt_required()
def create_exercise(lesson_id):
    """Tạo bài tập mới cho bài giảng (chỉ giảng viên tạo khóa học)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    lesson = Lesson.query.get(lesson_id)
    if not user or not lesson:
        return jsonify({'error': 'User hoặc bài giảng không tồn tại'}), 404
    course = Course.query.get(lesson.course_id)
    if user.role != UserRole.TEACHER or course.teacher_id != user.id:
        return jsonify({'error': 'Chỉ giảng viên tạo khóa học mới được tạo bài tập'}), 403

    data = request.get_json()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    exercise_type = data.get('exercise_type', 'CODE')
    test_cases = data.get('test_cases', {})
    deadline = data.get('deadline') 

    if not title or not description:
        return jsonify({'error': 'Thiếu tiêu đề hoặc mô tả'}), 400

    exercise = Exercise(
        title=title,
        description=description,
        exercise_type=exercise_type,
        test_cases=test_cases,
        lesson_id=lesson_id
    )
    if hasattr(exercise, 'deadline') and deadline:
        exercise.deadline = datetime.strptime(deadline, '%Y-%m-%d %H:%M:%S')
    db.session.add(exercise)
    db.session.commit()
    
    
    # Gửi thông báo cho sinh viên đã ghi danh vào khóa học
    from ..models.notification import Notification
    for student in course.enrolled_students:
        notif = Notification(
            user_id=student.id,
            message=f'Bạn có bài tập mới: {exercise.title}'
        )
        db.session.add(notif)
    db.session.commit()
    return jsonify({'message': 'Tạo bài tập thành công', 'exercise_id': exercise.id}), 201

@exercise_bp.route('/exercises/<int:exercise_id>', methods=['PUT'])
@jwt_required()
def update_exercise(exercise_id):
    """Cập nhật bài tập (chỉ giảng viên tạo khóa học)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    exercise = Exercise.query.get(exercise_id)
    if not user or not exercise:
        return jsonify({'error': 'User hoặc bài tập không tồn tại'}), 404
    lesson = Lesson.query.get(exercise.lesson_id)
    course = Course.query.get(lesson.course_id)
    if user.role != UserRole.TEACHER or course.teacher_id != user.id:
        return jsonify({'error': 'Chỉ giảng viên tạo khóa học mới được sửa bài tập'}), 403

    data = request.get_json()
    if 'title' in data:
        exercise.title = data['title'].strip()
    if 'description' in data:
        exercise.description = data['description'].strip()
    if 'exercise_type' in data:
        exercise.exercise_type = data['exercise_type']
    if 'test_cases' in data:
        exercise.test_cases = data['test_cases']
    if hasattr(exercise, 'deadline') and 'deadline' in data:
        exercise.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d %H:%M:%S')
    db.session.commit()
    return jsonify({'message': 'Cập nhật bài tập thành công'}), 200

@exercise_bp.route('/exercises/<int:exercise_id>', methods=['DELETE'])
@jwt_required()
def delete_exercise(exercise_id):
    """Xóa bài tập (chỉ giảng viên tạo khóa học)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    exercise = Exercise.query.get(exercise_id)
    if not user or not exercise:
        return jsonify({'error': 'User hoặc bài tập không tồn tại'}), 404
    lesson = Lesson.query.get(exercise.lesson_id)
    course = Course.query.get(lesson.course_id)
    if user.role != UserRole.TEACHER or course.teacher_id != user.id:
        return jsonify({'error': 'Chỉ giảng viên tạo khóa học mới được xóa bài tập'}), 403

    db.session.delete(exercise)
    db.session.commit()
    return jsonify({'message': 'Xóa bài tập thành công'}), 200

@exercise_bp.route('/submissions/<int:submission_id>/grade', methods=['POST'])
@jwt_required()
def grade_submission(submission_id):
    """Chấm điểm bài nộp (chỉ giảng viên tạo khóa học)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    submission = Submission.query.get(submission_id)
    if not user or not submission:
        return jsonify({'error': 'User hoặc bài nộp không tồn tại'}), 404
    exercise = Exercise.query.get(submission.exercise_id)
    lesson = Lesson.query.get(exercise.lesson_id)
    course = Course.query.get(lesson.course_id)
    if user.role != UserRole.TEACHER or course.teacher_id != user.id:
        return jsonify({'error': 'Chỉ giảng viên tạo khóa học mới được chấm điểm'}), 403

    data = request.get_json()
    score = data.get('score')
    feedback = data.get('feedback', '')
    if score is None:
        return jsonify({'error': 'Thiếu điểm số'}), 400
    submission.score = float(score)
    submission.feedback = feedback
    submission.status = 'GRADED'
    db.session.commit()
    return jsonify({'message': 'Chấm điểm thành công'}), 200



@exercise_bp.route('/exercises/<int:exercise_id>/submit', methods=['POST'])
@jwt_required()
def submit_exercise(exercise_id):
    """Sinh viên nộp bài làm cho một bài tập và tự động chấm điểm nếu là CODE"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    exercise = Exercise.query.get(exercise_id)
    if not user or not exercise:
        return jsonify({'error': 'Người dùng hoặc bài tập không tồn tại'}), 404
    if user.role != UserRole.STUDENT:
        return jsonify({'error': 'Chỉ sinh viên mới được nộp bài'}), 403
    lesson = Lesson.query.get(exercise.lesson_id)
    course = Course.query.get(lesson.course_id)
    if course not in user.enrolled_courses:
        return jsonify({'error': 'Bạn chưa ghi danh vào khóa học này'}), 403
    data = request.get_json()
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'error': 'Bài làm không được để trống'}), 400

    # Kiểm tra nếu đã nộp bài thì cập nhật, chưa thì tạo mới
    submission = Submission.query.filter_by(student_id=user.id, exercise_id=exercise_id).first()
    if submission:
        submission.content = content
        submission.status = 'SUBMITTED'
        submission.submitted_at = datetime.utcnow()
    else:
        submission = Submission(
            content=content,
            status='SUBMITTED',
            student_id=user.id,
            exercise_id=exercise_id
        )
        db.session.add(submission)
    db.session.commit()

    # --- TỰ ĐỘNG CHẤM ĐIỂM NẾU LÀ BÀI CODE ---
    if exercise.exercise_type == "CODE" or (hasattr(exercise.exercise_type, 'value') and exercise.exercise_type.value == "code"):
        test_cases = exercise.test_cases
        if not isinstance(test_cases, list):
            return jsonify({'error': 'Test cases không hợp lệ'}), 400

        passed = 0
        total = len(test_cases)
        feedbacks = []
        code = content

        for idx, case in enumerate(test_cases):
            input_data = case.get('input')
            expected_output = str(case.get('output')).strip()
            try:
                f = io.StringIO()
                with redirect_stdout(f):
                    exec(code, {'input_data': input_data})
                output = f.getvalue().strip()
            except Exception as e:
                feedbacks.append(f"Test case {idx+1}: Lỗi khi chạy code: {e}")
                continue

            if output == expected_output:
                passed += 1
            else:
                feedbacks.append(
                    f"Test case {idx+1}: Sai. Input: {input_data}, Output của bạn: {output}, Kết quả đúng: {expected_output}"
                )

        score = round(10 * passed / total, 2) if total > 0 else 0
        feedback = "\n".join(feedbacks) if feedbacks else "Tốt lắm! Đúng hết các test case."
        submission.score = score
        submission.feedback = feedback
        submission.status = 'GRADED'
        db.session.commit()
        # Ghi log nộp bài
        from ..models.user import UserLog
        log = UserLog(user_id=user.id, action='submit', detail=f'Nộp bài {exercise.id}')
        db.session.add(log)
        db.session.commit()
        return jsonify({
            'message': 'Nộp bài và chấm điểm tự động thành công',
            'submission_id': submission.id,
            'score': score,
            'feedback': feedback
        }), 200

    db.session.commit()
    # Ghi log nộp bài
    from ..models.user import UserLog
    log = UserLog(user_id=user.id, action='submit', detail=f'Nộp bài {exercise.id}')
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'Nộp bài thành công', 'submission_id': submission.id}), 200

@exercise_bp.route('/lessons/<int:lesson_id>/exercises', methods=['GET'])
@jwt_required()
def get_exercises_for_lesson(lesson_id):
    """danh sách bài tập của bài """
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({'error': 'Bài giảng không tồn tại'}), 404
    exercises = lesson.exercises.all()
    data = []
    for ex in exercises:
        data.append({
            'id': ex.id,
            'title': ex.title,
            'description': ex.description,
            'exercise_type': ex.exercise_type.value if hasattr(ex.exercise_type, 'value') else ex.exercise_type,
            'lesson_id': ex.lesson_id
        })
    return jsonify({'exercises': data}), 200

@exercise_bp.route('/exercises/<int:exercise_id>', methods=['GET'])
@jwt_required()
def get_exercise_detail(exercise_id):
    """chi tiết bài tập"""
    ex = Exercise.query.get(exercise_id)
    if not ex:
        return jsonify({'error': 'Bài tập không tồn tại'}), 404
    data = {
        'id': ex.id,
        'title': ex.title,
        'description': ex.description,
        'exercise_type': ex.exercise_type.value if hasattr(ex.exercise_type, 'value') else ex.exercise_type,
        'test_cases': ex.test_cases,
        'lesson_id': ex.lesson_id
    }
    return jsonify({'exercise': data}), 200