from flask import Blueprint, jsonify, request
from datetime import datetime
from src.models.listing import Listing, db
from src.models.user import User
import json

listing_bp = Blueprint('listing', __name__)

@listing_bp.route('/listings', methods=['GET'])
def get_listings():
    """Get all active listings with optional filtering"""
    # Get query parameters
    location = request.args.get('location')
    listing_type = request.args.get('type')  # 'sale', 'rental', 'both'
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sleeps = request.args.get('sleeps', type=int)
    
    # Build query
    query = Listing.query.filter_by(is_active=True)
    
    if location:
        query = query.filter(Listing.location.ilike(f'%{location}%'))
    
    if listing_type:
        if listing_type in ['sale', 'rental']:
            query = query.filter((Listing.listing_type == listing_type) | (Listing.listing_type == 'both'))
        elif listing_type == 'both':
            query = query.filter(Listing.listing_type == 'both')
    
    if min_price:
        if listing_type == 'sale':
            query = query.filter(Listing.sale_price >= min_price)
        elif listing_type == 'rental':
            query = query.filter(Listing.rental_price_per_night >= min_price)
    
    if max_price:
        if listing_type == 'sale':
            query = query.filter(Listing.sale_price <= max_price)
        elif listing_type == 'rental':
            query = query.filter(Listing.rental_price_per_night <= max_price)
    
    if sleeps:
        query = query.filter(Listing.sleeps >= sleeps)
    
    listings = query.all()
    return jsonify([listing.to_dict() for listing in listings])

@listing_bp.route('/listings', methods=['POST'])
def create_listing():
    """Create a new listing"""
    data = request.json
    
    # Validate required fields
    required_fields = ['title', 'description', 'location', 'resort_name', 'unit_type', 
                      'sleeps', 'bedrooms', 'bathrooms', 'listing_type', 'user_id']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate user exists
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if user has active membership
    if not user.has_active_membership():
        return jsonify({'error': 'Active membership required to create listings'}), 403
    
    # Validate listing type and pricing
    listing_type = data['listing_type']
    if listing_type not in ['sale', 'rental', 'both']:
        return jsonify({'error': 'Invalid listing type. Must be sale, rental, or both'}), 400
    
    if listing_type in ['sale', 'both'] and not data.get('sale_price'):
        return jsonify({'error': 'Sale price required for sale listings'}), 400
    
    if listing_type in ['rental', 'both'] and not data.get('rental_price_per_night'):
        return jsonify({'error': 'Rental price required for rental listings'}), 400
    
    # Create listing
    listing = Listing(
        title=data['title'],
        description=data['description'],
        location=data['location'],
        resort_name=data['resort_name'],
        unit_type=data['unit_type'],
        sleeps=data['sleeps'],
        bedrooms=data['bedrooms'],
        bathrooms=data['bathrooms'],
        sale_price=data.get('sale_price'),
        rental_price_per_night=data.get('rental_price_per_night'),
        listing_type=listing_type,
        available_from=datetime.fromisoformat(data['available_from']) if data.get('available_from') else None,
        available_to=datetime.fromisoformat(data['available_to']) if data.get('available_to') else None,
        image_urls=json.dumps(data.get('image_urls', [])),
        user_id=data['user_id']
    )
    
    db.session.add(listing)
    db.session.commit()
    return jsonify(listing.to_dict()), 201

@listing_bp.route('/listings/<int:listing_id>', methods=['GET'])
def get_listing(listing_id):
    """Get a specific listing"""
    listing = Listing.query.get_or_404(listing_id)
    return jsonify(listing.to_dict())

@listing_bp.route('/listings/<int:listing_id>', methods=['PUT'])
def update_listing(listing_id):
    """Update a listing"""
    listing = Listing.query.get_or_404(listing_id)
    data = request.json
    
    # Update fields if provided
    updatable_fields = ['title', 'description', 'location', 'resort_name', 'unit_type',
                       'sleeps', 'bedrooms', 'bathrooms', 'sale_price', 'rental_price_per_night',
                       'listing_type', 'is_active']
    
    for field in updatable_fields:
        if field in data:
            setattr(listing, field, data[field])
    
    # Handle date fields
    if 'available_from' in data:
        listing.available_from = datetime.fromisoformat(data['available_from']) if data['available_from'] else None
    
    if 'available_to' in data:
        listing.available_to = datetime.fromisoformat(data['available_to']) if data['available_to'] else None
    
    # Handle image URLs
    if 'image_urls' in data:
        listing.image_urls = json.dumps(data['image_urls'])
    
    listing.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(listing.to_dict())

@listing_bp.route('/listings/<int:listing_id>', methods=['DELETE'])
def delete_listing(listing_id):
    """Delete a listing (soft delete by setting is_active to False)"""
    listing = Listing.query.get_or_404(listing_id)
    listing.is_active = False
    listing.updated_at = datetime.utcnow()
    db.session.commit()
    return '', 204

@listing_bp.route('/users/<int:user_id>/listings', methods=['GET'])
def get_user_listings(user_id):
    """Get all listings for a specific user"""
    user = User.query.get_or_404(user_id)
    listings = Listing.query.filter_by(user_id=user_id).all()
    return jsonify([listing.to_dict() for listing in listings])

