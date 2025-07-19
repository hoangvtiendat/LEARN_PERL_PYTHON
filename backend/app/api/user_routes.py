
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User
from .. import db
import pyotp
from functools import wraps
from ..models.user import UserRole
import subprocess
import os
from flask import send_file
from werkzeug.utils import secure_filename

user_bp = Blueprint('user_bp', __name__)

MYSQL_DB = 'learn_perl_python'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'
BACKUP_FOLDER = 'db_backups'
os.makedirs(BACKUP_FOLDER, exist_ok=True)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'Người dùng không tồn tại'}), 404
    return jsonify({
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'role': user.role.value,
        'two_fa_enabled': user.two_fa_enabled,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'updated_at': user.updated_at.isoformat() if user.updated_at else None
    }), 200

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'Người dùng không tồn tại'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dữ liệu không hợp lệ'}), 400
    if 'full_name' in data:
        if not data['full_name'] or len(data['full_name'].strip()) == 0:
            return jsonify({'error': 'Họ tên không được để trống'}), 400
        user.full_name = data['full_name'].strip()
    if 'email' in data:
        new_email = data['email'].strip().lower()
        if not new_email:
            return jsonify({'error': 'Email không được để trống'}), 400
        if '@' not in new_email or '.' not in new_email:
            return jsonify({'error': 'Email không đúng định dạng'}), 400
        existing_user = User.query.filter_by(email=new_email).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({'error': 'Email này đã được sử dụng bởi tài khoản khác'}), 409
        user.email = new_email
    try:
        db.session.commit()
        # Ghi log cập nhật thông tin cá nhân
        from ..models.user import UserLog
        log = UserLog(user_id=user.id, action='update_profile', detail='Cập nhật thông tin cá nhân')
        db.session.add(log)
        db.session.commit()
        return jsonify({
            'message': 'Cập nhật thông tin thành công',
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role.value,
                'two_fa_enabled': user.two_fa_enabled,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Có lỗi xảy ra khi cập nhật thông tin'}), 500

@user_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'Người dùng không tồn tại'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dữ liệu không hợp lệ'}), 400
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    if not current_password:
        return jsonify({'error': 'Mật khẩu hiện tại là bắt buộc'}), 400
    if not new_password:
        return jsonify({'error': 'Mật khẩu mới là bắt buộc'}), 400
    if not confirm_password:
        return jsonify({'error': 'Xác nhận mật khẩu mới là bắt buộc'}), 400
    if not user.check_password(current_password):
        return jsonify({'error': 'Mật khẩu hiện tại không chính xác'}), 401
    if new_password != confirm_password:
        return jsonify({'error': 'Mật khẩu mới và xác nhận không khớp'}), 400
    if len(new_password) < 6:
        return jsonify({'error': 'Mật khẩu mới phải có ít nhất 6 ký tự'}), 400
    if user.check_password(new_password):
        return jsonify({'error': 'Mật khẩu mới không được giống mật khẩu cũ'}), 400
    try:
        user.set_password(new_password)
        db.session.commit()
        return jsonify({'message': 'Đổi mật khẩu thành công'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Có lỗi xảy ra khi đổi mật khẩu'}), 500

@user_bp.route('/profile/2fa-status', methods=['GET'])
@jwt_required()
def get_2fa_status():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'Người dùng không tồn tại'}), 404
    return jsonify({
        'two_fa_enabled': user.two_fa_enabled,
        'has_secret': bool(user.two_fa_secret)
    }), 200

# ===== FC14: ADMIN QUẢN LÝ NGƯỜI DÙNG =====
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if user and user.role == UserRole.ADMIN:
            return fn(*args, **kwargs)
        else:
            return jsonify({"error": "Yêu cầu quyền admin"}), 403
    return wrapper

@user_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    users = User.query.all()
    data = []
    for user in users:
        data.append({
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "student_code": getattr(user, "student_code", None)
        })
    return jsonify(data), 200

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Người dùng không tồn tại'}), 404
    data = request.get_json()
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'email' in data:
        user.email = data['email']
    if 'role' in data:
        try:
            user.role = UserRole[data['role']]
        except KeyError:
            return jsonify({'error': 'Role không hợp lệ'}), 400
    db.session.commit()
    return jsonify({'message': 'Cập nhật thành công'}), 200

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Người dùng không tồn tại'}), 404

    # Xóa tất cả submission của user này trước
    from ..models.submission import Submission
    Submission.query.filter_by(student_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Xóa người dùng thành công'}), 200

# Đã xóa API /logs cho admin xem log hoạt động người dùng

@user_bp.route('/logs', methods=['GET'])
@admin_required
def get_logs():
    from ..models.user import UserLog
    logs = UserLog.query.order_by(UserLog.timestamp.desc()).all()
    data = []
    for log in logs:
        data.append({
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "detail": log.detail,
            "timestamp": log.timestamp.isoformat()
        })
    return jsonify(data), 200

@user_bp.route('/admin/backup', methods=['POST'])
@admin_required
def backup_db():
    MYSQL_DB = 'learn_perl_python'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '123456'
    # Đặt thư mục backup ở backend/db_backups/
    BACKUP_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'db_backups'))
    os.makedirs(BACKUP_FOLDER, exist_ok=True)
    backup_file = os.path.join(BACKUP_FOLDER, f'backup_{MYSQL_DB}.sql')
    cmd = [
        r'C:\Program Files\MySQL\MySQL Workbench 8.0 CE\mysqldump.exe',
        f'-u{MYSQL_USER}',
        f'-p{MYSQL_PASSWORD}',
        MYSQL_DB,
        '-r', backup_file
    ]
    try:
        subprocess.check_call(cmd)
        return send_file(backup_file, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'Backup thất bại: {e}'}), 500

@user_bp.route('/admin/restore', methods=['POST'])
@admin_required
def restore_db():
    if 'file' not in request.files:
        return jsonify({'error': 'Chưa upload file backup'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    backup_path = os.path.join(BACKUP_FOLDER, filename)
    file.save(backup_path)
    cmd = [
        'mysql',
        f'-u{MYSQL_USER}',
        f'-p{MYSQL_PASSWORD}',
        MYSQL_DB
    ]
    try:
        with open(backup_path, 'rb') as f:
            subprocess.check_call(cmd, stdin=f)
        return jsonify({'message': 'Phục hồi dữ liệu thành công'}), 200
    except Exception as e:
        return jsonify({'error': f'Phục hồi thất bại: {e}'}), 500
