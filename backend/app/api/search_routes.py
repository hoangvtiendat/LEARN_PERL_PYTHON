from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models.course import Course, Lesson
from ..models.submission import Exercise
from sqlalchemy import or_

search_bp = Blueprint('search_bp', __name__)

@search_bp.route('', methods=['GET'])
@jwt_required()
def search():
    # Lấy tham số từ URL, ví dụ: /api/search?q=python&type=course
    keyword = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all').lower() # Mặc định tìm tất cả

    if not keyword:
        return jsonify([])

    search_pattern = f"%{keyword}%"
    results = []

    # Tìm kiếm trong Khóa học
    if search_type in ['all', 'course']:
        courses = Course.query.filter(
            or_(
                Course.title.ilike(search_pattern),
                Course.description.ilike(search_pattern)
            )
        ).limit(10).all()
        for c in courses:
            results.append({"id": c.id, "title": c.title, "type": "course"})

    # Tìm kiếm trong Bài giảng
    if search_type in ['all', 'lesson']:
        lessons = Lesson.query.filter(
            or_(
                Lesson.title.ilike(search_pattern),
                Lesson.content.ilike(search_pattern)
            )
        ).limit(10).all()
        for l in lessons:
            results.append({"id": l.id, "title": l.title, "type": "lesson", "course_id": l.course_id})

    # Tìm kiếm trong Bài tập
    if search_type in ['all', 'exercise']:
        exercises = Exercise.query.filter(
            or_(
                Exercise.title.ilike(search_pattern),
                Exercise.description.ilike(search_pattern)
            )
        ).limit(10).all()
        for e in exercises:
            results.append({"id": e.id, "title": e.title, "type": "exercise", "lesson_id": e.lesson_id})

    # Lưu ý: Việc tìm kiếm người dùng nên được giới hạn cho Admin để đảm bảo quyền riêng tư.
    # Chức năng này có thể được thêm vào admin routes sau.

    return jsonify(results)