from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(
        __name__,
        static_folder="static",  # 指向 app/static
        template_folder="templates"  # 指向 app/templates
    )

    app_folder = os.path.dirname(os.path.abspath(__file__))
    instance_folder = os.path.abspath(os.path.join(app_folder, '..', 'instance'))
    upload_folder = os.path.join(instance_folder, 'uploads')
    sqlite_db = os.path.join(instance_folder, 'database.db')
    os.makedirs(upload_folder, exist_ok = True)

    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', '1') == '1'
    app.config['SECRET_KEY'] = os.getenv('SQLITE_SECRET')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{sqlite_db}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    from .models import User, Upload, Comment
    with app.app_context():
        db.create_all()

    # 注册路由蓝图
    from .routes import main_bp
    from .routes_new.analyze import analyze_bp
    from .routes_new.upload import upload_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(upload_bp)

    return app
