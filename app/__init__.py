from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates"
    )
    
    app_folder = os.path.dirname(os.path.abspath(__file__))
    instance_folder = os.path.abspath(os.path.join(app_folder, '..', 'instance'))
    upload_folder = os.path.join(instance_folder, 'uploads')
    sqlite_db = os.path.join(instance_folder, 'database.db')
    os.makedirs(upload_folder, exist_ok=True)
    
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', '1') == '1'
    
    app.config['SECRET_KEY'] = os.getenv('SQLITE_SECRET')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{sqlite_db}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)  # 初始化mail
    
    from .models import User, Upload, Comment, Share
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