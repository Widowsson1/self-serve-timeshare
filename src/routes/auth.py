from flask import Blueprint, jsonify, request, session
from models.user import User, db
from datetime import datetime
import secrets
import string

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    try:
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user and user.is_active:
                return jsonify({
                    'authenticated': True,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    }
                })
        
        return jsonify({'authenticated': False})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """User login with session management"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        print(f"Login attempt - Username: {username}, Email: {email}")
        
        if not password:
            return jsonify({'error': 'Password required'}), 400
        
        if not username and not email:
            return jsonify({'error': 'Username or email required'}), 400
        
        # Find user by username or email
        user = None
        if username:
            user = User.query.filter_by(username=username).first()
            print(f"User found by username: {user is not None}")
        elif email:
            user = User.query.filter_by(email=email).first()
            print(f"User found by email: {user is not None}")
        
        if user:
            print(f"User active: {user.is_active}")
            print(f"Password check: {user.check_password(password)}")
        
        if user and user.check_password(password) and user.is_active:
            session['user_id'] = user.id
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
            
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout"""
    try:
        session.clear()
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """User registration"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone = data.get('phone')
        
        if not all([username, email, password, first_name, last_name]):
            return jsonify({'error': 'Username, email, password, first name, and last name are required'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
            
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Auto-login after registration
        session['user_id'] = user.id
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/profile', methods=['GET'])
def get_profile():
    """Get current user profile"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/profile', methods=['PUT'])
def update_profile():
    """Update current user profile"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        updatable_fields = ['first_name', 'last_name', 'phone']
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # Handle email update with uniqueness check
        if 'email' in data and data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email already exists'}), 400
            user.email = data['email']
        
        # Handle username update with uniqueness check
        if 'username' in data and data['username'] != user.username:
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'error': 'Username already exists'}), 400
            user.username = data['username']
        
        # Handle password update
        if 'password' in data:
            user.set_password(data['password'])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@auth_bp.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            # Don't reveal if email exists or not for security
            return jsonify({'success': True, 'message': 'If the email exists, a reset link has been sent'})
        
        # Generate reset token
        reset_token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow().replace(hour=datetime.utcnow().hour + 1)  # 1 hour expiry
        db.session.commit()
        
        # In a real application, you would send an email here
        # For now, we'll return the token for testing purposes
        return jsonify({
            'success': True, 
            'message': 'Password reset instructions sent to your email',
            'reset_token': reset_token  # Remove this in production
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('password')
        
        if not token or not new_password:
            return jsonify({'error': 'Token and new password are required'}), 400
        
        user = User.query.filter_by(reset_token=token).first()
        if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
            return jsonify({'error': 'Invalid or expired reset token'}), 400
        
        # Update password and clear reset token
        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Password reset successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/change-password', methods=['POST'])
def change_password():
    """Change password for authenticated user"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        if not user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Password changed successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

