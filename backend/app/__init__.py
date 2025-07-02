from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager # Thêm dòng này
from .core.config import Config
from flask_mail import Mail


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager() 
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    # ... (phần import và đăng ký blueprint giữ nguyên)
    from .api.auth_routes import auth_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    return app

from . import models

