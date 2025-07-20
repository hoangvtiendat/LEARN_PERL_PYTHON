
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
from datetime import datetime
from flask import current_app

user_bp = Blueprint('user_bp', __name__)


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
        # Ghi log cập nhật thông tin cá nhân với thông tin đầy đủ
        log_user_activity(user.id, 'update_profile', 'Cập nhật thông tin cá nhân', request)
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
        # Ghi log đổi mật khẩu
        log_user_activity(user.id, 'change_password', 'Đổi mật khẩu thành công', request)
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

# ===== FC20: LOGGING HỆ THỐNG - THEO DÕI LOG HOẠT ĐỘNG NGƯỜI DÙNG =====

@user_bp.route('/logs', methods=['GET'])
@admin_required
def get_logs():
    """Lấy danh sách log với thông tin đầy đủ"""
    from ..models.user import UserLog
    from flask import request
    
    # Lấy tham số phân trang và lọc
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    action_filter = request.args.get('action', '')
    user_filter = request.args.get('user', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Query cơ bản
    query = UserLog.query
    
    # Áp dụng các bộ lọc
    if action_filter:
        query = query.filter(UserLog.action.contains(action_filter))
    if user_filter:
        query = query.filter(
            db.or_(
                UserLog.username.contains(user_filter),
                UserLog.email.contains(user_filter),
                UserLog.full_name.contains(user_filter)
            )
        )
    if date_from:
        try:
            from datetime import datetime
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(UserLog.timestamp >= date_from_obj)
        except ValueError:
            pass
    if date_to:
        try:
            from datetime import datetime
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(UserLog.timestamp <= date_to_obj)
        except ValueError:
            pass
    
    # Sắp xếp theo thời gian mới nhất
    query = query.order_by(UserLog.timestamp.desc())
    
    # Phân trang
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    logs_data = []
    for log in pagination.items:
        logs_data.append({
            "id": log.id,
            "user_id": log.user_id,
            "username": log.username or (log.user.email if log.user else ''),
            "email": log.email or (log.user.email if log.user else ''),
            "full_name": log.full_name or (log.user.full_name if log.user else ''),
            "role": log.role or (log.user.role.value if log.user else ''),
            "status": log.status or 'active',
            "action": log.action,
            "detail": log.detail,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None
        })
    
    return jsonify({
        "logs": logs_data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
    }), 200

@user_bp.route('/logs/<int:log_id>', methods=['GET'])
@admin_required
def get_log_detail(log_id):
    """Lấy chi tiết một log cụ thể"""
    from ..models.user import UserLog
    log = UserLog.query.get(log_id)
    if not log:
        return jsonify({'error': 'Log không tồn tại'}), 404
    
    return jsonify({
        "id": log.id,
        "user_id": log.user_id,
        "username": log.username or (log.user.email if log.user else ''),
        "email": log.email or (log.user.email if log.user else ''),
        "full_name": log.full_name or (log.user.full_name if log.user else ''),
        "role": log.role or (log.user.role.value if log.user else ''),
        "status": log.status or 'active',
        "action": log.action,
        "detail": log.detail,
        "ip_address": log.ip_address,
        "user_agent": log.user_agent,
        "timestamp": log.timestamp.isoformat() if log.timestamp else None
    }), 200

@user_bp.route('/logs/<int:log_id>', methods=['PUT'])
@admin_required
def update_log(log_id):
    """Chỉnh sửa log (chỉ cho phép sửa detail và status)"""
    from ..models.user import UserLog
    log = UserLog.query.get(log_id)
    if not log:
        return jsonify({'error': 'Log không tồn tại'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dữ liệu không hợp lệ'}), 400
    
    # Chỉ cho phép sửa một số trường nhất định
    if 'detail' in data:
        log.detail = data['detail']
    if 'status' in data:
        log.status = data['status']
    if 'action' in data:
        log.action = data['action']
    
    try:
        db.session.commit()
        return jsonify({'message': 'Cập nhật log thành công'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Có lỗi xảy ra khi cập nhật log'}), 500

@user_bp.route('/logs/<int:log_id>', methods=['DELETE'])
@admin_required
def delete_log(log_id):
    """Xóa log"""
    from ..models.user import UserLog
    log = UserLog.query.get(log_id)
    if not log:
        return jsonify({'error': 'Log không tồn tại'}), 404
    
    try:
        db.session.delete(log)
        db.session.commit()
        return jsonify({'message': 'Xóa log thành công'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Có lỗi xảy ra khi xóa log'}), 500

@user_bp.route('/logs/export', methods=['GET'])
@admin_required
def export_logs():
    """Xuất logs ra file CSV"""
    from ..models.user import UserLog
    import csv
    from io import StringIO, BytesIO
    from flask import send_file
    from datetime import datetime

    # Lấy tất cả logs
    logs = UserLog.query.order_by(UserLog.timestamp.desc()).all()

    # Ghi CSV vào StringIO (text)
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Username', 'Email', 'Họ tên', 'Vai trò', 'Trạng thái', 
                 'Hành động', 'Chi tiết', 'IP Address', 'User Agent', 'Thời gian'])
    for log in logs:
        cw.writerow([
            log.id,
            log.username or (log.user.email if log.user else ''),
            log.email or (log.user.email if log.user else ''),
            log.full_name or (log.user.full_name if log.user else ''),
            log.role or (log.user.role.value if log.user else ''),
            log.status or 'active',
            log.action,
            log.detail,
            log.ip_address,
            log.user_agent,
            log.timestamp.isoformat() if log.timestamp else ''
        ])
    # Encode sang bytes
    mem = BytesIO()
    mem.write(si.getvalue().encode('utf-8'))
    mem.seek(0)
    si.close()

    return send_file(
        mem,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'user_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )


# Hàm tiện ích để ghi log với thông tin đầy đủ
def log_user_activity(user_id, action, detail, request_obj=None):
    """Ghi log hoạt động người dùng với thông tin đầy đủ"""
    from ..models.user import UserLog, User
    
    user = User.query.get(user_id) if user_id else None
    
    log = UserLog(
        user_id=user_id,
        username=user.email if user else None,
        email=user.email if user else None,
        full_name=user.full_name if user else None,
        role=user.role.value if user else None,
        status='active',
        action=action,
        detail=detail,
        ip_address=request_obj.remote_addr if request_obj else None,
        user_agent=request_obj.headers.get('User-Agent') if request_obj else None
    )
    
    db.session.add(log)
    db.session.commit()
    return log
@user_bp.route('/admin/backup', methods=['POST'])
@admin_required
def backup_db():
    # Lấy thông tin từ config thay vì biến cứng
    db_name = current_app.config['DB_NAME']
    db_user = current_app.config['DB_USER']
    db_password = current_app.config['DB_PASSWORD']
    mysqldump_path = current_app.config['MYSQLDUMP_PATH']

    if not all([db_name, db_user, db_password, mysqldump_path]):
        return jsonify({'error': 'Cấu hình database cho backup chưa đầy đủ'}), 500

    BACKUP_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'db_backups'))
    os.makedirs(BACKUP_FOLDER, exist_ok=True)
    backup_file = os.path.join(BACKUP_FOLDER, f'backup_{db_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sql')

    cmd = [
        mysqldump_path,
        f'-u{db_user}',
        f'-p{db_password}',
        db_name,
        '--result-file=' + backup_file # Dùng --result-file an toàn hơn
    ]
    try:
        subprocess.run(cmd, check=True) # Dùng subprocess.run an toàn hơn
        return send_file(backup_file, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'Backup thất bại: {e}'}), 500

@user_bp.route('/admin/restore', methods=['POST'])
@admin_required
def restore_db():
    if 'file' not in request.files:
        return jsonify({'error': 'Chưa upload file backup'}), 400

    # Lấy thông tin từ config
    db_name = current_app.config['DB_NAME']
    db_user = current_app.config['DB_USER']
    db_password = current_app.config['DB_PASSWORD']

    if not all([db_name, db_user, db_password]):
        return jsonify({'error': 'Cấu hình database cho restore chưa đầy đủ'}), 500

    file = request.files['file']
    filename = secure_filename(file.filename)
    # Lưu file tạm thời để restore
    temp_backup_path = os.path.join(BACKUP_FOLDER, filename)
    file.save(temp_backup_path)

    cmd = [
        'mysql',
        f'-u{db_user}',
        f'-p{db_password}',
        db_name
    ]
    try:
        with open(temp_backup_path, 'rb') as f:
            subprocess.run(cmd, stdin=f, check=True) # Dùng subprocess.run
        os.remove(temp_backup_path) # Xóa file tạm sau khi restore
        return jsonify({'message': 'Phục hồi dữ liệu thành công'}), 200
    except Exception as e:
        os.remove(temp_backup_path) # Xóa file tạm nếu có lỗi
        return jsonify({'error': f'Phục hồi thất bại: {e}'}), 500