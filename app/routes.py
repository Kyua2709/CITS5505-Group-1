from flask import Blueprint, render_template, request, jsonify
from app.models import Upload, db, predict_batch_text

# 定义蓝图
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """主页"""
    return render_template('index.html')

@main_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """上传数据页面"""
    if request.method == 'POST':
        file = request.files['file']
        if not file:
            return "No file uploaded!", 400

        file_contents = file.read().decode('utf-8')
        lines = file_contents.split('\n')
        lines = [line.strip() for line in lines if line.strip()]

        results = predict_batch_text(lines)

        return render_template('upload.html', results=results)
    return render_template('upload.html')

@main_bp.route('/save_upload', methods=['POST'])
def save_upload():
    """保存上传记录到数据库"""
    data = request.json
    upload = Upload(
        dataset_name=data.get('dataset_name'),
        platform=data.get('platform'),
        upload_type=data.get('upload_type'),
        file_path=data.get('file_path'),
        url=data.get('url'),
        comments=data.get('comments'),
        status="Processing"
    )
    db.session.add(upload)
    db.session.commit()
    return jsonify({"message": "Upload saved successfully", "id": upload.id}), 201

@main_bp.route('/get_uploads', methods=['GET'])
def get_uploads():
    """获取所有上传记录"""
    uploads = Upload.query.order_by(Upload.upload_date.desc()).all()
    return jsonify([{
        "id": upload.id,
        "dataset_name": upload.dataset_name,
        "platform": upload.platform,
        "upload_type": upload.upload_type,
        "upload_date": upload.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
        "status": upload.status
    } for upload in uploads])

@main_bp.route('/analyze')
def analyze():
    """分析页面"""
    return render_template('analyze.html')

@main_bp.route('/share')
def share():
    """分享页面"""
    return render_template('share.html')