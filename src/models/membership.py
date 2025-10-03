from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from models.user import db

class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    membership_type = db.Column(db.String(50), nullable=False)  # 'basic', 'premium', etc.
    status = db.Column(db.String(20), nullable=False, default='active')  # 'active', 'expired', 'cancelled'
    
    # Payment details
    payment_amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), nullable=True)
    transaction_id = db.Column(db.String(100), nullable=True)
    
    # Membership period
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('memberships', lazy=True))

    def __repr__(self):
        return f'<Membership {self.user_id} - {self.membership_type}>'

    def is_active(self):
        """Check if membership is currently active"""
        if self.status != 'active':
            return False
        if self.end_date and self.end_date < datetime.utcnow():
            return False
        return True

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'membership_type': self.membership_type,
            'status': self.status,
            'payment_amount': self.payment_amount,
            'payment_date': self.payment_date.isoformat(),
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active()
        }

