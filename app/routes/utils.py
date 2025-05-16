import functools
import flask
import flask_wtf.csrf
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app

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

def send_share_notification(recipient_email, analysis_title, message=None):
    """
    Sends an email to notify a registered user that an analysis has been shared with them.
    """

    sender_email = current_app.config.get("MAIL_SENDER", "noreply@sentisocial.com")
    smtp_server = current_app.config.get("MAIL_SERVER", "smtp.gmail.com")
    smtp_port = current_app.config.get("MAIL_PORT", 587)
    smtp_user = current_app.config.get("MAIL_USERNAME")
    smtp_password = current_app.config.get("MAIL_PASSWORD")

    if not smtp_user or not smtp_password:
        raise Exception("Email credentials not configured.")

    subject = f"New Analysis Shared: {analysis_title}"

    body = f"""
    Hi there,

    Someone has shared an analysis titled "{analysis_title}" with you on SentiSocial.

    {"Message: " + message if message else ""}

    You can view it by logging in to your dashboard:
    https://your-sentisocial-app.com/analyze/

    Regards,
    The SentiSocial Team
    """

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

    except Exception as e:
        raise Exception(f"Failed to send email to {recipient_email}: {e}")
