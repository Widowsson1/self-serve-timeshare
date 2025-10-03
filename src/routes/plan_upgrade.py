from flask import Blueprint, redirect, session, flash, url_for, request
import stripe
import os

plan_upgrade_bp = Blueprint('plan_upgrade', __name__)

# Set Stripe API key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@plan_upgrade_bp.route('/upgrade/starter')
def upgrade_starter():
    """Direct upgrade to starter plan"""
    return handle_plan_upgrade('starter_monthly', 7.99)

@plan_upgrade_bp.route('/upgrade/basic')
def upgrade_basic():
    """Direct upgrade to basic plan"""
    return handle_plan_upgrade('basic_monthly', 14.99)

@plan_upgrade_bp.route('/upgrade/premium')
def upgrade_premium():
    """Direct upgrade to premium plan"""
    return handle_plan_upgrade('premium_monthly', 24.99)

@plan_upgrade_bp.route('/upgrade/unlimited')
def upgrade_unlimited():
    """Direct upgrade to unlimited plan - bypass auth for testing"""
    try:
        # Create Stripe checkout session directly without auth check
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': 'price_1SDudZEQGduXa1ejpRT2KC6Y',
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'payment/success?session_id={CHECKOUT_SESSION_ID}&upgrade=true',
            cancel_url=request.host_url + 'dashboard',
            metadata={
                'plan_type': 'unlimited_monthly',
                'billing_cycle': 'monthly',
                'is_upgrade': 'true'
            }
        )
        
        # Redirect directly to Stripe checkout
        return redirect(checkout_session.url)
        
    except Exception as e:
        return f"Payment setup failed: {str(e)}"

def handle_plan_upgrade(plan_type, price):
    """Handle plan upgrade with proper authentication check"""
    
    # Check authentication
    user_id = session.get('user_id')
    if not user_id:
        # User not authenticated - redirect to login page
        session['selected_plan'] = plan_type
        session['selected_price'] = price
        return redirect('/login')
    
    try:
        # Define price IDs from Stripe dashboard (TEST MODE)
        price_ids = {
            'starter_monthly': 'price_1SDubcEQGduXa1ejbJzcEG3k',
            'basic_monthly': 'price_1SDucbEQGduXa1ejCrkj08HX',
            'premium_monthly': 'price_1SDud1EQGduXa1ej6bylRcbB',
            'unlimited_monthly': 'price_1SDudZEQGduXa1ejpRT2KC6Y'
        }
        
        if plan_type not in price_ids:
            flash('Invalid plan selected', 'error')
            return redirect(url_for('main.index'))
        
        # Create Stripe checkout session directly
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_ids[plan_type],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'payment/success?session_id={CHECKOUT_SESSION_ID}&upgrade=true',
            cancel_url=request.host_url + 'dashboard',
            client_reference_id=str(user_id),
            metadata={
                'user_id': str(user_id),
                'plan_type': plan_type,
                'billing_cycle': 'monthly',
                'is_upgrade': 'true'
            }
        )
        
        # Redirect directly to Stripe checkout
        return redirect(checkout_session.url)
        
    except Exception as e:
        flash(f'Payment setup failed: {str(e)}', 'error')
        return redirect(url_for('main.index'))
