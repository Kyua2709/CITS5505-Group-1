from flask import Blueprint, render_template, request, jsonify, redirect, session, url_for, flash, current_app
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
        return jsonify({'status': 'error', 'message': 'Email already registered'}), 400

    user = User(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=email
    )
    user.set_password(data.get('password'))
    db.session.add(user)
    db.session.commit()

    # Auto login
    session['user_id'] = user.id
    session['user_name'] = user.first_name

    return jsonify({'status': 'success', 'message': f'Welcome, {user.first_name}!'})


@main_bp.route('/login', methods=['POST'])
def login():
    data = request.form
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['user_name'] = user.first_name
        return jsonify({'status': 'success', 'message': 'Login successful'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401

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

    # 验证必填字段
    if not platform or not comments:
        flash('Platform and comments are required.', 'danger')
        return redirect(url_for('main.upload'))

    # 准备数据
    data = {
        "platform": platform,
        "source": source,
        "category": category,
        "comments": comments.splitlines()
    }

    # 保存到 instance/manual_entries.json
    file_path = os.path.join(current_app.instance_path, 'manual_entries.json')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # 确保目录存在
    try:
        with open(file_path, 'a') as f:
            f.write(json.dumps(data) + '\n')
        flash('Manual entry saved successfully!', 'success')
    except Exception as e:
        flash(f'Failed to save manual entry: {e}', 'danger')

    return redirect(url_for('main.upload'))


@main_bp.route('/save_file_upload', methods=['POST'])
def save_file_upload():
    platform = request.form.get('platform')
    dataset_name = request.form.get('dataset_name')
    date_range_start = request.form.get('start_date')
    date_range_end = request.form.get('end_date')
    file = request.files.get('file')

    if not platform or not dataset_name or not file:
        flash('Platform, dataset name, and file are required.', 'danger')
        return redirect(url_for('main.upload'))

    # 保存文件信息
    data = {
        "platform": platform,
        "dataset_name": dataset_name,
        "date_range_start": date_range_start,
        "date_range_end": date_range_end,
        "file_name": file.filename
    }

    # 保存到文件
    file_path = os.path.join(current_app.instance_path, 'file_uploads.json')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        with open(file_path, 'a') as f:
            f.write(json.dumps(data) + '\n')
        flash('File upload saved successfully!', 'success')
    except Exception as e:
        flash(f'Failed to save file upload: {e}', 'danger')

    return redirect(url_for('main.upload'))

@main_bp.route('/save_platform_url', methods=['POST'])
def save_platform_url():
    platform = request.form.get('platform')
    url_type = request.form.get('url_type')
    url = request.form.get('url')
    comment_limit = request.form.get('comment_limit')

    if not platform or not url or not url_type:
        flash('Platform, URL type, and URL are required.', 'danger')
        return redirect(url_for('main.upload'))

    # 保存 URL 信息
    data = {
        "platform": platform,
        "url_type": url_type,
        "url": url,
        "comment_limit": comment_limit
    }

    # 保存到文件
    file_path = os.path.join(current_app.instance_path, 'platform_urls.json')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        with open(file_path, 'a') as f:
            f.write(json.dumps(data) + '\n')
        flash('Platform URL saved successfully!', 'success')
    except Exception as e:
        flash(f'Failed to save platform URL: {e}', 'danger')

    return redirect(url_for('main.upload'))


@main_bp.route('/upload', methods=['GET', 'POST'])
def upload_with_recent_uploads():
    # 定义文件路径
    manual_entries_path = os.path.join(current_app.instance_path, 'manual_entries.json')
    file_uploads_path = os.path.join(current_app.instance_path, 'file_uploads.json')
    platform_urls_path = os.path.join(current_app.instance_path, 'platform_urls.json')

    # 初始化数据列表
    recent_uploads = []

    # 读取 manual_entries.json
    if os.path.exists(manual_entries_path):
        with open(manual_entries_path, 'r') as f:
            for line in f:
                entry = json.loads(line.strip())
                recent_uploads.append({
                    "platform": entry.get("platform", "Unknown"),
                    "date_uploaded": datetime.now().strftime('%b %d, %Y'),  # 当前日期
                    "size": f"{len(entry.get('comments', []))} comments",
                    "status": "Completed"
                })

    # 读取 file_uploads.json
    if os.path.exists(file_uploads_path):
        with open(file_uploads_path, 'r') as f:
            for line in f:
                entry = json.loads(line.strip())
                recent_uploads.append({
                    "platform": entry.get("platform", "Unknown"),
                    "date_uploaded": datetime.now().strftime('%b %d, %Y'),  # 当前日期
                    "size": entry.get("file_name", "Unknown"),
                    "status": "Completed"
                })

    # 读取 platform_urls.json
    if os.path.exists(platform_urls_path):
        with open(platform_urls_path, 'r') as f:
            for line in f:
                entry = json.loads(line.strip())
                recent_uploads.append({
                    "platform": entry.get("platform", "Unknown"),
                    "date_uploaded": datetime.now().strftime('%b %d, %Y'),  # 当前日期
                    "size": f"Limit: {entry.get('comment_limit', 'Unknown')}",
                    "status": "Completed"
                })

    # 将 recent_uploads 数据传递到模板
    return render_template('upload.html', recent_uploads=recent_uploads)