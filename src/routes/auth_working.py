from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from models.user_fixed import User, db
from datetime import datetime

auth_working_bp = Blueprint('auth_working', __name__)

@auth_working_bp.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username_or_email = data.get('username')
        password = data.get('password')
        
        if not username_or_email or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        # Find user
        user = User.query.filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
        
        # Create session
        session['user_id'] = user.id
        session['username'] = user.username
        session['logged_in'] = True
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Login failed'}), 500

@auth_working_bp.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Check if user exists
        if User.query.filter_by(username=data.get('username')).first():
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'success': False, 'message': 'Email already exists'}), 400
        
        # Create user
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            is_active=True,
            email_verified=True,
            account_type='free'
        )
        user.set_password(data.get('password'))
        
        db.session.add(user)
        db.session.commit()
        
        # Auto login
        session['user_id'] = user.id
        session['username'] = user.username
        session['logged_in'] = True
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Registration failed'}), 500

@auth_working_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@auth_working_bp.route('/api/auth/check', methods=['GET'])
def check_auth():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user and user.is_active:
            return jsonify({
                'authenticated': True,
                'user': user.to_dict()
            })
    
    return jsonify({'authenticated': False})

