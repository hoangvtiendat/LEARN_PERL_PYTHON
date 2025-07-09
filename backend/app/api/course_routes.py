from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from ..models.user import User, UserRole
from ..models.course import Course, Lesson
from .. import db

# Tạo blueprint mới
course_bp = Blueprint('course_bp', __name__)


# --- Custom Decorator để kiểm tra vai trò Teacher ---
def teacher_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        if user and (user.role == UserRole.TEACHER or user.role == UserRole.ADMIN):
            return fn(*args, **kwargs)
        else:
            return jsonify({"error": "Yêu cầu quyền giảng viên hoặc admin"}), 403
    return wrapper


# --- API Routes ---

# 1. API tạo một khóa học mới (chỉ cho Teacher)
@course_bp.route('', methods=['POST'])
@teacher_required
def create_course():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    
    if not title:
        return jsonify({"error": "Tiêu đề là bắt buộc"}), 400
        
    current_teacher_id = get_jwt_identity()
    
    new_course = Course(
        title=title,
        description=description,
        teacher_id=current_teacher_id
    )
    db.session.add(new_course)
    db.session.commit()
    
    return jsonify({
        "id": new_course.id,
        "title": new_course.title,
        "description": new_course.description
    }), 201


# 2. API lấy danh sách tất cả khóa học (cho mọi user đã đăng nhập)
@course_bp.route('', methods=['GET'])
@jwt_required()
def get_all_courses():
    courses = Course.query.all()
    courses_list = [{
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "teacher_name": course.creator.full_name # Lấy tên giảng viên từ quan hệ
    } for course in courses]
    
    return jsonify(courses_list)


