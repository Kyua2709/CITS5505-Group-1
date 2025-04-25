# app/__init__.py
from flask import Flask

def create_app():
    app = Flask(
        __name__,
        static_folder="../static",     # 指向项目根的 static
        template_folder="templates"    # 指向 app/templates
    )

    # 注册路由蓝图
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app# create_app and extensions go here
