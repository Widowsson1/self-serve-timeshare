from flask import Blueprint, request, jsonify, session
from src.models.user import User, db
from werkzeug.security import generate_password_hash, check_password_hash
import re

browser_auth_bp = Blueprint('browser_auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@browser_auth_bp.route('/api/browser/register', methods=['POST'])
def register_browser_account():
    """Register a browser account for favorites and watchlist"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        
        # Validate input
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new browser user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            account_type='browser'  # Browser account for favorites/watchlist
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Set session
        session['user_id'] = user.id
        session['username'] = user.username
        session['account_type'] = user.account_type
        
        return jsonify({
            'message': 'Browser account created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@browser_auth_bp.route('/api/browser/login', methods=['POST'])
def login_browser_account():
    """Login to browser account"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get login credentials
        username_or_email = data.get('username_or_email', '').strip()
        password = data.get('password', '')
        
        if not username_or_email or not password:
            return jsonify({'error': 'Username/email and password are required'}), 400
        
        # Find user by username or email
        user = User.query.filter(
            db.or_(
                User.username == username_or_email,
                User.email == username_or_email.lower()
            )
        ).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Set session
        session['user_id'] = user.id
        session['username'] = user.username
        session['account_type'] = user.account_type
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@browser_auth_bp.route('/api/browser/logout', methods=['POST'])
def logout_browser_account():
    """Logout from browser account"""
    try:
        session.clear()
        return jsonify({'message': 'Logout successful'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@browser_auth_bp.route('/api/browser/profile', methods=['GET'])
def get_browser_profile():
    """Get browser account profile"""
    try:
        user_id = request.headers.get('X-User-ID') or session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user stats
        from src.models.listing import Favorite
        favorite_count = Favorite.query.filter_by(user_id=user_id).count()
        
        profile_data = user.to_dict()
        profile_data['stats'] = {
            'favorite_count': favorite_count,
            'account_type': user.account_type
        }
        
        return jsonify(profile_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@browser_auth_bp.route('/api/browser/profile', methods=['PUT'])
def update_browser_profile():
    """Update browser account profile"""
    try:
        user_id = request.headers.get('X-User-ID') or session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        updatable_fields = ['first_name', 'last_name', 'email']
        for field in updatable_fields:
            if field in data:
                if field == 'email':
                    email = data[field].strip().lower()
                    if not validate_email(email):
                        return jsonify({'error': 'Invalid email format'}), 400
                    # Check if email is already taken by another user
                    existing_user = User.query.filter(
                        User.email == email,
                        User.id != user_id
                    ).first()
                    if existing_user:
                        return jsonify({'error': 'Email already in use'}), 409
                    setattr(user, field, email)
                else:
                    setattr(user, field, data[field].strip())
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@browser_auth_bp.route('/api/browser/change-password', methods=['POST'])
def change_browser_password():
    """Change browser account password"""
    try:
        user_id = request.headers.get('X-User-ID') or session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current and new passwords are required'}), 400
        
        # Verify current password
        if not check_password_hash(user.password_hash, current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Validate new password
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters long'}), 400
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

