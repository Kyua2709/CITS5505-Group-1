from flask import Blueprint, render_template, request, jsonify, redirect, session, url_for, flash, current_app
from app.models import User, db

# Define Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return render_template('login.html')
    return render_template('index.html')

@main_bp.route('/login')
def logged_in_home():
    """Logged in home page"""
    if 'user_id' not in session:
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
    return redirect(url_for('main.index'))

@main_bp.route('/share')
def share():
    """Share page"""
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('main.index'))
    return render_template('share.html')