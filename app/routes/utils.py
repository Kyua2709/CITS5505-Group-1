from functools import wraps
from flask import request, abort
from flask_wtf.csrf import validate_csrf, CSRFError

def require_csrf_token(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        token = request.form.get('csrf_token') or request.args.get('csrf_token')
        try:
            validate_csrf(token)
        except:
            abort(400)
        return func(*args, **kwargs)
    return decorated_view
