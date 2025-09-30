from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from decimal import Decimal
from models.user_fixed import db

class Listing(db.Model):
    __tablename__ = 'listing'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Basic Property Information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    property_type = db.Column(db.String(50), nullable=False)  # 'sale', 'rental', 'both'
    
    # Location Information
    resort_name = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(20), nullable=True)
    
    # Property Details
    bedrooms = db.Column(db.Integer, nullable=True)
    bathrooms = db.Column(db.Float, nullable=True)
    sleeps = db.Column(db.Integer, nullable=True)
    unit_size = db.Column(db.String(50), nullable=True)  # e.g., "1200 sq ft"
    floor = db.Column(db.String(20), nullable=True)
    view_type = db.Column(db.String(100), nullable=True)  # e.g., "Ocean View", "Mountain View"
    
    # Ownership Details
    ownership_type = db.Column(db.String(50), nullable=True)  # 'deeded', 'right_to_use', 'points'
    week_number = db.Column(db.String(20), nullable=True)
    season = db.Column(db.String(20), nullable=True)  # 'red', 'white', 'blue', 'gold', etc.
    usage_type = db.Column(db.String(20), nullable=True)  # 'annual', 'biennial_odd', 'biennial_even'
    
    # Pricing Information
    sale_price = db.Column(db.Numeric(10, 2), nullable=True)
    rental_price_weekly = db.Column(db.Numeric(10, 2), nullable=True)
    rental_price_nightly = db.Column(db.Numeric(10, 2), nullable=True)
    maintenance_fee = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Availability
    available_dates = db.Column(db.Text, nullable=True)  # JSON string of available date ranges
    check_in_day = db.Column(db.String(20), nullable=True)  # e.g., "Saturday", "Sunday"
    
    # Amenities (stored as JSON string)
    amenities = db.Column(db.Text, nullable=True)  # JSON array of amenities
    
    # Contact Information
    contact_method = db.Column(db.String(20), default='email')  # 'email', 'phone', 'both'
    contact_phone = db.Column(db.String(20), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    
    # Listing Status and Management
    status = db.Column(db.String(20), default='active')  # 'active', 'inactive', 'sold', 'rented'
    is_featured = db.Column(db.Boolean, default=False)
    featured_until = db.Column(db.DateTime, nullable=True)
    
    # Photo Management
    photo_count = db.Column(db.Integer, default=0)
    main_photo_url = db.Column(db.String(500), nullable=True)
    
    # Statistics
    view_count = db.Column(db.Integer, default=0)
    inquiry_count = db.Column(db.Integer, default=0)
    favorite_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_viewed = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('listings', lazy=True))
    photos = db.relationship('ListingPhoto', backref='listing', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='listing', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Listing {self.title}>'

    def increment_view_count(self):
        """Increment the view count for this listing"""
        self.view_count += 1
        self.last_viewed = datetime.utcnow()
        db.session.commit()

    def increment_inquiry_count(self):
        """Increment the inquiry count for this listing"""
        self.inquiry_count += 1
        db.session.commit()

    def is_available_for_dates(self, start_date, end_date):
        """Check if listing is available for given date range"""
        # This would implement date availability logic
        # For now, return True if listing is active
        return self.status == 'active'

    def get_price_display(self):
        """Get formatted price display string"""
        prices = []
        if self.sale_price and self.property_type in ['sale', 'both']:
            prices.append(f"Sale: ${self.sale_price:,.0f}")
        if self.rental_price_weekly and self.property_type in ['rental', 'both']:
            prices.append(f"Rental: ${self.rental_price_weekly:,.0f}/week")
        return " | ".join(prices) if prices else "Contact for pricing"

    def get_location_display(self):
        """Get formatted location display string"""
        return f"{self.city}, {self.state}, {self.country}"

    def to_dict(self, include_user=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'property_type': self.property_type,
            'resort_name': self.resort_name,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'zip_code': self.zip_code,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'sleeps': self.sleeps,
            'unit_size': self.unit_size,
            'floor': self.floor,
            'view_type': self.view_type,
            'ownership_type': self.ownership_type,
            'week_number': self.week_number,
            'season': self.season,
            'usage_type': self.usage_type,
            'sale_price': float(self.sale_price) if self.sale_price else None,
            'rental_price_weekly': float(self.rental_price_weekly) if self.rental_price_weekly else None,
            'rental_price_nightly': float(self.rental_price_nightly) if self.rental_price_nightly else None,
            'maintenance_fee': float(self.maintenance_fee) if self.maintenance_fee else None,
            'available_dates': self.available_dates,
            'check_in_day': self.check_in_day,
            'amenities': self.amenities,
            'contact_method': self.contact_method,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'status': self.status,
            'is_featured': self.is_featured,
            'featured_until': self.featured_until.isoformat() if self.featured_until else None,
            'photo_count': self.photo_count,
            'main_photo_url': self.main_photo_url,
            'view_count': self.view_count,
            'inquiry_count': self.inquiry_count,
            'favorite_count': self.favorite_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_viewed': self.last_viewed.isoformat() if self.last_viewed else None,
            'price_display': self.get_price_display(),
            'location_display': self.get_location_display()
        }
        
        if include_user:
            data['user'] = self.user.to_dict()
            
        return data


class ListingPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    
    # Photo Information
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    
    # Photo Properties
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    caption = db.Column(db.String(255), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    is_main = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ListingPhoto {self.filename}>'

    def to_dict(self):
        return {
            'id': self.id,
            'listing_id': self.listing_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'width': self.width,
            'height': self.height,
            'caption': self.caption,
            'sort_order': self.sort_order,
            'is_main': self.is_main,
            'created_at': self.created_at.isoformat()
        }


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    
    # Favorite Properties
    notes = db.Column(db.Text, nullable=True)  # User's private notes about this listing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('favorites', lazy=True))
    
    # Unique constraint to prevent duplicate favorites
    __table_args__ = (db.UniqueConstraint('user_id', 'listing_id', name='unique_user_listing_favorite'),)

    def __repr__(self):
        return f'<Favorite User:{self.user_id} Listing:{self.listing_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'listing_id': self.listing_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'listing': self.listing.to_dict() if self.listing else None
        }

