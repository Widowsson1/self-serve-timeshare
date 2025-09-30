from flask import Blueprint, request, jsonify, session
from models.listing import Listing, db
from models.user_fixed import User
from datetime import datetime

listing_working_bp = Blueprint('listing_working', __name__)

@listing_working_bp.route('/api/listings', methods=['POST'])
def create_listing():
    try:
        data = request.get_json()
        
        # Get user
        user_id = session.get('user_id', 1)  # Default to user 1 if no session
        
        # Create listing
        listing = Listing(
            title=data.get('title'),
            property_type=data.get('property_type'),
            resort_name=data.get('resort_name'),
            city=data.get('city'),
            state=data.get('state'),
            country=data.get('country'),
            sale_price=data.get('sale_price'),
            weekly_rental_price=data.get('weekly_rental_price'),
            description=data.get('description'),
            contact_email=data.get('contact_email', 'test@example.com'),
            contact_phone=data.get('contact_phone', '555-123-4567'),
            user_id=user_id,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(listing)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Listing created successfully',
            'listing_id': listing.id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to create listing'}), 500

@listing_working_bp.route('/api/listings', methods=['GET'])
def get_listings():
    try:
        listings = Listing.query.filter_by(is_active=True).all()
        
        listings_data = []
        for listing in listings:
            listings_data.append({
                'id': listing.id,
                'title': listing.title,
                'property_type': listing.property_type,
                'resort_name': listing.resort_name,
                'city': listing.city,
                'state': listing.state,
                'country': listing.country,
                'sale_price': listing.sale_price,
                'weekly_rental_price': listing.weekly_rental_price,
                'description': listing.description,
                'created_at': listing.created_at.isoformat() if listing.created_at else None
            })
        
        return jsonify({
            'success': True,
            'listings': listings_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to get listings'}), 500

@listing_working_bp.route('/api/user/<int:user_id>/listings', methods=['GET'])
def get_user_listings(user_id):
    try:
        listings = Listing.query.filter_by(user_id=user_id, is_active=True).all()
        
        listings_data = []
        for listing in listings:
            listings_data.append({
                'id': listing.id,
                'title': listing.title,
                'property_type': listing.property_type,
                'resort_name': listing.resort_name,
                'city': listing.city,
                'state': listing.state,
                'sale_price': listing.sale_price,
                'weekly_rental_price': listing.weekly_rental_price,
                'created_at': listing.created_at.isoformat() if listing.created_at else None
            })
        
        return jsonify({
            'success': True,
            'listings': listings_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'listings': []})

