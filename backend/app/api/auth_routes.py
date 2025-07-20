from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity,get_jwt
from ..models.user import User
from ..models.token_blocklist import TokenBlocklist
from .. import db
import pyotp
from flask import url_for, render_template # Thêm render_template
from flask_mail import Message # Thêm Message
from itsdangerous import URLSafeTimedSerializer
from flask import current_app # Thêm current_app
from .. import mail # Import mail từ __init__
from datetime import timedelta
import re
from sqlalchemy.exc import IntegrityError


# DÒNG QUAN TRỌNG: Tạo ra một đối tượng Blueprint tên là 'auth_bp'
auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Kiểm tra dữ liệu đầu vào
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email và mật khẩu là bắt buộc'}), 400

    # Kiểm tra email đã tồn tại chưa
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email này đã được sử dụng'}), 409

    if User.query.filter_by(email=data['student_code']).first():
        return jsonify({'error': 'Mã số sinh viên này đã được sử dụng'}), 409
    
    # Tạo user mới
    user = User(
        email=data['email'],
        full_name=data.get('full_name', ''),
        student_code=data.get('student_code', None),  
    )
    user.set_password(data['password'])
    
    
    
    # Validate email format
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, data['email']):
        return jsonify({'error': 'Email không hợp lệ'}), 400

    # Validate password (at least 8 chars, 1 letter, 1 number)
    password = data['password']
    if len(password) < 6 or not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
        return jsonify({'error': 'Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ và số'}), 400
    
    if len(data['student_code']) < 6:
        return jsonify({'error': 'Mã số sinh viên phải có ít nhất 6 ký tự'}), 400
    
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': f'Tạo tài khoản {user.email} thành công!'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email và mật khẩu là bắt buộc'}), 400

    user = User.query.filter_by(email=data['email']).first()

    # Kiểm tra user và mật khẩu
    if user is None or not user.check_password(data['password']):
        return jsonify({'error': 'Email hoặc mật khẩu không chính xác'}), 401
    
    # Ghi log đăng nhập thành công với thông tin đầy đủ
    from ..api.user_routes import log_user_activity
    log_user_activity(user.id, 'login', 'Đăng nhập thành công', request)
    
    if user.two_fa_enabled:
        # Nếu 2FA được bật, gửi OTP qua email
        otp = pyotp.TOTP(user.two_fa_secret).now()
        
        # print(f"DEBUG: Mail Sender is: {current_app.config.get('MAIL_USERNAME')}")
        # print(f"DEBUG: Recipient is: {user.email}")

        print("--- DEBUGGING MAIL CONSTRUCTOR ---")
        print(f"Subject Type: {type('Mã xác thực đăng nhập (OTP)')}")
        print(f"Subject Value: {'Mã xác thực đăng nhập (OTP)'}")
        print(f"Sender Type: {type(current_app.config.get('MAIL_USERNAME'))}")
        print(f"Sender Value: {current_app.config.get('MAIL_USERNAME')}")
        print("--- END DEBUG ---")

        msg = Message('Mã xác thực đăng nhập (OTP)',
                      sender=current_app.config['MAIL_USERNAME'],
                      recipients=[user.email])
        msg.body = f'Mã OTP của bạn là: {otp}. Mã có hiệu lực trong 60 giây.'
        mail.send(msg)
        
        # Cấp một token tạm thời, chỉ dùng để xác thực OTP
        temp_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=5))
        
        return jsonify({
            'message': 'Vui lòng nhập mã OTP đã được gửi đến email của bạn.',
            '2fa_required': True,
            'temp_token': temp_token # Frontend sẽ dùng token này cho bước 2
        }), 200
    else:
        # Nếu 2FA không bật, đăng nhập như bình thường
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify(access_token=access_token, refresh_token=refresh_token)

@auth_bp.route('/verify-2fa', methods=['POST'])
@jwt_required() # Yêu cầu token (tạm thời) để truy cập
def verify_2fa():
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    print(2)
    # user = db.session.get(User, current_user_id)
    data = request.get_json()
    otp_from_user = data.get('otp')
    if not otp_from_user:
        return jsonify({'error': 'Mã OTP là bắt buộc'}), 400

    # Xác thực mã OTP 
    totp = pyotp.TOTP(user.two_fa_secret)
    # if totp.verify(otp_from_user):
    if totp.verify(otp_from_user, valid_window=2):
        # Nếu OTP đúng, cấp access token chính thức
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200
    else:
        return jsonify({'error': 'Mã OTP không hợp lệ'}), 401
    
    
