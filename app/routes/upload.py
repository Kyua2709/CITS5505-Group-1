import threading
import uuid
from os import path

import flask
import requests

from app import db
from app.models import Upload
from .utils import require_csrf_token, require_login

# Create a Flask blueprint for upload-related routes
upload_bp = flask.Blueprint(
    "upload",
    __name__,
    url_prefix="/upload",
)

def handle_upload(source):
    user_id = flask.session.get('user_id')

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

    # Handle upload based on source type
    if source == "url":
        # Case 1: Upload source is a URL
        url = form.get("url")
        limit = form.get("comment_limit", type=int, default=1000)
        if not url:
            return flask.jsonify({"message": "URL missing"}), 400
    elif source == "file":
        # Case 2: Upload source is a file
        file = files.get("file")
        if not file:
            return flask.jsonify({"message": "File missing"}), 400
        file.save(file_path)
    else:
        # Case 3: Upload source is text input
        comments = form.get("comments")
        if not comments:
            return flask.jsonify({"message": "Comments missing"}), 400
        with open(file_path, "w") as f:
            f.write(comments)

    # Store metadata in the database
    upload = Upload(
        id=upload_id,
        title=title,
        platform=platform,
        description=description,
        user_id=user_id,
    )
    # Store metadata in the database
    db.session.add(upload)
    db.session.commit()

    # Kick off asynchronous sentiment analysis via HTTP POST request
    # NOTE: db.session cannot be safely used in threads due to lack of thread-safety
    # So, we trigger an API call to perform the processing asynchronously
    analysis_url = "http://127.0.0.1:5000/analyze/run"  # TODO: replace hardcoded hostname
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
@require_login
@require_csrf_token
def upload_by_text():
    return handle_upload("text")

# Route to handle file uploads
@upload_bp.route("/file", methods=["POST"])
@require_login
@require_csrf_token
def upload_by_file():
    return handle_upload("file")

# Route to handle uploads via external URL
@upload_bp.route("/url", methods=["POST"])
@require_login
@require_csrf_token
def upload_by_url():
    return handle_upload("url")

# Route to render the HTML form for uploads
@upload_bp.route('/', methods=['GET'])
@require_login
def home():
    user_id = flask.session.get('user_id')
    args = flask.request.args
    partial = args.get('partial')
    page = args.get('page', type=int, default=1)
    per_page = args.get('per_page', type=int, default=3)

    # Return metadata for all uploads, ordered by most recent
    order = Upload.timestamp.desc()
    uploads = db.session.query(Upload).filter_by(user_id=user_id).order_by(order)
    uploads = uploads.paginate(page=page, per_page=per_page, error_out=False)

    # Return only partial if requested
    if partial:
        return flask.render_template('partials/upload_list.html', uploads=uploads)

    # Return full page
    return flask.render_template('upload.html', uploads=uploads)
