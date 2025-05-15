import flask
from flask import Blueprint, session, redirect, url_for, render_template
from app.models import Upload
from .utils import require_csrf_token, require_login

# Blueprint setup
share_bp = flask.Blueprint(
    "share",
    __name__,
    url_prefix="/share",
)

@share_bp.route('/')
@require_login
def home():
    user_id = session['user_id']

    uploads = Upload.query.filter_by(user_id=user_id).order_by(Upload.timestamp.desc()).all()

    return render_template('share.html', uploads=uploads)