# 3. API lấy chi tiết một khóa học (bao gồm các bài giảng)
@course_bp.route('/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_details(course_id):
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({"error": "Không tìm thấy khóa học"}), 404
    
    lessons_list = [{
        "id": lesson.id,
        "title": lesson.title,
        "order": lesson.order
    } for lesson in course.lessons.order_by(Lesson.order)]
    
    return jsonify({
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "teacher_name": course.creator.full_name,
        "lessons": lessons_list
    })


# 4. API tạo một bài giảng mới cho một khóa học (chỉ cho Teacher)
@course_bp.route('/<int:course_id>/lessons', methods=['POST'])
@teacher_required
def create_lesson(course_id):
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({"error": "Không tìm thấy khóa học"}), 404
    
    # (Tùy chọn) Kiểm tra xem đúng giảng viên của khóa học mới được thêm bài
    current_teacher_id = get_jwt_identity()
    if course.teacher_id != current_teacher_id:
        return jsonify({"error": "Bạn không có quyền thêm bài giảng vào khóa học này"}), 403

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    order = data.get('order')
    attachment_url = data.get('attachment_url') 
    
    if not title or not content or order is None:
        return jsonify({"error": "Tiêu đề, nội dung và thứ tự là bắt buộc"}), 400
        
    new_lesson = Lesson(
        title=title,
        content=content,
        order=order,
        course_id=course.id,
        attachment_url=attachment_url  
    )
    db.session.add(new_lesson)
    db.session.commit()
    
    return jsonify({
        "id": new_lesson.id,
        "title": new_lesson.title,
        "content": new_lesson.content,      
        "order": new_lesson.order,
        "attachment_url": new_lesson.attachment_url
    }), 201
    
#5. API lấy bài giảng chi tiết
@course_bp.route('/lessons/<int:lesson_id>', methods=['GET'])
@jwt_required()
def get_lesson_details(lesson_id):
    lesson = db.session.get(Lesson, lesson_id)
    if not lesson:
        return jsonify({"error": "Không tìm thấy bài giảng"}), 404

    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    is_admin = user.role == UserRole.ADMIN
    is_teacher_of_course = user.id == lesson.course.teacher_id
    
    # Kiểm tra xem người dùng có phải là sinh viên đã ghi danh không
    is_enrolled_student = False
    if user.role == UserRole.STUDENT:
        # lesson.course là đối tượng Course chứa bài giảng này
        # user.enrolled_courses là danh sách các khóa học mà user đã ghi danh
        if lesson.course in user.enrolled_courses:
            is_enrolled_student = True

    # Nếu không phải admin, không phải giảng viên của khóa học, và cũng không phải sinh viên đã ghi danh
    if not (is_admin or is_teacher_of_course or is_enrolled_student):
        return jsonify({"error": "Bạn không có quyền xem bài giảng này"}), 403

    return jsonify({
        "id": lesson.id,
        "title": lesson.title,
        "content": lesson.content,
        "order": lesson.order,
        "attachment_url": lesson.attachment_url,
        "course_id": lesson.course_id
    })

# 6. API cho phép sinh viên ghi danh vào một khóa học
@course_bp.route('/<int:course_id>/enroll', methods=['POST'])
@jwt_required()
def enroll_in_course(course_id):
    # Lấy thông tin user đang đăng nhập
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    # Chỉ sinh viên mới được ghi danh
    if user.role != UserRole.STUDENT:
        return jsonify({"error": "Chỉ sinh viên mới có thể ghi danh"}), 403

    # Tìm khóa học
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({"error": "Không tìm thấy khóa học"}), 404

    # Kiểm tra xem sinh viên đã ghi danh khóa này chưa
    if course in user.enrolled_courses:
        return jsonify({"message": "Bạn đã ghi danh vào khóa học này từ trước"}), 409 # 409 Conflict

    # Thêm khóa học vào danh sách đã ghi danh của sinh viên
    user.enrolled_courses.append(course)
    db.session.commit()

    return jsonify({"message": f"Ghi danh vào khóa học '{course.title}' thành công!"})

# 7. API để giảng viên/admin thêm một sinh viên vào khóa học
@course_bp.route('/<int:course_id>/enroll-student', methods=['POST'])
@teacher_required
def enroll_student_by_teacher(course_id):
    # Lấy thông tin giảng viên/admin đang thực hiện
    current_teacher_id = get_jwt_identity()
    teacher = db.session.get(User, current_teacher_id)
    
    # Tìm khóa học
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({"error": "Không tìm thấy khóa học"}), 404

    # Chỉ admin hoặc giảng viên sở hữu khóa học mới có quyền
    if teacher.role != UserRole.ADMIN and course.teacher_id != current_teacher_id:
        return jsonify({"error": "Bạn không có quyền quản lý sinh viên trong khóa học này"}), 403

    # Lấy email của sinh viên cần thêm từ body
    data = request.get_json()
    student_email = data.get('student_email')
    if not student_email:
        return jsonify({"error": "Cần cung cấp email của sinh viên"}), 400

    # Tìm sinh viên trong database
    student_to_enroll = User.query.filter_by(email=student_email, role=UserRole.STUDENT).first()
    if not student_to_enroll:
        return jsonify({"error": f"Không tìm thấy sinh viên với email: {student_email}"}), 404

    # Kiểm tra xem sinh viên đã ở trong khóa học chưa
    if course in student_to_enroll.enrolled_courses:
        return jsonify({"message": "Sinh viên này đã có trong khóa học"}), 409

    # Thêm sinh viên vào khóa học
    student_to_enroll.enrolled_courses.append(course)
    db.session.commit()

    return jsonify({"message": f"Thêm sinh viên {student_email} vào khóa học thành công"})


# 8. API để giảng viên/admin xóa một sinh viên khỏi khóa học
@course_bp.route('/<int:course_id>/unenroll-student', methods=['POST'])
@teacher_required
def unenroll_student_by_teacher(course_id):
    current_teacher_id = get_jwt_identity()
    teacher = db.session.get(User, current_teacher_id)
    
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({"error": "Không tìm thấy khóa học"}), 404

    if teacher.role != UserRole.ADMIN and course.teacher_id != current_teacher_id:
        return jsonify({"error": "Bạn không có quyền quản lý sinh viên trong khóa học này"}), 403

    data = request.get_json()
    student_email = data.get('student_email')
    if not student_email:
        return jsonify({"error": "Cần cung cấp email của sinh viên"}), 400

    student_to_unenroll = User.query.filter_by(email=student_email, role=UserRole.STUDENT).first()
    if not student_to_unenroll:
        return jsonify({"error": f"Không tìm thấy sinh viên với email: {student_email}"}), 404

    # Kiểm tra xem sinh viên có thực sự trong khóa học không
    if course not in student_to_unenroll.enrolled_courses:
        return jsonify({"message": "Sinh viên này không có trong khóa học"}), 404

    # Xóa sinh viên khỏi khóa học
    student_to_unenroll.enrolled_courses.remove(course)
    db.session.commit()

    return jsonify({"message": f"Xóa sinh viên {student_email} khỏi khóa học thành công"})

#9. API Chỉnh sửa khoá học
@course_bp.route('/<int:course_id>', methods=['PUT'])
@teacher_required
def update_course(course_id):
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({"error": "Không tìm thấy khóa học"}), 404

    current_teacher_id = get_jwt_identity()
    if course.teacher_id != current_teacher_id:
        return jsonify({"error": "Bạn không có quyền chỉnh sửa khóa học này"}), 403

    data = request.get_json()
    title = data.get('title')
    description = data.get('description')

    if not title:
        return jsonify({"error": "Tiêu đề là bắt buộc"}), 400

    course.title = title
    course.description = description
    db.session.commit()

    return jsonify({
        "id": course.id,
        "title": course.title,
        "description": course.description
    }), 200
    
#10. API Xoá khoá học
@course_bp.route('/<int:course_id>', methods=['DELETE'])
@teacher_required
def delete_course(course_id):
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({"error": "Không tìm thấy khóa học"}), 404

    current_teacher_id = get_jwt_identity()
    if course.teacher_id != current_teacher_id:
        return jsonify({"error": "Bạn không có quyền xóa khóa học này"}), 403

    db.session.delete(course)
    db.session.commit()

    return jsonify({"message": "Xóa khóa học thành công"}), 200

#11. API chỉnh sửa bài giảng
@course_bp.route('/lessons/<int:lesson_id>', methods=['PUT'])
@teacher_required
def update_lesson(lesson_id):
    lesson = db.session.get(Lesson, lesson_id)
    if not lesson:
        return jsonify({"error": "Không tìm thấy bài giảng"}), 404

    current_teacher_id = get_jwt_identity()
    if lesson.course.teacher_id != current_teacher_id:
        return jsonify({"error": "Bạn không có quyền chỉnh sửa bài giảng này"}), 403

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    order = data.get('order')
    attachment_url = data.get('attachment_url')

    if not title or not content or order is None:
        return jsonify({"error": "Tiêu đề, nội dung và thứ tự là bắt buộc"}), 400

    lesson.title = title
    lesson.content = content
    lesson.order = order
    lesson.attachment_url = attachment_url
    db.session.commit()

    return jsonify({
        "id": lesson.id,
        "title": lesson.title,
        "content": lesson.content,
        "order": lesson.order,
        "attachment_url": lesson.attachment_url
    }), 200
    

#13. API xóa một bài giảng cụ thể
@course_bp.route('/lessons/<int:lesson_id>', methods=['DELETE'])
@teacher_required
def delete_lesson(lesson_id):
    # Lấy thông tin người dùng đang thực hiện hành động
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    # Tìm bài giảng cần xóa
    lesson = db.session.get(Lesson, lesson_id)
    if not lesson:
        return jsonify({"error": "Không tìm thấy bài giảng"}), 404

    # Kiểm tra quyền sở hữu: Phải là admin hoặc giảng viên đã tạo ra khóa học này
    is_admin = user.role == UserRole.ADMIN
    is_course_owner = lesson.course.teacher_id == current_user_id
    
    if not (is_admin or is_course_owner):
        return jsonify({"error": "Bạn không có quyền xóa bài giảng này"}), 403

    # Thực hiện xóa
    db.session.delete(lesson)
    db.session.commit()

    return jsonify({"message": "Bài giảng đã được xóa thành công"})