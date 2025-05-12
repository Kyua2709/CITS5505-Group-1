from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(
        __name__,
        static_folder="static",  # 指向 app/static
        template_folder="templates"  # 指向 app/templates
    )
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', '1') == '1'
    app.config['SECRET_KEY'] = os.getenv('SQLITE_SECRET')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/uploads.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    from .models import User, Upload

    with app.app_context():
        db.create_all()

    # 注册路由蓝图
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app  