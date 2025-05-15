import functools
import flask
import flask_wtf.csrf

def require_csrf_token(func):
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        request = flask.request
        token = request.form.get('csrf_token') or request.args.get('csrf_token')
        try:
            flask_wtf.csrf.validate_csrf(token)
        except:
            flask.abort(400)
        return func(*args, **kwargs)
    return decorated_view

def require_login(func):
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        if 'user_id' not in flask.session:
            home = flask.url_for('main.home')
            return flask.redirect(home)
        return func(*args, **kwargs)
    return decorated_view
