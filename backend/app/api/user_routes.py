from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User
from .. import db
import pyotp

user_bp = Blueprint('user_bp', __name__)

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

@user_bp.route('/profile/toggle-2fa', methods=['POST'])
@jwt_required()
def toggle_2fa():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'Người dùng không tồn tại'}), 404
    data = request.get_json()
    enable_flag = data.get('enable')
    if enable_flag is None:
        return jsonify({'error': "Trường 'enable' (true/false) là bắt buộc"}), 400
    if enable_flag:
        if user.two_fa_enabled:
            return jsonify({'message': '2FA đã được bật từ trước.'}), 200
        user.two_fa_secret = pyotp.random_base32()
        user.two_fa_enabled = True
        db.session.commit()
        provisioning_uri = pyotp.TOTP(user.two_fa_secret).provisioning_uri(
            name=user.email,
            issuer_name="PerlPython App"
        )
        return jsonify({
            'message': 'Đã bật 2FA. Hãy quét mã QR bằng ứng dụng xác thực.',
            'provisioning_uri': provisioning_uri,
            'secret_key': user.two_fa_secret
        }), 200
    else:
        user.two_fa_enabled = False
        user.two_fa_secret = None
        db.session.commit()
        return jsonify({'message': 'Đã tắt xác thực hai lớp.'}), 200



