from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from src.models.membership import Membership, db
from src.models.user import User

membership_bp = Blueprint('membership', __name__)

@membership_bp.route('/api/memberships', methods=['GET'])
def get_api_memberships():
    """Get memberships via API endpoint"""
    try:
        memberships = Membership.query.all()
        return jsonify({
            'memberships': [membership.to_dict() for membership in memberships]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@membership_bp.route('/memberships', methods=['GET'])
def get_memberships():
    """Get all memberships"""
    memberships = Membership.query.all()
    return jsonify([membership.to_dict() for membership in memberships])

@membership_bp.route('/memberships', methods=['POST'])
def create_membership():
    """Create a new membership (simulate payment processing)"""
    data = request.json
    
    # Validate required fields
    required_fields = ['user_id', 'membership_type', 'payment_amount']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate user exists
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if user already has an active membership
    existing_membership = Membership.query.filter_by(
        user_id=data['user_id'], 
        status='active'
    ).first()
    
    if existing_membership and existing_membership.is_active():
        return jsonify({'error': 'User already has an active membership'}), 400
    
    # Determine membership duration based on type
    membership_type = data['membership_type']
    start_date = datetime.utcnow()
    end_date = None
    
    if membership_type == 'basic_monthly':
        end_date = start_date + timedelta(days=30)
    elif membership_type == 'basic_yearly':
        end_date = start_date + timedelta(days=365)
    elif membership_type == 'lifetime':
        end_date = None  # No expiration
    
    # Create membership
    membership = Membership(
        user_id=data['user_id'],
        membership_type=membership_type,
        status='active',
        payment_amount=data['payment_amount'],
        payment_method=data.get('payment_method', 'credit_card'),
        transaction_id=data.get('transaction_id', f'txn_{datetime.utcnow().timestamp()}'),
        start_date=start_date,
        end_date=end_date
    )
    
    db.session.add(membership)
    db.session.commit()
    return jsonify(membership.to_dict()), 201

@membership_bp.route('/memberships/<int:membership_id>', methods=['GET'])
def get_membership(membership_id):
    """Get a specific membership"""
    membership = Membership.query.get_or_404(membership_id)
    return jsonify(membership.to_dict())

@membership_bp.route('/memberships/<int:membership_id>', methods=['PUT'])
def update_membership(membership_id):
    """Update a membership"""
    membership = Membership.query.get_or_404(membership_id)
    data = request.json
    
    # Update allowed fields
    updatable_fields = ['status', 'end_date']
    for field in updatable_fields:
        if field in data:
            if field == 'end_date' and data[field]:
                membership.end_date = datetime.fromisoformat(data[field])
            else:
                setattr(membership, field, data[field])
    
    membership.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(membership.to_dict())

@membership_bp.route('/memberships/<int:membership_id>/cancel', methods=['POST'])
def cancel_membership(membership_id):
    """Cancel a membership"""
    membership = Membership.query.get_or_404(membership_id)
    membership.status = 'cancelled'
    membership.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(membership.to_dict())

@membership_bp.route('/users/<int:user_id>/membership', methods=['GET'])
def get_user_membership(user_id):
    """Get current active membership for a user"""
    user = User.query.get_or_404(user_id)
    
    # Get the most recent active membership
    membership = Membership.query.filter_by(
        user_id=user_id, 
        status='active'
    ).order_by(Membership.created_at.desc()).first()
    
    if not membership:
        return jsonify({'error': 'No active membership found'}), 404
    
    return jsonify(membership.to_dict())

@membership_bp.route('/users/<int:user_id>/membership/status', methods=['GET'])
def check_membership_status(user_id):
    """Check if user has active membership"""
    user = User.query.get_or_404(user_id)
    has_active = user.has_active_membership()
    
    return jsonify({
        'user_id': user_id,
        'has_active_membership': has_active,
        'checked_at': datetime.utcnow().isoformat()
    })

