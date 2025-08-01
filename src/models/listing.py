from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    resort_name = db.Column(db.String(200), nullable=False)
    unit_type = db.Column(db.String(100), nullable=False)
    sleeps = db.Column(db.Integer, nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    
    # Pricing
    sale_price = db.Column(db.Float, nullable=True)
    rental_price_per_night = db.Column(db.Float, nullable=True)
    
    # Listing type
    listing_type = db.Column(db.String(20), nullable=False)  # 'sale', 'rental', or 'both'
    
    # Availability
    available_from = db.Column(db.Date, nullable=True)
    available_to = db.Column(db.Date, nullable=True)
    
    # Images
    image_urls = db.Column(db.Text, nullable=True)  # JSON string of image URLs
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Foreign key to user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('listings', lazy=True))

    def __repr__(self):
        return f'<Listing {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'resort_name': self.resort_name,
            'unit_type': self.unit_type,
            'sleeps': self.sleeps,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'sale_price': self.sale_price,
            'rental_price_per_night': self.rental_price_per_night,
            'listing_type': self.listing_type,
            'available_from': self.available_from.isoformat() if self.available_from else None,
            'available_to': self.available_to.isoformat() if self.available_to else None,
            'image_urls': self.image_urls,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None
        }

