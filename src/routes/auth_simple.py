from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from models.user import User, db
from datetime import datetime

auth_simple_bp = Blueprint('auth_simple', __name__)

@auth_simple_bp.route('/api/auth/login', methods=['POST'])
def simple_login():
    """Simplified login without reset_token dependencies"""
    try:
        data = request.get_json()
        username_or_email = data.get('username')
        password = data.get('password')
        
        print(f"Simple login attempt for: {username_or_email}")
        
        if not username_or_email or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        # Simple query without reset_token fields
        try:
            # Try to find user by username first
            user = User.query.filter_by(username=username_or_email).first()
            if not user:
                # Try by email
                user = User.query.filter_by(email=username_or_email).first()
        except Exception as query_error:
            print(f"Query error: {query_error}")
            # If there's a database schema issue, create a test user
            return jsonify({'success': False, 'message': 'Database schema needs migration'}), 500
        
        if not user:
            print(f"User not found: {username_or_email}")
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
        
        print(f"User found: {user.username}")
        
        # Check password
        if hasattr(user, 'check_password'):
            password_valid = user.check_password(password)
        else:
            password_valid = check_password_hash(user.password_hash, password)
        
        if not password_valid:
            print(f"Invalid password for user: {user.username}")
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
        
        # Create session
        session['user_id'] = user.id
        session['username'] = user.username
        session['logged_in'] = True
        
        print(f"Login successful for: {user.username}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        })
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'success': False, 'message': f'Login failed: {str(e)}'}), 500

@auth_simple_bp.route('/api/auth/create-test-user', methods=['POST'])
def create_test_user():
    """Create a test user for immediate testing"""
    try:
        # Check if testuser already exists
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            return jsonify({'success': True, 'message': 'Test user already exists'})
        
        # Create test user
        password_hash = generate_password_hash('password123')
        
        # Create user with minimal required fields
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=password_hash,
            first_name='Test',
            last_name='User',
            is_active=True,
            email_verified=True,
            account_type='subscriber',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(test_user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Test user created successfully'})
        
    except Exception as e:
        print(f"Error creating test user: {str(e)}")
        return jsonify({'success': False, 'message': f'Failed to create test user: {str(e)}'}), 500

