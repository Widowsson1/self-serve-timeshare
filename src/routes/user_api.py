from flask import Blueprint, jsonify, session
from models.user import User
from models.membership import Membership

user_api_bp = Blueprint('user_api', __name__)

@user_api_bp.route('/api/user/current', methods=['GET'])
def get_current_user():
    """Get current authenticated user information"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's current membership
        membership = Membership.query.filter_by(user_id=user.id).first()
        subscription_plan = membership.plan_type if membership else 'free'
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'subscription_plan': subscription_plan,
            'sms_consent': user.sms_consent if hasattr(user, 'sms_consent') else False,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_api_bp.route('/api/user/membership', methods=['GET'])
def get_user_membership():
    """Get current user's membership details"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        membership = Membership.query.filter_by(user_id=session['user_id']).first()
        
        if not membership:
            return jsonify({
                'plan_type': 'free',
                'status': 'active',
                'created_at': None,
                'stripe_subscription_id': None
            })
        
        return jsonify({
            'id': membership.id,
            'user_id': membership.user_id,
            'plan_type': membership.plan_type,
            'status': membership.status,
            'created_at': membership.created_at.isoformat() if membership.created_at else None,
            'stripe_subscription_id': membership.stripe_subscription_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
