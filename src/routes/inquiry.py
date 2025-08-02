from flask import Blueprint, request, jsonify, session
from src.models.listing import Listing, db
from src.models.user import User

inquiry_bp = Blueprint('inquiry', __name__)

@inquiry_bp.route('/api/listings/<int:listing_id>/inquiry', methods=['POST'])
def track_inquiry(listing_id):
    """Track an inquiry for a listing"""
    try:
        # Get user ID from request headers or session
        user_id = request.headers.get('X-User-ID') or session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get listing
        listing = Listing.query.get_or_404(listing_id)
        
        # Increment inquiry count
        listing.inquiry_count = (listing.inquiry_count or 0) + 1
        db.session.commit()
        
        return jsonify({
            'message': 'Inquiry tracked successfully',
            'inquiry_count': listing.inquiry_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

