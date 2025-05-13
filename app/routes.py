from flask import Blueprint, render_template, request, jsonify, redirect, session, url_for, flash, current_app
from app.models import Upload, User, db, predict_batch_text
from werkzeug.utils import secure_filename
import json
import os
import chardet

# Define Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page"""
    if 'first_name' in session:
        return render_template('login.html')
    return render_template('index.html')

@main_bp.route('/login')
def logged_in_home():
    """Logged in home page"""
    if 'first_name' not in session:
        return redirect(url_for('main.index'))
    return render_template('login.html')

# Authentication routes
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
    session['first_name'] = user.first_name

    return jsonify({'status': 'success', 'message': f'Welcome, {user.first_name}!'})

@main_bp.route('/login', methods=['POST'])
def login():
    data = request.form
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['first_name'] = user.first_name
        return jsonify({'status': 'success', 'message': 'Login successful'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401

@main_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard page"""
    if 'first_name' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('main.index'))
    return render_template('login.html')

@main_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """Render upload page and handle file POST if needed."""
    if 'first_name' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('main.index'))

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
            lines = [line.strip() for line in file_contents.split('\n') if line.strip()]
            results = predict_batch_text(lines)

            flash('File uploaded and processed successfully.', 'success')
            return redirect(url_for('main.upload'))

        except Exception as e:
            flash(f'Error processing file: {e}', 'danger')
            return redirect(url_for('main.upload'))

    # For GET requests: just render the template, JS will load data via AJAX
    return render_template('upload.html')

@main_bp.route('/save_upload', methods=['POST'])
def save_upload():
    """Save upload details"""
    if 'first_name' not in session:
        return jsonify({"message": "Please log in to save uploads"}), 401

    try:
        data = request.form
        file = request.files.get('file')
        file_path = ''
        num_comments = None

        # 平台爬虫自动分发
        PLATFORM_CRAWLER_MAP = {
            'reddit': 'reddit_crawler.fetch_reddit_comments',
            'twitter': 'twitter_crawler.fetch_twitter_comments',
            'instagram': 'instagram_crawler.fetch_instagram_comments',
            'facebook': 'facebook_crawler.fetch_facebook_comments',
            'tiktok': 'tiktok_crawler.fetch_tiktok_comments',
            'youtube': 'youtube_crawler.fetch_youtube_comments',
        }
        platform = data.get('platform', '').lower()
        if platform in PLATFORM_CRAWLER_MAP and data.get('url'):
            import importlib
            func_path = PLATFORM_CRAWLER_MAP[platform]
            module_name, func_name = func_path.rsplit('.', 1)
            module = importlib.import_module(f'crawlers.{module_name}')
            func = getattr(module, func_name)
            try:
                comment_limit = int(data.get('comment_limit', 100))
            except Exception:
                comment_limit = 100
            comments = func(data.get('url'), comment_limit)
            num_comments = len(comments)
            import datetime
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{platform}_comments_{ts}.txt"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            with open(save_path, "w", encoding="utf-8") as f:
                for c in comments:
                    f.write(c.replace('\n', ' ') + '\n')
            file_path = save_path
        elif file:
            filename = secure_filename(file.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            file_path = save_path
            # 统计评论数
            ext = filename.split('.')[-1].lower()
            file.seek(0)
            file_bytes = file.read()
            detected = chardet.detect(file_bytes)
            encoding = detected['encoding'] or 'utf-8'
            try:
                content = file_bytes.decode(encoding)
            except Exception:
                content = file_bytes.decode('utf-8', errors='replace')
            if ext in ['txt', 'csv']:
                num_comments = len([line for line in content.splitlines() if line.strip()])
            elif ext == 'json':
                import json
                try:
                    data_json = json.loads(content)
                    if isinstance(data_json, list):
                        num_comments = len(data_json)
                    elif isinstance(data_json, dict) and 'comments' in data_json:
                        num_comments = len(data_json['comments'])
                except Exception:
                    num_comments = None
            else:
                num_comments = None

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
            status="Processing",
            num_comments=num_comments,
            user_id=session.get('user_id')
        )
        db.session.add(upload)
        db.session.commit()

        return jsonify({"message": "Upload saved successfully", "id": upload.id}), 201
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"message": f"Failed to save upload: {str(e)}"}), 500

@main_bp.route('/get_uploads', methods=['GET'])
def get_uploads():
    """Get all upload records"""
    if 'first_name' not in session:
        return jsonify({"message": "Please log in to view uploads"}), 401
    
    page = request.args.get('page', 1, type=int)
    per_page = 3

    user_id = session.get('user_id')
    uploads = Upload.query\
                    .filter_by(user_id=user_id)\
                    .order_by(Upload.upload_date.desc())\
                    .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
    "items": [{
        "id": upload.id,
        "dataset_name": upload.dataset_name,
        "platform": upload.platform,
        "upload_date": upload.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
        "status": upload.status,
        "num_comments": getattr(upload, 'num_comments', None),
        "file_path": upload.file_path,
        "comments": upload.comments,
        "url": upload.url
    } for upload in uploads.items],
    "page": uploads.page,
    "pages": uploads.pages,
    "total": uploads.total
})

@main_bp.route('/analyze')
def analyze():
    """Analysis page"""
    if 'first_name' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('main.index'))
    return render_template('analyze.html')

@main_bp.route('/share')
def share():
    """Share page"""
    if 'first_name' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('main.index'))
    return render_template('share.html')