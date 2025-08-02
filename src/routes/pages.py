from flask import Blueprint, send_from_directory
import os

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/listings')
def listings_page():
    """Serve the listings browse page"""
    static_folder = os.path.join(os.path.dirname(__file__), '..', 'static')
    return send_from_directory(static_folder, 'listings.html')

@pages_bp.route('/listing/<int:listing_id>')
def listing_detail_page(listing_id):
    """Serve the listing detail page"""
    static_folder = os.path.join(os.path.dirname(__file__), '..', 'static')
    return send_from_directory(static_folder, 'listing-detail.html')

@pages_bp.route('/favorites')
def favorites_page():
    """Serve the favorites page"""
    static_folder = os.path.join(os.path.dirname(__file__), '..', 'static')
    return send_from_directory(static_folder, 'favorites.html')

@pages_bp.route('/pricing')
def pricing_page():
    """Serve the pricing page"""
    static_folder = os.path.join(os.path.dirname(__file__), '..', 'static')
    return send_from_directory(static_folder, 'pricing.html')

