"""
Mock Flask Application for Testing

This module provides a mock Flask application for testing purposes.
It simulates the behavior of the real application without requiring
external dependencies like databases or APIs.
"""

from flask import Flask, jsonify, request, render_template_string
from unittest.mock import MagicMock

def create_mock_app():
    """Create a mock Flask application for testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.secret_key = 'test_secret_key'
    
    # Mock user data
    users = {
        'test@example.com': {
            'email': 'test@example.com',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    }
    
    # Mock upload data
    uploads = [
        {
            'id': 1,
            'title': 'Test Dataset',
            'platform': 'Twitter',
            'date': '2023-01-01',
            'comments_count': 3
        }
    ]
    
    # Mock routes
    @app.route('/')
    def home():
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SentiSocial</title>
        </head>
        <body>
            <nav class="navbar">
                <div class="navbar-nav">
                    <a class="nav-link" href="/">Home</a>
                    <a class="nav-link" href="/upload">Upload</a>
                    <a class="nav-link" href="/analyze">Analysis</a>
                    <a class="nav-link" href="/share">Share</a>
                </div>
                <div>
                    <button data-bs-target="#loginModal">Login</button>
                    <button data-bs-target="#registerModal">Sign Up</button>
                </div>
            </nav>
            <div class="hero-section">
                <h1>Decode Sentiment Trends</h1>
            </div>
            
            <!-- Register Modal -->
            <div id="registerModal" style="display: none;">
                <form id="registerForm">
                    <input id="firstName" name="first_name">
                    <input id="lastName" name="last_name">
                    <input id="registerEmail" name="email">
                    <input id="registerPassword" name="password" type="password">
                    <input id="confirmPassword" name="confirm_password" type="password">
                    <button type="submit">Create Account</button>
                </form>
                <div id="registerError"></div>
            </div>
            
            <!-- Login Modal -->
            <div id="loginModal" style="display: none;">
                <form id="loginForm">
                    <input id="loginEmail" name="email">
                    <input id="loginPassword" name="password" type="password">
                    <button type="submit">Login</button>
                </form>
                <div id="loginError"></div>
            </div>
        </body>
        </html>
        """)
    
    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        email = data.get('email')
        
        if email in users:
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        users[email] = {
            'email': email,
            'password': data.get('password'),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name')
        }
        
        return jsonify({'success': True, 'message': 'Registration successful'})
    
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if email in users and users[email]['password'] == password:
            return jsonify({
                'success': True, 
                'user': {
                    'email': email,
                    'first_name': users[email]['first_name'],
                    'last_name': users[email]['last_name']
                }
            })
        
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    @app.route('/upload')
    def upload():
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Upload Data - SentiSocial</title>
        </head>
        <body>
            <div class="upload-options">
                <div id="manualEntryCard">Manual Entry</div>
                <div id="fileUploadCard">File Upload</div>
                <div id="urlEntryCard">Platform URL</div>
            </div>
            
            <div id="manualEntryForm" style="display: none;">
                <form>
                    <select name="platform">
                        <option value="" disabled selected>Select platform</option>
                        <option value="Twitter">Twitter</option>
                        <option value="Facebook">Facebook</option>
                    </select>
                    <input name="title" placeholder="Enter a title">
                    <textarea name="comments" placeholder="Enter comments"></textarea>
                    <button type="submit">Analyze Comments</button>
                </form>
            </div>
            
            <div id="successModal" style="display: none;">
                <h5>Upload Successful</h5>
                <p>Your data has been uploaded successfully!</p>
            </div>
        </body>
        </html>
        """)
    
    @app.route('/upload/text', methods=['POST'])
    def upload_text():
        # Mock successful upload
        uploads.append({
            'id': len(uploads) + 1,
            'title': request.form.get('title'),
            'platform': request.form.get('platform'),
            'date': '2023-01-01',
            'comments_count': 3
        })
        return jsonify({'success': True})
    
    @app.route('/analyze')
    def analyze():
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Analysis - SentiSocial</title>
        </head>
        <body>
            <select id="upload-select">
                <option value="" disabled selected>Select a dataset</option>
                {% for upload in uploads %}
                <option value="{{ upload.id }}">{{ upload.title }}</option>
                {% endfor %}
            </select>
            
            <div id="analyze-result-info">
                No Dataset Selected
            </div>
            
            <iframe id="analyze-result-iframe" style="display: none;"></iframe>
        </body>
        </html>
        """, uploads=uploads)
    
    @app.route('/share')
    def share():
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Share - SentiSocial</title>
        </head>
        <body>
            <h1>Share Your Analysis</h1>
        </body>
        </html>
        """)
    
    return app
