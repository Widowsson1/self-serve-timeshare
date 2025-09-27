from flask import Blueprint, jsonify, request, render_template
from datetime import datetime
from src.models.user import User, db

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.json
    
    # Validate required fields
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create user
    user = User(
        username=data['username'],
        email=data['email'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        phone=data.get('phone')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a user"""
    user = User.query.get_or_404(user_id)
    data = request.json
    
    # Update allowed fields
    updatable_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    for field in updatable_fields:
        if field in data:
            # Check for uniqueness on username and email
            if field == 'username' and data[field] != user.username:
                if User.query.filter_by(username=data[field]).first():
                    return jsonify({'error': 'Username already exists'}), 400
            
            if field == 'email' and data[field] != user.email:
                if User.query.filter_by(email=data[field]).first():
                    return jsonify({'error': 'Email already exists'}), 400
            
            setattr(user, field, data[field])
    
    # Handle password update separately
    if 'password' in data:
        user.set_password(data['password'])
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Deactivate a user (soft delete)"""
    user = User.query.get_or_404(user_id)
    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.session.commit()
    return '', 204

@user_bp.route('/auth/login', methods=['POST'])
def login():
    """Authenticate user login"""
    data = request.json
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 401
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    })

@user_bp.route('/users/<int:user_id>/listings', methods=['GET'])
def get_user_listings(user_id):
    """Get listings for a specific user"""
    try:
        from src.models.listing import Listing
        listings = Listing.query.filter_by(user_id=user_id).all()
        return jsonify({
            'listings': [listing.to_dict() for listing in listings]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    return create_user()  # Reuse the create_user function

@user_bp.route('/forgot-password')
def forgot_password_page():
    """Forgot password page"""
    return render_template('forgot_password.html')

@user_bp.route('/reset-password')
def reset_password_page():
    """Reset password page"""
    return render_template('reset_password.html')

