import threading
import uuid
from os import path
import logging

import flask
import requests
from bs4 import BeautifulSoup

from app import db
from app.models import Upload
from packages.crawler.reddit_crawler import fetch_reddit_comments
from packages.crawler.youtube_crawler import fetch_youtube_comments

# Create a Flask blueprint for upload-related routes
upload_bp = flask.Blueprint(
    "upload",
    __name__,
    url_prefix="/upload",
)

def handle_upload(source):
    user_id = flask.session.get('user_id')
    if not user_id:
        return flask.jsonify({"message": "Please log in to save uploads"}), 401

    # Extract basic metadata from the form
    form = flask.request.form
    files = flask.request.files
    title = form.get("title")
    platform = form.get("platform")
    description = form.get("description")

    # Validate required fields
    if not title or not platform:
        return flask.jsonify({"message": "Title and Platform are required"}), 400

    # Generate a unique ID for the upload and construct the local file path
    upload_id = str(uuid.uuid4())
    upload_folder = flask.current_app.config["UPLOAD_FOLDER"]
    secret = flask.current_app.config["SECRET_KEY"]
    file_path = path.join(upload_folder, upload_id)

    # Initialize optional fields
    url, limit = None, None
    comment_count = 0

    # Handle upload based on source type
    if source == "url":
        # Case 1: Upload source is a URL
        url = form.get("url")
        limit = form.get("comment_limit", type=int, default=1000)  # 默认限制改为1000
        if not url:
            return flask.jsonify({"message": "URL missing"}), 400
            
        # 爬取URL中的评论数量
        try:
            if platform.lower() == 'reddit':
                # 使用专门的Reddit爬虫
                flask.current_app.logger.info(f"Fetching Reddit comments from: {url}")
                comments = fetch_reddit_comments(url, limit)
                comment_count = len(comments)
                flask.current_app.logger.info(f"Found {comment_count} Reddit comments")
                
                # 保存评论内容到文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    for comment in comments:
                        f.write(comment + '\n')
                
            elif platform.lower() == 'youtube':
                # 使用专门的YouTube爬虫
                flask.current_app.logger.info(f"Fetching YouTube comments from: {url}")
                comments = fetch_youtube_comments(url, limit)
                comment_count = len(comments)
                flask.current_app.logger.info(f"Found {comment_count} YouTube comments")
                
                # 保存评论内容到文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    for comment in comments:
                        f.write(comment + '\n')
                
            else:
                # 其他平台的爬取逻辑保持不变
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'max-age=0'
                }
                
                flask.current_app.logger.info(f"Fetching URL: {url}")
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                flask.current_app.logger.info(f"Response status: {response.status_code}")
                
                # 使用BeautifulSoup解析页面
                soup = BeautifulSoup(response.text, 'html.parser')
                flask.current_app.logger.info(f"Platform: {platform}")
                
                if platform.lower() == 'twitter':
                    # Twitter评论通常在article[data-testid="tweet"]中
                    comments = soup.find_all('article', {'data-testid': 'tweet'})
                    total_comments = len(comments)
                    comment_count = min(total_comments, limit)
                    flask.current_app.logger.info(f"Found {total_comments} Twitter comments, limited to {comment_count}")
                    
                else:
                    # 通用评论查找（查找常见的评论容器）
                    comment_selectors = [
                        'div.comment', 'div.comments', 'div.review',
                        'article.comment', 'li.comment', 'div.review-item',
                        'div[class*="comment"]', 'div[class*="review"]'
                    ]
                    all_comments = []
                    for selector in comment_selectors:
                        comments = soup.select(selector)
                        if comments:
                            all_comments.extend(comments)
                            flask.current_app.logger.info(f"Found {len(comments)} comments using selector: {selector}")
                    
                    # 去重并计算总评论数
                    unique_comments = set(str(comment) for comment in all_comments)
                    total_comments = len(unique_comments)
                    comment_count = min(total_comments, limit)
                    flask.current_app.logger.info(f"Found {total_comments} total comments, limited to {comment_count}")
            
        except requests.RequestException as e:
            flask.current_app.logger.error(f"Request error: {str(e)}")
            return flask.jsonify({"message": f"Error fetching URL: {str(e)}"}), 400
        except Exception as e:
            flask.current_app.logger.error(f"General error: {str(e)}")
            return flask.jsonify({"message": f"Error processing URL: {str(e)}"}), 400
    elif source == "file":
        # Case 2: Upload source is a file
        file = files.get("file")
        if not file:
            return flask.jsonify({"message": "File missing"}), 400
        
        # 保存文件
        file.save(file_path)
        
        # 读取文件内容并计算评论数量
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                comment_count = len([line for line in content.splitlines() if line.strip()])
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                    comment_count = len([line for line in content.splitlines() if line.strip()])
            except Exception as e:
                return flask.jsonify({"message": f"Error reading file: {str(e)}"}), 400
        except Exception as e:
            return flask.jsonify({"message": f"Error reading file: {str(e)}"}), 400
    else:
        # Case 3: Upload source is text input
        comments = form.get("comments")
        if not comments:
            return flask.jsonify({"message": "Comments missing"}), 400
        
        # 保存原始文本
        with open(file_path, "w") as f:
            f.write(comments)
        
        # 计算评论数量（按行数）
        comment_count = len([line for line in comments.splitlines() if line.strip()])

    # 创建上传记录
    upload = Upload(
        id=upload_id,
        title=title,
        platform=platform,
        description=description,
        user_id=user_id,
        size=comment_count  # 使用 size 字段存储评论数量
    )

    # Store metadata in the database
    db.session.add(upload)
    db.session.commit()

    # Kick off asynchronous sentiment analysis via HTTP POST request
    # NOTE: db.session cannot be safely used in threads due to lack of thread-safety
    # So, we trigger an API call to perform the processing asynchronously
    analysis_url = "http://localhost:5000/analyze/run"
    thread = threading.Thread(
        target=requests.post,
        args=(
            analysis_url,
            {
                "secret": secret,
                "upload_id": upload_id,
                "file_path": file_path,
                "platform": platform,
                "url": url,
                "limit": limit,
            },
        ),
    )
    thread.daemon = True  # Ensure thread exits with main process
    thread.start()

    return flask.jsonify({"message": "Upload saved successfully", "id": upload_id}), 201

# Route to handle text uploads
@upload_bp.route("/text", methods=["POST"])
def upload_by_text():
    return handle_upload("text")

# Route to handle file uploads
@upload_bp.route("/file", methods=["POST"])
def upload_by_file():
    return handle_upload("file")

# Route to handle uploads via external URL
@upload_bp.route("/url", methods=["POST"])
def upload_by_url():
    return handle_upload("url")

# Route to render the HTML form for uploads
@upload_bp.route('/', methods=['GET'])
def home():
    if 'user_id' not in flask.session:
        flask.flash('Please log in to access this page.', 'danger')
        return flask.redirect(flask.url_for('main.index'))

    args = flask.request.args
    partial = args.get('partial')
    page = args.get('page', type=int, default=1)
    per_page = args.get('per_page', type=int, default=3)

    # Return metadata for all uploads, ordered by most recent
    order = Upload.timestamp.desc()
    uploads = db.session.query(Upload).options(
        db.joinedload(Upload.comments)
    ).order_by(order)
    uploads = uploads.paginate(page=page, per_page=per_page, error_out=False)

    # Return only partial if requested
    if partial:
        return flask.render_template('partials/upload_list.html', uploads=uploads)

    # Return full page
    return flask.render_template('upload.html', uploads=uploads)
