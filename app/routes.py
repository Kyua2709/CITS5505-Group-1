# app/routes.py

from flask import render_template, request, redirect, url_for
from app import app
from app.models import predict_single_text, predict_batch_text
import os

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if not file:
            return "No file uploaded!", 400

        file_contents = file.read().decode('utf-8')
        lines = file_contents.split('\n')
        lines = [line.strip() for line in lines if line.strip()]

        # 预测每一行的情感
        results = predict_batch_text(lines)

        return render_template('upload.html', results=results)
    return render_template('upload.html')
