from app import db
from datetime import datetime
from bert_model import predict_sentiment
from preprocessing import clean_text
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
        return f'<User {self.email}>'

# 数据库模型
class Upload(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_name = db.Column(db.String(255), nullable=False, default='Manual Entry')
    platform = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(255), nullable=True)
    url = db.Column(db.String(255), nullable=True)
    url_type = db.Column(db.String(50), nullable=True, default='N/A')
    comment_limit = db.Column(db.String(50), nullable=True)
    source = db.Column(db.String(50), nullable=True, default='N/A')
    comments = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True, default='N/A')
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Pending")
    num_comments = db.Column(db.Integer, nullable=True)
    
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('uploads', lazy=True))

    def __repr__(self):
        return f'<Upload {self.dataset_name} - {self.platform}>'

    def to_dict(self):
        return {
            'id': self.id,
            'dataset_name': self.dataset_name,
            'platform': self.platform,
            'file_path': self.file_path,
            'url': self.url,
            'url_type': self.url_type,
            'comment_limit': self.comment_limit,
            'source': self.source,
            'category': self.category,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'status': self.status,
            'user_id': self.user_id,
            'num_comments': self.num_comments,
            'comments': self.comments
        }

# 文本预测功能
def predict_single_text(text):
    cleaned = clean_text(text)
    prediction = predict_sentiment(cleaned)
    return prediction

def predict_batch_text(text_list):
    results = []
    for text in text_list:
        cleaned = clean_text(text)
        pred = predict_sentiment(cleaned)
        results.append((text, pred))
    return results