from flask import Blueprint, render_template, request, jsonify, redirect, session, url_for, flash, current_app
from app.models import Upload, User, db, predict_batch_text
from werkzeug.utils import secure_filename
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
            
            # TODO: Load uploads from the database, pass the first 3 uploads to the upload page, and implement pagination for additional uploads.
            return render_template('upload.html', results=results)
        except Exception as e:
            flash(f'Error processing file: {e}', 'danger')
            return redirect(url_for('main.upload'))

    return render_template('upload.html')

@main_bp.route('/save_upload', methods=['POST'])
def save_upload():
    try:
        data = request.form
        file = request.files.get('file')
        file_path = ''

        if file:
            filename = secure_filename(file.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            file_path = save_path

        if not data.get('dataset_name') or not data.get('platform'):
            return jsonify({"message": "Dataset name and platform are required"}), 400

        upload = Upload(
            dataset_name=data.get('dataset_name'),
            platform=data.get('platform'),
            file_path=file_path,
            url=data.get('url', 'N/A'),
            url_type=data.get('url_type', 'N/A'),
            source=data.get('source', 'N/A'),
            comments=data.get('comments', 'N/A'),
            category=data.get('category', 'N/A'),
            comment_limit=data.get('comment_limit', 'N/A'),
            status="Processing"
        )
        db.session.add(upload)
        db.session.commit()

        return jsonify({"message": "Upload saved successfully", "id": upload.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to save upload: {str(e)}"}), 500

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