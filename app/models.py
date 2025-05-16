from app import db
from datetime import datetime, timezone
import uuid
from werkzeug.security import generate_password_hash, check_password_hash


# User Model
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


# Database Model
class Upload(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    size = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), nullable=False, default="Processing")

    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("uploads", lazy=True))
    comments = db.relationship("Comment", backref="upload", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None,
            "title": self.title,
            "description": self.description,
            "platform": self.platform,
            "size": self.size,
            "status": self.status,
            "user_id": self.user_id,
        }


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    upload_id = db.Column(db.String(36), db.ForeignKey("upload.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    @property
    def rating(self):
        SCORE_NEGATIVE = 38
        SCORE_POSITIVE = 54
        return -1 if self.score < SCORE_NEGATIVE else 1 if self.score > SCORE_POSITIVE else 0

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "score": self.score,
            "rating": self.rating,
            "created_at": self.created_at.strftime("%b %d, %Y %I:%M %p") if self.created_at else "N/A",
        }


class Share(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.String(36), db.ForeignKey("upload.id"), nullable=False)
    sender_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False)
    recipient_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=True)
    recipient_email = db.Column(db.String(120), nullable=True)
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship("User", foreign_keys=[sender_id])
    recipient = db.relationship("User", foreign_keys=[recipient_id])
    upload = db.relationship("Upload")

    def __repr__(self):
        return (
            f"Share(From: {self.sender_id}, To: {self.recipient_id or self.recipient_email}, Upload: {self.upload_id})"
        )
