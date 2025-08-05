from flask import Blueprint, send_from_directory
import os

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/faq.html')
def faq():
    return send_from_directory('static', 'faq.html')

@pages_bp.route('/chatbot.js')
def chatbot_js():
    return send_from_directory('static', 'chatbot.js', mimetype='application/javascript')

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


@pages_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create Stripe checkout session for subscription payment"""
    from flask import request, jsonify
    
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        plan_type = data.get('plan_type')
        price = data.get('price')
        
        # For now, return a placeholder response
        # TODO: Implement actual Stripe integration
        return jsonify({
            'error': 'Stripe integration not yet configured. Please contact support to complete your subscription.',
            'message': f'Plan: {plan_type} (${price}/month) for user {user_id}'
        }), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

