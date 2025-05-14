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
        upload.status = "Error"
        session.commit()

    # Internal endpoint; response content is not used
    return flask.jsonify()

@analyze_bp.route("/export/<upload_id>", methods=["GET"])
def export(upload_id):
    upload_folder = flask.current_app.config["UPLOAD_FOLDER"]
    return flask.send_from_directory(upload_folder, upload_id )

def percentage(x, y):
    r = x / max(y, 1)
    return round(100 * r)

@analyze_bp.route("/result/<upload_id>", methods=["GET"])
def result(upload_id):
    if 'user_id' not in flask.session:
        return flask.redirect(flask.url_for('main.index'))

    # TODO: Add extra security check, the page should only be visible to owner and shared people
    pass

    # TODO: For now, the analysis is performed at the frontend due to its complexity
    # In the future, some of the calculation can be moved to the backend
    # So we do not need to send all comments to frontend
    upload = db.session.query(Upload).get(upload_id)
    comments = db.session.query(Comment).filter(Comment.upload_id == upload.id).order_by(Comment.id)

    if flask.request.args.get("partial"):
        search = flask.request.args.get('search')
        if search:
            for keyword in search.split():
                comments = comments.filter(Comment.content.ilike(f"%{keyword}%"))
        page = flask.request.args.get("page", type=int, default=1)
        per_page = 5
        comments = comments.paginate(page=page, per_page=per_page, error_out=False)
        return flask.render_template(
            "partials/comment_list.html",
            comments=comments,
        )

    comments = list(comments)
    comments_positive = list(filter(lambda comment: comment.rating > 0, comments))
    comments_negative = list(filter(lambda comment: comment.rating < 0, comments))

    count_all = len(comments)
    count_positive = len(comments_positive)
    count_negative = len(comments_negative)
    count_neutral = count_all - count_positive - count_negative

    percentage_positive = percentage(count_positive, count_all)
    percentage_neutral = percentage(count_neutral, count_all)
    percentage_negative = percentage(count_negative, count_all)

    # Convert to dict outside html because Jinja2 does not support for ... in syntax
    comments_positive = [comment.to_dict() for comment in comments_positive]
    comments_negative = [comment.to_dict() for comment in comments_negative]

    return flask.render_template(
        "partials/analyze_result.html",
        upload=upload,
        percentage_positive=percentage_positive,
        percentage_neutral=percentage_neutral,
        percentage_negative=percentage_negative,
        comments_positive=comments_positive,
        comments_negative=comments_negative,
    )

@analyze_bp.route("/")
def home():
    if 'user_id' not in flask.session:
        return flask.redirect(flask.url_for('main.index'))

    user_id = flask.session.get('user_id')
    order = Upload.timestamp.desc()
    uploads = db.session.query(Upload).filter_by(user_id=user_id).order_by(order)

    # Current selected upload id
    upload_id = flask.request.args.get('upload_id')
    selected_upload = db.session.query(Upload).get(upload_id)

    # Render the HTML page for viewing analysis results
    return flask.render_template("analyze.html", uploads=uploads, selected_upload=selected_upload)
