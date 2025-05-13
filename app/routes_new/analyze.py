import importlib
import time

import flask
from packages import sentiment_analysis

from app import db
from app.models import Comment, Upload

# Create a Flask blueprint for analysis-related routes
analyze_bp = flask.Blueprint(
    "analyze",
    __name__,
    url_prefix="/analyze",
)

# Use a web crawler to save content from the URL into file_path
def craw_comments(file_path: str, platform: str, url: str, url_type: str, limit: int):
    print(url, limit)

    PLATFORM_CRAWLER_MAP = {
        'reddit': 'reddit_crawler.fetch_reddit_comments',
        'twitter': 'twitter_crawler.fetch_twitter_comments',
        'instagram': 'instagram_crawler.fetch_instagram_comments',
        'facebook': 'facebook_crawler.fetch_facebook_comments',
        'tiktok': 'tiktok_crawler.fetch_tiktok_comments',
        'youtube': 'youtube_crawler.fetch_youtube_comments',
    }

    if platform not in PLATFORM_CRAWLER_MAP:
        raise RuntimeError(f"Platform {platform} is not supported")

    func_path = PLATFORM_CRAWLER_MAP[platform]
    module_name, func_name = func_path.rsplit('.', 1)
    module = importlib.import_module(f'crawlers.{module_name}')
    func = getattr(module, func_name)

    comments = func(url, limit)
    with open(file_path, "w", encoding="utf-8") as f:
        for c in comments:
            f.write(c.replace('\n', ' ') + '\n')

@analyze_bp.route("/run", methods=["POST"])
def run_analyze_job():
    # TODO: Secure this internal interface with secret token, so user cannot access it directly

    # Simulate a time-consuming task (e.g., crawling, analyzing) with a sleep
    time.sleep(10)

    session = db.session
    form = flask.request.form

    # Extract job metadata from the request
    upload_id = form.get("upload_id")
    file_path = form.get("file_path")
    platform = form.get('platform')
    url = form.get("url")
    url_type = form.get("url_type")
    limit = form.get("limit", type=int)

    try:
        # If the source was a URL, retrieve content and save to file_path
        if url:
            craw_comments(file_path, platform, url, url_type, limit)

        # Load the file and perform sentiment analysis line-by-line
        with open(file_path) as file:
            comments = file.readlines()

        count = 0  # Counter for valid comments
        for comment in comments:
            content = comment.strip()
            if not content:
                continue  # Skip empty lines
            count += 1
            score = sentiment_analysis.tabularisai(content)  # Predict sentiment score
            comment = Comment(content=content, score=score, upload_id=upload_id)
            session.add(comment)

        # Mark the upload job as completed
        upload = session.query(Upload).get(upload_id)
        upload.size = count
        upload.status = "Completed"
        session.commit()
    except Exception as e:
        # Roll back on error and update status to 'Error'
        session.rollback()
        upload = session.query(Upload).get(upload_id)
        upload.status = f"Error: {e}"
        session.commit()

    # Internal endpoint; response content is not used
    return flask.jsonify()

def upload_to_dict(upload: Upload, comments=False) -> dict:
    """
    Converts an Upload SQLAlchemy object into a serializable dictionary.
    Optionally includes associated comments.
    """
    result = {
        "id": upload.id,
        "timestamp": upload.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "title": upload.title,
        "description": upload.description,
        "platform": upload.platform,
        "size": upload.size,
        "status": upload.status,
        "user_id": upload.user_id,
    }

    # Include comments in the result if requested
    if comments:
        result["comments"] = [
            {
                "id": comment.id,
                "content": comment.content,
                "score": comment.score,
            }
            for comment in upload.comments
        ]

    return result

@analyze_bp.route("/result/<upload_id>", methods=["GET"])
def result(upload_id):
    # TODO: Render data and add security check
    # Return full upload data, including analyzed comments
    upload = db.session.query(Upload).get(upload_id)
    return flask.jsonify(upload_to_dict(upload, True))

@analyze_bp.route("/")
def home():    
    if 'user_id' not in flask.session:
        flask.flash('Please log in to access this page.', 'danger')
        return flask.redirect(flask.url_for('main.index'))

    # Render the HTML page for viewing analysis results
    return flask.render_template("analyze.html")
