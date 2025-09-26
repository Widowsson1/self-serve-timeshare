from flask import Blueprint, request, jsonify, session
from src.models.listing import Listing, ListingPhoto, Favorite, db
from src.models.user import User
from src.models.membership import Membership
from datetime import datetime
import json

listing_bp = Blueprint('listing', __name__)

@listing_bp.route('/api/listings', methods=['GET'])
def get_listings():
    """Get all active listings with optional filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        property_type = request.args.get('property_type')
        city = request.args.get('city')
        state = request.args.get('state')
        country = request.args.get('country')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        bedrooms = request.args.get('bedrooms', type=int)
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Build query
        query = Listing.query.filter_by(status='active')
        
        # Apply filters
        if property_type:
            query = query.filter(Listing.property_type.in_([property_type, 'both']))
        if city:
            query = query.filter(Listing.city.ilike(f'%{city}%'))
        if state:
            query = query.filter(Listing.state.ilike(f'%{state}%'))
        if country:
            query = query.filter(Listing.country.ilike(f'%{country}%'))
        if bedrooms:
            query = query.filter(Listing.bedrooms >= bedrooms)
        if min_price:
            query = query.filter(
                db.or_(
                    Listing.sale_price >= min_price,
                    Listing.rental_price_weekly >= min_price
                )
            )
        if max_price:
            query = query.filter(
                db.or_(
                    Listing.sale_price <= max_price,
                    Listing.rental_price_weekly <= max_price
                )
            )
        
        # Apply sorting
        order_clauses = []
        
        if sort_by == 'price':
            if sort_order == 'desc':
                order_clauses.extend([Listing.sale_price.desc().nullslast(), 
                                     Listing.rental_price_weekly.desc().nullslast()])
            else:
                order_clauses.extend([Listing.sale_price.asc().nullsfirst(), 
                                     Listing.rental_price_weekly.asc().nullsfirst()])
        elif sort_by == 'created_at':
            if sort_order == 'desc':
                order_clauses.append(Listing.created_at.desc())
            else:
                order_clauses.append(Listing.created_at.asc())
        elif sort_by == 'view_count':
            if sort_order == 'desc':
                order_clauses.append(Listing.view_count.desc())
            else:
                order_clauses.append(Listing.view_count.asc())
        
        # Featured listings first, then apply other sorting
        query = query.order_by(Listing.is_featured.desc(), *order_clauses)
        
        # Paginate
        listings = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'listings': [listing.to_dict() for listing in listings.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': listings.total,
                'pages': listings.pages,
                'has_next': listings.has_next,
                'has_prev': listings.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@listing_bp.route('/api/listings/<int:listing_id>', methods=['GET'])
def get_listing(listing_id):
    """Get a specific listing by ID"""
    try:
        listing = Listing.query.get_or_404(listing_id)
        
        # Increment view count
        listing.increment_view_count()
        
        # Get listing with user info
        listing_data = listing.to_dict(include_user=True)
        
        # Get photos
        photos = ListingPhoto.query.filter_by(listing_id=listing_id).order_by(
            ListingPhoto.is_main.desc(), 
            ListingPhoto.sort_order.asc()
        ).all()
        listing_data['photos'] = [photo.to_dict() for photo in photos]
        
        return jsonify(listing_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@listing_bp.route('/api/listings', methods=['POST'])
def create_listing():
    """Create a new listing (subscribers only)"""
    try:
        # For demo purposes, use a default user ID
        # In production, get from session or authentication
        user_id = 1  # Default test user
        user = User.query.get(user_id)
        
        # Get listing data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['title', 'property_type', 'resort_name', 'city', 'state', 'country']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create new listing
        listing = Listing(
            user_id=user_id,
            title=data['title'],
            description=data.get('description'),
            property_type=data['property_type'],
            resort_name=data['resort_name'],
            city=data['city'],
            state=data['state'],
            country=data['country'],
            zip_code=data.get('zip_code'),
            bedrooms=data.get('bedrooms'),
            bathrooms=data.get('bathrooms'),
            sleeps=data.get('sleeps'),
            unit_size=data.get('unit_size'),
            floor=data.get('floor'),
            view_type=data.get('view_type'),
            ownership_type=data.get('ownership_type'),
            week_number=data.get('week_number'),
            season=data.get('season'),
            usage_type=data.get('usage_type'),
            sale_price=data.get('sale_price'),
            rental_price_weekly=data.get('rental_price_weekly'),
            rental_price_nightly=data.get('rental_price_nightly'),
            maintenance_fee=data.get('maintenance_fee'),
            available_dates=data.get('available_dates'),
            check_in_day=data.get('check_in_day'),
            amenities=json.dumps(data.get('amenities', [])) if data.get('amenities') else None,
            contact_method=data.get('contact_method', 'email'),
            contact_phone=data.get('contact_phone'),
            contact_email=data.get('contact_email') or (user.email if user else 'test@example.com')
        )
        
        db.session.add(listing)
        db.session.commit()
        
        return jsonify({
            'message': 'Listing created successfully',
            'listing': listing.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@listing_bp.route('/api/listings/<int:listing_id>', methods=['PUT'])
def update_listing(listing_id):
    """Update an existing listing (owner only)"""
    try:
        # Get user ID from request headers or session
        user_id = request.headers.get('X-User-ID') or session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get listing
        listing = Listing.query.get_or_404(listing_id)
        
        # Verify ownership
        if listing.user_id != int(user_id):
            return jsonify({'error': 'Not authorized to update this listing'}), 403
        
        # Get update data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields
        updatable_fields = [
            'title', 'description', 'property_type', 'resort_name', 'city', 'state', 
            'country', 'zip_code', 'bedrooms', 'bathrooms', 'sleeps', 'unit_size', 
            'floor', 'view_type', 'ownership_type', 'week_number', 'season', 
            'usage_type', 'sale_price', 'rental_price_weekly', 'rental_price_nightly', 
            'maintenance_fee', 'available_dates', 'check_in_day', 'contact_method', 
            'contact_phone', 'contact_email', 'status'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'amenities':
                    setattr(listing, field, json.dumps(data[field]) if data[field] else None)
                else:
                    setattr(listing, field, data[field])
        
        listing.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Listing updated successfully',
            'listing': listing.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@listing_bp.route('/api/listings/<int:listing_id>', methods=['DELETE'])
def delete_listing(listing_id):
    """Delete a listing (owner only)"""
    try:
        # Get user ID from request headers or session
        user_id = request.headers.get('X-User-ID') or session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get listing
        listing = Listing.query.get_or_404(listing_id)
        
        # Verify ownership
        if listing.user_id != int(user_id):
            return jsonify({'error': 'Not authorized to delete this listing'}), 403
        
        # Delete listing (cascade will handle photos and favorites)
        db.session.delete(listing)
        db.session.commit()
        
        return jsonify({'message': 'Listing deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@listing_bp.route('/api/users/<int:user_id>/listings', methods=['GET'])
def get_user_listings(user_id):
    """Get all listings for a specific user"""
    try:
        # Get current user ID for authorization
        current_user_id = request.headers.get('X-User-ID') or session.get('user_id')
        
        # If requesting own listings, show all statuses
        # If requesting someone else's listings, show only active ones
        if current_user_id and int(current_user_id) == user_id:
            listings = Listing.query.filter_by(user_id=user_id).order_by(
                Listing.created_at.desc()
            ).all()
        else:
            listings = Listing.query.filter_by(
                user_id=user_id, 
                status='active'
            ).order_by(Listing.created_at.desc()).all()
        
        return jsonify({
            'listings': [listing.to_dict() for listing in listings]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@listing_bp.route('/api/listings/search', methods=['GET'])
def search_listings():
    """Advanced search for listings"""
    try:
        # Get search parameters
        query_text = request.args.get('q', '').strip()
        
        if not query_text:
            return jsonify({'listings': []})
        
        # Search in title, description, resort_name, city, state
        search_filter = db.or_(
            Listing.title.ilike(f'%{query_text}%'),
            Listing.description.ilike(f'%{query_text}%'),
            Listing.resort_name.ilike(f'%{query_text}%'),
            Listing.city.ilike(f'%{query_text}%'),
            Listing.state.ilike(f'%{query_text}%')
        )
        
        listings = Listing.query.filter(
            Listing.status == 'active',
            search_filter
        ).order_by(
            Listing.is_featured.desc(),
            Listing.created_at.desc()
        ).limit(50).all()
        
        return jsonify({
            'listings': [listing.to_dict() for listing in listings],
            'query': query_text,
            'count': len(listings)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

