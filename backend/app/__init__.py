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
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    from .models.token_blocklist import TokenBlocklist
    jti = jwt_payload["jti"]
    token = TokenBlocklist.query.filter_by(jti=jti).first()
    return token is not None # Trả về True nếu token tồn tại trong blocklist

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    # ... (phần import và đăng ký blueprint giữ nguyên)
    from .api.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
    from .api.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from .api.ai_routes import ai_bp
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    
    from .api.course_routes import course_bp
    app.register_blueprint(course_bp, url_prefix='/api/courses')
    
    from .api.exercise_routes import exercise_bp
    app.register_blueprint(exercise_bp, url_prefix='/api/exercise')
    
    from .api.ide_routes import ide_bp
    app.register_blueprint(ide_bp, url_prefix='/api/ide')
    
    from .api.report_routes import report_bp
    app.register_blueprint(report_bp, url_prefix='/api/report')
    
    from .api.search_routes import search_bp
    app.register_blueprint(search_bp, url_prefix='/api/search')

    from .api.notification_routes import notification_bp
    app.register_blueprint(notification_bp, url_prefix='/api')
    
    return app


from . import models

