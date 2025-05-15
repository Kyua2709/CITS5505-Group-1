import flask
from packages import crawler
from packages import sentiment_analysis
from sqlalchemy import func
from datetime import datetime
from collections import defaultdict

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

    secret = form.get("secret")
    expected = flask.current_app.config["SECRET_KEY"]
    if not secret or secret != expected:
        flask.abort(404)

    upload_id = form.get("upload_id")
    file_path = form.get("file_path")
    platform = form.get("platform")
    url = form.get("url")
    limit = form.get("limit", type=int)

    try:
        if url:
            comments = crawler.fetch_comments(platform, url, limit)
            comments_by_line = map(lambda c: c.replace("\n", " "), comments)
            output = "\n".join(comments_by_line)
            with open(file_path, "w") as f:
                f.write(output)

        with open(file_path) as file:
            comments = file.readlines()

        count = 0
        for comment in comments:
            content = comment.strip()
            if not content:
                continue
            count += 1
            score = sentiment_analysis.tabularisai(content)
            comment = Comment(content=content, score=score, upload_id=upload_id)
            session.add(comment)

        upload = session.query(Upload).get(upload_id)
        upload.size = count
        upload.status = "Completed"
        session.commit()

    except Exception as e:
        import traceback
        session.rollback()
        traceback.print_exc()
        upload = session.query(Upload).get(upload_id)
        upload.status = "Error"
        session.commit()

    return flask.jsonify()

@analyze_bp.route("/export/<upload_id>", methods=["GET"])
def export(upload_id):
    upload_folder = flask.current_app.config["UPLOAD_FOLDER"]
    return flask.send_from_directory(upload_folder, upload_id)

def percentage(x, y):
    r = x / max(y, 1)
    return round(100 * r)

@analyze_bp.route("/result/<upload_id>", methods=["GET"])
def result(upload_id):
    if 'user_id' not in flask.session:
        return flask.redirect(flask.url_for('main.index'))
        
    user_id = flask.session.get('user_id')
    upload = db.session.query(Upload).get(upload_id)
    
    if upload.user_id != user_id and not is_shared_with_user(upload_id, user_id):
        flask.abort(403)
        
    comments_query = db.session.query(Comment).filter(Comment.upload_id == upload.id).order_by(Comment.id)

    if flask.request.args.get("partial"):
        search = flask.request.args.get('search')
        if search:
            for keyword in search.split():
                comments_query = comments_query.filter(Comment.content.ilike(f"%{keyword}%"))
        page = flask.request.args.get("page", type=int, default=1)
        per_page = flask.request.args.get("per_page", type=int, default=5)
        if per_page < 0: per_page = comments_query.count()
        comments = comments_query.paginate(page=page, per_page=per_page, error_out=False)
        return flask.render_template("partials/comment_list.html", comments=comments)

    comments = list(comments_query)
    comments_positive = list(filter(lambda c: c.rating > 0, comments))
    comments_negative = list(filter(lambda c: c.rating < 0, comments))

    count_all = len(comments)
    count_positive = len(comments_positive)
    count_negative = len(comments_negative)
    count_neutral = count_all - count_positive - count_negative

    percentage_positive = percentage(count_positive, count_all)
    percentage_neutral = percentage(count_neutral, count_all)
    percentage_negative = percentage(count_negative, count_all)

    comments_positive = [c.to_dict() for c in comments_positive]
    comments_negative = [c.to_dict() for c in comments_negative]

    # Sentiment distribution
    distribution_data = {
        "positive": count_positive,
        "neutral": count_neutral,
        "negative": count_negative,
    }

    # Emotion Intensity Histogram
    def get_bucket(score):
        return (score // 10) * 10

    histogram_data = defaultdict(lambda: {"Positive": 0, "Neutral": 0, "Negative": 0})

    for c in comments:
        bucket = f"{get_bucket(c.score)}-{get_bucket(c.score) + 9}"
        sentiment = "Positive" if c.rating > 0 else "Negative" if c.rating < 0 else "Neutral"
        histogram_data[bucket][sentiment] += 1

    all_buckets = [f"{i}-{i + 9}" for i in range(0, 100, 10)]
    emotion_histogram_data = {
        "labels": all_buckets,
        "positive": [histogram_data[b]["Positive"] for b in all_buckets],
        "neutral": [histogram_data[b]["Neutral"] for b in all_buckets],
        "negative": [histogram_data[b]["Negative"] for b in all_buckets],
    }
    
    auto_export_pdf = flask.request.args.get('export_pdf') == 'true'

    return flask.render_template(
        "partials/analyze_result.html",
        upload=upload,
        percentage_positive=percentage_positive,
        percentage_neutral=percentage_neutral,
        percentage_negative=percentage_negative,
        comments_positive=comments_positive,
        comments_negative=comments_negative,
        distribution_data=distribution_data,
        emotion_histogram_data=emotion_histogram_data,
        auto_export_pdf=auto_export_pdf
    )

def is_shared_with_user(upload_id, user_id):
    from app.models import Share
    share = db.session.query(Share).filter_by(
        upload_id=upload_id, 
        recipient_id=user_id
    ).first()
    return share is not None

@analyze_bp.route("/")
def home():
    if 'user_id' not in flask.session:
        return flask.redirect(flask.url_for('main.index'))

    user_id = flask.session.get('user_id')
    order = Upload.timestamp.desc()
    uploads = db.session.query(Upload).filter_by(user_id=user_id).order_by(order)

    upload_id = flask.request.args.get('upload_id')
    selected_upload = db.session.query(Upload).get(upload_id)

    return flask.render_template("analyze.html", uploads=uploads, selected_upload=selected_upload)