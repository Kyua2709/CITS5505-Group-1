
import flask

from app import db

# Create a Flask blueprint for analysis-related routes
share_bp = flask.Blueprint(
    "share",
    __name__,
    url_prefix="/share",
)

@share_bp.route('/')
def home():
    if 'user_id' not in flask.session:
        return flask.redirect(flask.url_for('main.index'))
    return flask.render_template('share.html')
