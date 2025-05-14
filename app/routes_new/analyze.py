import importlib
import time

import flask
from packages import crawler
from packages import sentiment_analysis

from app import db
from app.models import Comment, Upload

# Create a Flask blueprint for analysis-related routes
analyze_bp = flask.Blueprint(
    "analyze",
    __name__,
    url_prefix="/analyze",
)

@analyze_bp.route("/run", methods=["POST"])
def run_analyze_job():
    session = db.session
    form = flask.request.form

    # This is an internal interface - only legitimate requests with the correct secret should access it
    # Abort with a fake 404 if the secret does not match
    secret = form.get("secret")
    expected = flask.current_app.config["SECRET_KEY"]
    if not secret or secret != expected:
        flask.abort(404)

    # Extract job metadata from the request
    upload_id = form.get("upload_id")
    file_path = form.get("file_path")
    platform = form.get("platform")
    url = form.get("url")
    limit = form.get("limit", type=int)

    try:
        # If the source was a URL, retrieve content and save to file_path
        if url:
            comments = crawler.fetch_comments(platform, url, limit)
            comments_by_line = map(lambda c: c.replace("\n", " "), comments)
            output = "\n".join(comments_by_line)
            with open(file_path, "w") as f:
                f.write(output)

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
        return flask.redirect(flask.url_for('main.index'))

    order = Upload.timestamp.desc()
    uploads = db.session.query(Upload).order_by(order)

    # Render the HTML page for viewing analysis results
    return flask.render_template("analyze.html", uploads=uploads)
