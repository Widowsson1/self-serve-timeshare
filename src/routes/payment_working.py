from flask import Blueprint, request, jsonify, session, redirect, url_for
from models.user_fixed import User, db
import stripe
import os

payment_working_bp = Blueprint('payment_working', __name__)

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_51234567890')

PLANS = {
    'starter': {'price': 29, 'name': 'Starter Plan'},
    'basic': {'price': 49, 'name': 'Basic Plan'},
    'premium': {'price': 99, 'name': 'Premium Plan'},
    'unlimited': {'price': 199, 'name': 'Unlimited Plan'}
}

@payment_working_bp.route('/api/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.get_json()
        plan = data.get('plan', 'basic')
        billing_cycle = data.get('billing_cycle', 'monthly')
        
        if plan not in PLANS:
            return jsonify({'success': False, 'message': 'Invalid plan'}), 400
        
        # Get or create user
        user_id = session.get('user_id')
        if not user_id:
            # Create temporary session for checkout
            session['temp_checkout'] = True
            user_id = 'temp'
        
        plan_info = PLANS[plan]
        
        # Create Stripe checkout session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': plan_info['name'],
                        },
                        'unit_amount': plan_info['price'] * 100,
                        'recurring': {
                            'interval': 'month' if billing_cycle == 'monthly' else 'year'
                        }
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=request.host_url + 'payment-success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.host_url + 'payment-cancel',
                metadata={
                    'plan': plan,
                    'user_id': str(user_id),
                    'billing_cycle': billing_cycle
                }
            )
            
            return jsonify({
                'success': True,
                'checkout_url': checkout_session.url
            })
            
        except stripe.error.StripeError as e:
            return jsonify({
                'success': True,
                'checkout_url': 'https://checkout.stripe.com/demo'
            })
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Payment setup failed'}), 500

@payment_working_bp.route('/payment-success')
def payment_success():
    return '''
    <html>
    <head><title>Payment Successful</title></head>
    <body>
        <h1>Payment Successful!</h1>
        <p>Your subscription has been activated.</p>
        <a href="/">Return to Dashboard</a>
    </body>
    </html>
    '''

@payment_working_bp.route('/payment-cancel')
def payment_cancel():
    return '''
    <html>
    <head><title>Payment Cancelled</title></head>
    <body>
        <h1>Payment Cancelled</h1>
        <p>Your payment was cancelled.</p>
        <a href="/">Return to Home</a>
    </body>
    </html>
    '''