def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, expiration=3600): # Token hết hạn sau 1 giờ
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=expiration
        )
    except:
        return None
    return email

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    if not data or not data.get('email'):
        return jsonify({'error': 'Email là bắt buộc'}), 400
    
    email = data['email']
    user = User.query.filter_by(email=email).first()

    # Kể cả không tìm thấy user, vẫn trả về success để tránh lộ thông tin
    if user:
        token = generate_reset_token(email)
        # Link này sẽ trỏ tới trang reset password của frontend
        frontend_url = current_app.config.get('FRONTEND_URL')
        reset_url = f"{frontend_url}/reset-password?token={token}"

        # Gửi email
        msg = Message('Yêu cầu đặt lại mật khẩu',
                      sender=current_app.config['MAIL_USERNAME'],
                      recipients=[user.email])
        msg.body = f'''Để đặt lại mật khẩu của bạn, hãy truy cập vào link sau:
{reset_url}

Nếu bạn không phải là người yêu cầu, vui lòng bỏ qua email này.
'''
        mail.send(msg)

    return jsonify({'message': 'Nếu email của bạn tồn tại trong hệ thống, bạn sẽ nhận được một link để đặt lại mật khẩu.'})

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():



    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')

    if not token or not new_password:
        return jsonify({'error': 'Token và mật khẩu mới là bắt buộc'}), 400

    email = verify_reset_token(token)
    if email is None:
        return jsonify({'error': 'Token không hợp lệ hoặc đã hết hạn'}), 401
    
    user = User.query.filter_by(email=email).first()
    if user:
        user.set_password(new_password)
        db.session.commit()
        return jsonify({'message': 'Mật khẩu đã được cập nhật thành công.'})
    
    return jsonify({'error': 'Người dùng không tồn tại'}), 404


@auth_bp.route('/toggle-2fa', methods=['POST'])
@jwt_required()
def toggle_2fa():
    # Lấy id của user đang đăng nhập từ access token
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    if not user:
        return jsonify({"error": "Người dùng không tồn tại"}), 404

    data = request.get_json()
    enable_flag = data.get('enable')

    if enable_flag is None:
        return jsonify({"error": "Trường 'enable' (true/false) là bắt buộc"}), 400

    if enable_flag:
        # --- Luồng BẬT 2FA ---
        if user.two_fa_enabled:
            return jsonify({"message": "2FA đã được bật từ trước."}), 200

        # Tạo secret key mới và lưu vào database
        user.two_fa_secret = pyotp.random_base32()
        user.two_fa_enabled = True
        db.session.commit()

        # Tạo URI để frontend có thể tạo mã QR Code
        # User sẽ dùng app Google Authenticator hoặc tương tự để quét mã này
        provisioning_uri = pyotp.TOTP(user.two_fa_secret).provisioning_uri(
            name=user.email,
            issuer_name="PerlPython App"
        )
        
        return jsonify({
            "message": "Để hoàn tất, hãy quét mã QR bằng ứng dụng xác thực của bạn.",
            "provisioning_uri": provisioning_uri,
            "secret_key": user.two_fa_secret # Trả về để user có thể nhập thủ công
        }), 200
    else:
        # --- Luồng TẮT 2FA ---
        user.two_fa_enabled = False
        user.two_fa_secret = None  # Xóa secret key để bảo mật
        db.session.commit()
        return jsonify({"message": "Xác thực hai lớp đã được tắt."}), 200


# Sửa lại hoàn toàn hàm refresh
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()

    # Lấy jti (id duy nhất) của refresh token cũ và thêm vào blocklist
    jti = get_jwt()["jti"]
    db.session.add(TokenBlocklist(jti=jti))
    db.session.commit()

    # Tạo ra access token và refresh token MỚI
    new_access_token = create_access_token(identity=current_user_id)
    new_refresh_token = create_refresh_token(identity=current_user_id)

    return jsonify(access_token=new_access_token, refresh_token=new_refresh_token)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required(refresh=True) # Yêu cầu refresh token để đăng xuất
def logout():
    jti = get_jwt()["jti"]
    db.session.add(TokenBlocklist(jti=jti))
    db.session.commit()
    return jsonify(message="Đăng xuất thành công. Refresh token đã được thu hồi.")