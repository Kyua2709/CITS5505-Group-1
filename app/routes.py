from flask import Blueprint, render_template, request, jsonify, redirect, session, url_for, flash
from app.models import Upload, User, db, predict_batch_text
import json
import os

# 定义蓝图
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """主页"""
    return render_template('index.html')

# authentication routes
@main_bp.route('/register', methods=['POST'])
def register():
    data = request.form
    email = data.get('email')
    if User.query.filter_by(email=email).first():
        flash('Email already registered.', 'danger')
        return redirect(url_for('main.index'))

    user = User(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=email
    )
    user.set_password(data.get('password'))
    db.session.add(user)
    db.session.commit()

    flash('Registration successful. Please log in.', 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/login', methods=['POST'])
def login():
    data = request.form
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        flash('Login successful.', 'success')
        session['user_id'] = user.id
        session['user_name'] = user.first_name
        return redirect(url_for('main.index'))
    else:
        flash('Invalid email or password.', 'danger')
        return redirect(url_for('main.index'))

@main_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@main_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request.', 'danger')
            return redirect(url_for('main.upload'))

        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading.', 'danger')
            return redirect(url_for('main.upload'))

        try:
            file_contents = file.read().decode('utf-8')
            lines = file_contents.split('\n')
            lines = [line.strip() for line in lines if line.strip()]

            results = predict_batch_text(lines)
            return render_template('upload.html', results=results)
        except Exception as e:
            flash(f'Error processing file: {e}', 'danger')
            return redirect(url_for('main.upload'))

    return render_template('upload.html')

@main_bp.route('/save_upload', methods=['POST'])
def save_upload():
    try:
        # 获取 JSON 数据
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # 验证必填字段
        if not data.get('dataset_name') or not data.get('platform'):
            return jsonify({"error": "Dataset name and platform are required"}), 400

        # 创建数据库记录
        upload = Upload(
            dataset_name=data.get('dataset_name', 'Unknown Dataset'),
            platform=data.get('platform', 'Unknown Platform'),
            upload_type=data.get('upload_type', 'Unknown Type'),
            file_path=data.get('file_path', ''),
            url=data.get('url', ''),
            comments=data.get('comments', ''),
            status="Processing"
        )
        db.session.add(upload)
        db.session.commit()

        return jsonify({"message": "Upload saved successfully", "id": upload.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save upload: {str(e)}"}), 500

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

@main_bp.route('/save_manual_entry', methods=['POST'])
def save_manual_entry():
    platform = request.form.get('platform')
    source = request.form.get('source')
    category = request.form.get('category')
    comments = request.form.get('comments')

    data = {
        "platform": platform,
        "source": source,
        "category": category,
        "comments": comments.splitlines()
    }

    # 使用 Flask 的 instance_path 保存文件
    file_path = os.path.join(main_bp.root_path, 'manual_entries.json')
    try:
        with open(file_path, 'a') as f:
            f.write(json.dumps(data) + '\n')
        flash('Manual entry saved successfully!', 'success')
    except Exception as e:
        flash(f'Failed to save manual entry: {e}', 'danger')

    return redirect(url_for('main.upload'))