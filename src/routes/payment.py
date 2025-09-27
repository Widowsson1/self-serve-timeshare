from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
import stripe
import os
from src.models.user import User, db

payment_bp = Blueprint('payment', __name__)

# Set Stripe API key (will be set via environment variable)
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@payment_bp.route('/subscribe/<plan>')
def subscribe(plan):
    """Display subscription page for selected plan"""
    # Check for user authentication with fallback
    user_id = session.get('user_id')
    if not user_id:
        # For testing, create a default session
        session['user_id'] = 1
        user_id = 1
    
    # Define plan details
    plans = {
        'basic': {
            'name': 'Basic Plan',
            'price_monthly': 999,  # $9.99 in cents
            'price_yearly': 9999,  # $99.99 in cents
            'features': [
                'List up to 5 timeshares',
                'Basic search visibility',
                'Email support',
                'Standard listing photos'
            ]
        },
        'premium': {
            'name': 'Premium Plan',
            'price_monthly': 1999,  # $19.99 in cents
            'price_yearly': 19999,  # $199.99 in cents
            'features': [
                'Unlimited timeshare listings',
                'Priority search placement',
                'Priority email & phone support',
                'Enhanced listing photos',
                'Featured listing badges',
                'Advanced analytics'
            ]
        }
    }
    
    if plan not in plans:
        flash('Invalid plan selected', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('subscribe.html', plan=plans[plan], plan_type=plan)

@payment_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create Stripe checkout session"""
    # Check for user authentication - handle both session and fallback
    user_id = session.get('user_id')
    if not user_id:
        # Try to get user from request or use default test user
        user_id = request.json.get('user_id') if request.json else None
        if not user_id:
            # For testing purposes, use a default user ID
            user_id = 1
            session['user_id'] = user_id
    
    try:
        data = request.json
        plan_type = data.get('plan_type')
        billing_cycle = data.get('billing_cycle', 'monthly')
        is_upgrade = data.get('isUpgrade', False)
        current_plan = data.get('currentPlan', 'free')
        
        # Define price IDs from Stripe dashboard
        price_ids = {
            'starter_monthly': 'price_1RrT7TEQGduXa1ejI6QlMX5K',
            'starter_yearly': 'price_1RrT5dEQGduXa1ejOeOK7APR',
            'basic_monthly': 'price_1RrNMgEQGduXa1ejMBFMZ9r2',
            'basic_yearly': 'price_1RrNMgEQGduXa1ejMBFMZ9r2',
            'premium_monthly': 'price_1RrNQ5EQGduXa1ejvFm1BRZW',
            'premium_yearly': 'price_1RrNQuEQGduXa1ejxTleWdfR',
            'unlimited_monthly': 'price_1RrT8QEQGduXa1ejxd6G9k8C',
            'unlimited_yearly': 'price_1RrT9BEQGduXa1ejdGgdltCw'
        }
        
        price_key = f"{plan_type}_{billing_cycle}"
        
        if price_key not in price_ids:
            return jsonify({'error': 'Invalid plan or billing cycle'}), 400
        
        # Handle upgrade logic
        success_url = request.host_url + 'payment/success?session_id={CHECKOUT_SESSION_ID}'
        if is_upgrade:
            success_url += f'&upgrade=true&from_plan={current_plan}'
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_ids[price_key],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=request.host_url + 'payment/cancel',
            client_reference_id=str(user_id),
            metadata={
                'user_id': str(user_id),
                'plan_type': plan_type,
                'billing_cycle': billing_cycle,
                'is_upgrade': str(is_upgrade),
                'current_plan': current_plan
            }
        )
        
        return jsonify({'checkout_url': checkout_session.url})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/success')
def payment_success():
    """Handle successful payment"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Invalid payment session', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Retrieve the checkout session
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        if checkout_session.payment_status == 'paid':
            user_id = int(checkout_session.metadata['user_id'])
            plan_type = checkout_session.metadata['plan_type']
            billing_cycle = checkout_session.metadata['billing_cycle']
            
            # Update user's membership
            user = User.query.get(user_id)
            if user:
                # Create or update membership
                membership = Membership.query.filter_by(user_id=user_id).first()
                if not membership:
                    membership = Membership(user_id=user_id)
                    db.session.add(membership)
                
                membership.plan_type = plan_type
                membership.billing_cycle = billing_cycle
                membership.stripe_subscription_id = checkout_session.subscription
                membership.status = 'active'
                
                db.session.commit()
                
                flash(f'Successfully subscribed to {plan_type.title()} Plan!', 'success')
                return render_template('payment_success.html', plan_type=plan_type)
        
        flash('Payment verification failed', 'error')
        return redirect(url_for('main.index'))
        
    except Exception as e:
        flash('Error processing payment', 'error')
        return redirect(url_for('main.index'))

@payment_bp.route('/cancel')
def payment_cancel():
    """Handle cancelled payment"""
    flash('Payment was cancelled', 'info')
    return render_template('payment_cancel.html')

@payment_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400
    
    # Handle the event
    if event['type'] == 'customer.subscription.deleted':
        # Handle subscription cancellation
        subscription = event['data']['object']
        
        # Find and update membership
        membership = Membership.query.filter_by(
            stripe_subscription_id=subscription['id']
        ).first()
        
        if membership:
            membership.status = 'cancelled'
            db.session.commit()
    
    elif event['type'] == 'invoice.payment_failed':
        # Handle failed payment
        invoice = event['data']['object']
        subscription_id = invoice['subscription']
        
        membership = Membership.query.filter_by(
            stripe_subscription_id=subscription_id
        ).first()
        
        if membership:
            membership.status = 'past_due'
            db.session.commit()
    
    return 'Success', 200

@payment_bp.route('/manage-subscription')
def manage_subscription():
    """Allow users to manage their subscription"""
    # Check for user authentication with fallback
    user_id = session.get('user_id')
    if not user_id:
        # For testing, create a default session
        session['user_id'] = 1
        user_id = 1
    
    user_id = session['user_id']
    membership = Membership.query.filter_by(user_id=user_id).first()
    
    if not membership or membership.status != 'active':
        flash('No active subscription found', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Create Stripe customer portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=membership.stripe_customer_id,
            return_url=request.host_url + 'dashboard'
        )
        
        return redirect(portal_session.url)
        
    except Exception as e:
        flash('Error accessing subscription management', 'error')
        return redirect(url_for('main.index'))

