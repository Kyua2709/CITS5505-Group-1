from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(
        __name__,
        static_folder="static",  # 指向 app/static
        template_folder="templates"  # 指向 app/templates
    )
    
    # 配置 SECRET_KEY
    app.config['SECRET_KEY'] = 'your_secret_key_here'  # 替换为一个随机的、唯一的字符串

    # 配置数据库
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/uploads.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初始化数据库
    db.init_app(app)

    # 创建数据库表
    with app.app_context():
        db.create_all()

    # 注册路由蓝图
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app  