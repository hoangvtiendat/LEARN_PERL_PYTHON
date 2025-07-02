from app import create_app, db
from app.models import user, course, submission

# Gọi hàm create_app() để tạo ra instance của ứng dụng
app = create_app()

# Cấu hình shell context để tiện debug với lệnh 'flask shell'
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': user.User, 
        'Course': course.Course, 
        'Lesson': course.Lesson,
        'Exercise': submission.Exercise,
        'Submission': submission.Submission
    }