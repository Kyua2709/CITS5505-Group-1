from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
import os
from dotenv import load_dotenv

load_dotenv()  # 加载 .flaskenv 文件

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

def create_app():
    app = Flask(
        __name__,
        static_folder="static",  # Points to app/static
        template_folder="templates"  # Points to app/templates
    )
    
    app_folder = os.path.dirname(os.path.abspath(__file__))
    instance_folder = os.path.abspath(os.path.join(app_folder, '..', 'instance'))
    upload_folder = os.path.join(instance_folder, 'uploads')
    sqlite_db = os.path.join(instance_folder, 'database.db')
    os.makedirs(upload_folder, exist_ok=True)
    
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', '1') == '1'
    
    app.config['SECRET_KEY'] = os.getenv('SQLITE_SECRET')
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{sqlite_db}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    from .models import User, Upload, Comment
    with app.app_context():
        db.create_all()
    
    # Register route blueprints
    from .routes.main import main_bp
    from .routes.analyze import analyze_bp
    from .routes.upload import upload_bp
    from .routes.share import share_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(share_bp)
    
    return app