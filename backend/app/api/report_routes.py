from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User, UserRole
from ..models.submission import Exercise, Submission
from .. import db
import csv
from io import StringIO, BytesIO

report_bp = Blueprint('report_bp', __name__)

@report_bp.route('/exercise/<int:exercise_id>/report', methods=['GET'])
@jwt_required()
def exercise_report(exercise_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    exercise = Exercise.query.get(exercise_id)
    if not user or not exercise:
        return jsonify({'error': 'User hoặc bài tập không tồn tại'}), 404
    if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        return jsonify({'error': 'Không có quyền truy cập'}), 403

    submissions = Submission.query.filter_by(exercise_id=exercise_id).all()
    report = []
    for sub in submissions:
        report.append({
            'student_id': sub.student_id,
            'student_email': sub.student.email if sub.student else '',
            'score': sub.score,
            'status': sub.status.value if hasattr(sub.status, 'value') else sub.status,
            'submitted_at': sub.submitted_at.isoformat() if sub.submitted_at else None,
            'feedback': sub.feedback
        })
    return jsonify({'exercise_id': exercise_id, 'submissions': report})

@report_bp.route('/exercise/<int:exercise_id>/report/export', methods=['GET'])
@jwt_required()
def export_exercise_report(exercise_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    exercise = Exercise.query.get(exercise_id)
    if not user or not exercise:
        return jsonify({'error': 'User hoặc bài tập không tồn tại'}), 404
    if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        return jsonify({'error': 'Không có quyền truy cập'}), 403

    submissions = Submission.query.filter_by(exercise_id=exercise_id).all()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Student ID', 'Email', 'Score', 'Status', 'Submitted At', 'Feedback'])
    for sub in submissions:
        cw.writerow([
            sub.student_id,
            sub.student.email if sub.student else '',
            sub.score,
            sub.status.value if hasattr(sub.status, 'value') else sub.status,
            sub.submitted_at.isoformat() if sub.submitted_at else '',
            sub.feedback
        ])
    mem = BytesIO()
    mem.write(si.getvalue().encode('utf-8'))
    mem.seek(0)
    si.close()
    return send_file(
        mem,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'exercise_{exercise_id}_report.csv'
    ) 