import os
from dotenv import load_dotenv

# Tải các biến từ file .env
load_dotenv() 

# Lấy đường dẫn thư mục gốc của dự án
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # ĐÂY LÀ DÒNG QUAN TRỌNG NHẤT
    # Nó bảo Flask-SQLAlchemy tạo một file database SQLite
    # tên là 'app.db' bên trong thư mục 'instance' của backend.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '../../instance', 'app.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super-secret-jwt'

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEBUG = False
    FRONTEND_URL = os.environ.get('FRONTEND_URL') or 'http://localhost:5000'
    
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')