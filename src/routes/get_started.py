from flask import Blueprint, render_template

get_started_bp = Blueprint('get_started', __name__)

@get_started_bp.route('/get-started')
def get_started():
    """Get Started page"""
    return render_template('get_started.html')

@get_started_bp.route('/signup')
def signup():
    """Signup page"""
    return render_template('signup.html')

@get_started_bp.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')

