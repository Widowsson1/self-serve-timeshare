from flask import Blueprint, request, jsonify, session
from models.listing import Listing, Favorite, db
from models.user import User
from datetime import datetime

favorites_bp = Blueprint('favorites', __name__)

@favorites_bp.route('/api/favorites', methods=['GET'])
def get_user_favorites():
    """Get all favorites for the current user"""
    try:
        # Get user ID from request headers or session
        user_id = request.headers.get('X-User-ID') or session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's favorites with listing details
        favorites = db.session.query(Favorite, Listing).join(
            Listing, Favorite.listing_id == Listing.id
        ).filter(
            Favorite.user_id == user_id,
            Listing.status == 'active'  # Only show active listings
        ).order_by(Favorite.created_at.desc()).all()
        
        favorites_data = []
        for favorite, listing in favorites:
            listing_data = listing.to_dict()
            listing_data['favorite_id'] = favorite.id
            listing_data['favorite_notes'] = favorite.notes
            listing_data['favorited_at'] = favorite.created_at.isoformat()
            favorites_data.append(listing_data)
        
        return jsonify({
            'favorites': favorites_data,
            'count': len(favorites_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@favorites_bp.route('/api/favorites', methods=['POST'])
def add_favorite():
    """Add a listing to user's favorites"""
    try:
        # Get user ID from request headers or session
        user_id = request.headers.get('X-User-ID') or session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get request data
        data = request.get_json()
        if not data or not data.get('listing_id'):
            return jsonify({'error': 'Listing ID is required'}), 400
        
        listing_id = data['listing_id']
        notes = data.get('notes', '')
        
        # Verify listing exists and is active
        listing = Listing.query.filter_by(id=listing_id, status='active').first()
        if not listing:
            return jsonify({'error': 'Listing not found or inactive'}), 404
        
        # Check if already favorited
        existing_favorite = Favorite.query.filter_by(
            user_id=user_id, 
            listing_id=listing_id
        ).first()
        
        if existing_favorite:
            return jsonify({'error': 'Listing already in favorites'}), 409
        
        # Create new favorite
        favorite = Favorite(
            user_id=user_id,
            listing_id=listing_id,
            notes=notes
        )
        
        db.session.add(favorite)
        
        # Update listing favorite count
        listing.favorite_count = (listing.favorite_count or 0) + 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Listing added to favorites',
            'favorite_id': favorite.id,
            'favorite_count': listing.favorite_count
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@favorites_bp.route('/api/favorites/<int:favorite_id>', methods=['DELETE'])
def remove_favorite(favorite_id):
    """Remove a listing from user's favorites"""
    try:
        # Get user ID from request headers or session
        user_id = request.headers.get('X-User-ID') or session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get favorite
        favorite = Favorite.query.filter_by(
            id=favorite_id, 
            user_id=user_id
        ).first()
        
        if not favorite:
            return jsonify({'error': 'Favorite not found'}), 404
        
        # Get listing to update favorite count
        listing = Listing.query.get(favorite.listing_id)
        if listing:
            listing.favorite_count = max((listing.favorite_count or 1) - 1, 0)
        
        # Delete favorite
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({
            'message': 'Listing removed from favorites',
            'favorite_count': listing.favorite_count if listing else 0
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@favorites_bp.route('/api/favorites/listing/<int:listing_id>', methods=['DELETE'])
def remove_favorite_by_listing(listing_id):
    """Remove a listing from user's favorites by listing ID"""
    try:
        # Get user ID from request headers or session
        user_id = request.headers.get('X-User-ID') or session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get favorite
        favorite = Favorite.query.filter_by(
            user_id=user_id,
            listing_id=listing_id
        ).first()
        
        if not favorite:
            return jsonify({'error': 'Favorite not found'}), 404
        
        # Get listing to update favorite count
        listing = Listing.query.get(listing_id)
        if listing:
            listing.favorite_count = max((listing.favorite_count or 1) - 1, 0)
        
        # Delete favorite
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({
            'message': 'Listing removed from favorites',
            'favorite_count': listing.favorite_count if listing else 0
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@favorites_bp.route('/api/favorites/<int:favorite_id>', methods=['PUT'])
def update_favorite_notes(favorite_id):
    """Update notes for a favorite"""
    try:
        # Get user ID from request headers or session
        user_id = request.headers.get('X-User-ID') or session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get favorite
        favorite = Favorite.query.filter_by(
            id=favorite_id, 
            user_id=user_id
        ).first()
        
        if not favorite:
            return jsonify({'error': 'Favorite not found'}), 404
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update notes
        favorite.notes = data.get('notes', '')
        favorite.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Favorite notes updated',
            'favorite': {
                'id': favorite.id,
                'notes': favorite.notes,
                'updated_at': favorite.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@favorites_bp.route('/api/favorites/check/<int:listing_id>', methods=['GET'])
def check_favorite_status(listing_id):
    """Check if a listing is favorited by the current user"""
    try:
        # Get user ID from request headers or session
        user_id = request.headers.get('X-User-ID') or session.get('user_id')
        if not user_id:
            return jsonify({'is_favorited': False})
        
        # Check if favorite exists
        favorite = Favorite.query.filter_by(
            user_id=user_id,
            listing_id=listing_id
        ).first()
        
        return jsonify({
            'is_favorited': favorite is not None,
            'favorite_id': favorite.id if favorite else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

