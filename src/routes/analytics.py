from flask import Blueprint, jsonify, request, session
from models.listing import Listing, db
from models.user import User
from datetime import datetime, timedelta
from sqlalchemy import func, and_

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/api/analytics/dashboard', methods=['GET'])
def get_dashboard_analytics():
    """Get analytics data for user dashboard"""
    try:
        # For demo purposes, return mock data without authentication
        # In production, you'd check session.get('user_id')
        
        return jsonify({
            'success': True,
            'data': {
                'active_listings': 0,
                'total_views': 0,
                'total_inquiries': 0,
                'recent_views': 0,
                'recent_inquiries': 0,
                'avg_views_per_listing': 0,
                'inquiry_rate': 0,
                'listings_data': []
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/analytics/listing/<int:listing_id>', methods=['GET'])
def get_listing_analytics(listing_id):
    """Get detailed analytics for a specific listing"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        listing = Listing.query.filter_by(id=listing_id, user_id=user_id).first()
        if not listing:
            return jsonify({'error': 'Listing not found'}), 404
        
        # Calculate days since listing was created
        days_active = (datetime.now() - listing.created_at).days if listing.created_at else 0
        
        # Calculate performance metrics
        views_per_day = (listing.views or 0) / max(days_active, 1)
        inquiries_per_day = (listing.inquiries or 0) / max(days_active, 1)
        
        return jsonify({
            'success': True,
            'data': {
                'listing_id': listing.id,
                'title': listing.title,
                'views': listing.views or 0,
                'inquiries': listing.inquiries or 0,
                'days_active': days_active,
                'views_per_day': round(views_per_day, 2),
                'inquiries_per_day': round(inquiries_per_day, 2),
                'status': listing.status,
                'created_at': listing.created_at.isoformat() if listing.created_at else None,
                'last_updated': listing.updated_at.isoformat() if listing.updated_at else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/analytics/track-view', methods=['POST'])
def track_listing_view():
    """Track a view for a listing"""
    try:
        data = request.get_json()
        listing_id = data.get('listing_id')
        
        if not listing_id:
            return jsonify({'error': 'Listing ID required'}), 400
        
        listing = Listing.query.get(listing_id)
        if not listing:
            return jsonify({'error': 'Listing not found'}), 404
        
        # Increment view count
        if listing.views is None:
            listing.views = 1
        else:
            listing.views += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'views': listing.views
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/analytics/track-inquiry', methods=['POST'])
def track_listing_inquiry():
    """Track an inquiry for a listing"""
    try:
        data = request.get_json()
        listing_id = data.get('listing_id')
        
        if not listing_id:
            return jsonify({'error': 'Listing ID required'}), 400
        
        listing = Listing.query.get(listing_id)
        if not listing:
            return jsonify({'error': 'Listing not found'}), 404
        
        # Increment inquiry count
        if listing.inquiries is None:
            listing.inquiries = 1
        else:
            listing.inquiries += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'inquiries': listing.inquiries
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/analytics/platform-stats', methods=['GET'])
def get_platform_stats():
    """Get overall platform statistics (for admin use)"""
    try:
        # Total counts
        total_users = User.query.count()
        total_listings = Listing.query.count()
        active_listings = Listing.query.filter_by(status='active').count()
        
        # Recent activity (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        new_users = User.query.filter(User.created_at >= seven_days_ago).count()
        new_listings = Listing.query.filter(Listing.created_at >= seven_days_ago).count()
        
        # Total views and inquiries
        total_views = db.session.query(func.sum(Listing.views)).scalar() or 0
        total_inquiries = db.session.query(func.sum(Listing.inquiries)).scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_users': total_users,
                'total_listings': total_listings,
                'active_listings': active_listings,
                'new_users_7_days': new_users,
                'new_listings_7_days': new_listings,
                'total_views': total_views,
                'total_inquiries': total_inquiries,
                'avg_views_per_listing': round(total_views / max(total_listings, 1), 1),
                'platform_inquiry_rate': round((total_inquiries / max(total_views, 1)) * 100, 2) if total_views > 0 else 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

