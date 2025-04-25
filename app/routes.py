# app/routes.py
from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/upload")
def upload():
    return render_template("upload.html")

@main_bp.route("/visualize")
def visualize():
    return render_template("visualize.html")

@main_bp.route("/share")
def share():
    return render_template("share.html")# route definitions go here
