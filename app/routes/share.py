# share.py - updated to support internal user sharing with optional email

import flask
from flask import request, jsonify
from app import db
from app.models import Upload, Share, User
from .utils import require_csrf_token, require_login, send_share_notification
from datetime import datetime

share_bp = flask.Blueprint("share", __name__, url_prefix="/share")


@share_bp.route("/", methods=["GET"])
@require_login
def home():
    user_id = flask.session.get("user_id")

    #Fetch all uploads by the user
    uploads = (
        db.session.query(Upload)
        .filter_by(user_id=user_id)
        .order_by(Upload.timestamp.desc())
        .all()
    )

    #Fetch all shares sent by the user
    recent_shares = (
        db.session.query(Share)
        .filter_by(sender_id=user_id)
        .order_by(Share.timestamp.desc())
        .all()
    )

    #Fetch all shares received by the user
    shared_with_me = (
        db.session.query(Share)
        .filter_by(recipient_id=user_id)
        .order_by(Share.timestamp.desc())
        .all()
    )

    return flask.render_template(
        "share.html",
        uploads=uploads,
        recent_shares=recent_shares,
        shared_with_me=shared_with_me,
    )


@share_bp.route("/internal", methods=["POST"])
@require_login
@require_csrf_token
def share_internal():
    # This route allows a user to share an upload with another registered user
    user_id = flask.session.get("user_id")
    form = request.form

    upload_id = form.get("upload_id")
    emails = form.get("emails")
    message = form.get("message")

    if not upload_id or not emails:
        return jsonify(success=False, message="Missing upload ID or emails"), 400

    upload = db.session.query(Upload).get(upload_id)
    if not upload or upload.user_id != user_id:
        return jsonify(success=False, message="You do not own this upload."), 403

    email_list = [e.strip() for e in emails.split(",") if e.strip()]
    success_list, fail_list = [], []

    for email in email_list:
        user = db.session.query(User).filter_by(email=email).first()
        if not user:
            fail_list.append(email)
            continue
        # Check if the user is already shared with
        existing = db.session.query(Share).filter_by(
            upload_id=upload_id,
            recipient_id=user.id
        ).first()
        # If the share already exists, skip sending
        if not existing:
            share = Share(
                upload_id=upload_id,
                sender_id=user_id,
                recipient_id=user.id,
                recipient_email=email,
                message=message,
                timestamp=datetime.utcnow()
            )
            db.session.add(share)
            try:
                send_share_notification(user.email, upload.title, message)
                success_list.append(email)
            except Exception as e:
                print(f"Email send failed to {email}: {e}")

    db.session.commit()

    return jsonify(success=True, shared=success_list, failed=fail_list)
