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
    id = db.Column(db.Integer, primary_key=True)
    dataset_name = db.Column(db.String(255), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    upload_type = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(255), nullable=True)
    url = db.Column(db.String(255), nullable=True)
    comments = db.Column(db.Text, nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Processing")

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