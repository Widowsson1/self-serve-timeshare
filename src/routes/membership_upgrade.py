from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from src.models.user import User, db
from src.models.membership import Membership
import stripe
import os

membership_upgrade_bp = Blueprint('membership_upgrade', __name__)

# Set Stripe API key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@membership_upgrade_bp.route('/membership')
def membership_page():
    """Display membership management page"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    
    user = User.query.get(user_id)
    if not user:
        return redirect('/login')
    
    # Get current membership
    current_membership = Membership.query.filter_by(
        user_id=user_id, 
        status='active'
    ).first()
    
    current_plan = 'free'
    if current_membership:
        current_plan = current_membership.membership_type
    
    return render_template('membership.html', 
                         user=user, 
                         current_plan=current_plan,
                         current_membership=current_membership)

@membership_upgrade_bp.route('/api/upgrade-membership', methods=['POST'])
def upgrade_membership():
    """Handle membership upgrade requests"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        new_plan = data.get('plan_type')
        billing_cycle = data.get('billing_cycle', 'monthly')
        
        if not new_plan:
            return jsonify({'error': 'Plan type required'}), 400
        
        # Define price IDs
        price_ids = {
            'starter_monthly': 'price_1RrT7TEQGduXa1ejI6QlMX5K',
            'starter_yearly': 'price_1RrT5dEQGduXa1ejOeOK7APR',
            'basic_monthly': 'price_1RrNMgEQGduXa1ejMBFMZ9r2',
            'basic_yearly': 'price_1RrNOaEQGduXa1eja9bkI7XM',
            'premium_monthly': 'price_1RrNQ5EQGduXa1ejvFm1BRZW',
            'premium_yearly': 'price_1RrNQuEQGduXa1ejxTleWdfR',
            'unlimited_monthly': 'price_1RrT8QEQGduXa1ejxd6G9k8C',
            'unlimited_yearly': 'price_1RrT9BEQGduXa1ejdGgdltCw'
        }
        
        price_key = f"{new_plan}_{billing_cycle}"
        
        if price_key not in price_ids:
            return jsonify({'error': 'Invalid plan or billing cycle'}), 400
        
        # Get current membership
        current_membership = Membership.query.filter_by(
            user_id=user_id, 
            status='active'
        ).first()
        
        current_plan = 'free'
        if current_membership:
            current_plan = current_membership.membership_type
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_ids[price_key],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + f'membership/success?session_id={{CHECKOUT_SESSION_ID}}&upgrade=true&from_plan={current_plan}',
            cancel_url=request.host_url + 'membership?cancelled=true',
            client_reference_id=str(user_id),
            metadata={
                'user_id': str(user_id),
                'plan_type': new_plan,
                'billing_cycle': billing_cycle,
                'is_upgrade': 'true',
                'current_plan': current_plan
            }
        )
        
        return jsonify({'checkout_url': checkout_session.url})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@membership_upgrade_bp.route('/membership/success')
def upgrade_success():
    """Handle successful membership upgrade"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        return redirect('/membership?error=invalid_session')
    
    try:
        # Retrieve the checkout session
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        if checkout_session.payment_status == 'paid':
            user_id = int(checkout_session.metadata['user_id'])
            plan_type = checkout_session.metadata['plan_type']
            billing_cycle = checkout_session.metadata['billing_cycle']
            
            # Cancel existing membership
            existing_membership = Membership.query.filter_by(
                user_id=user_id, 
                status='active'
            ).first()
            
            if existing_membership:
                existing_membership.status = 'cancelled'
            
            # Create new membership
            new_membership = Membership(
                user_id=user_id,
                membership_type=f"{plan_type}_{billing_cycle}",
                status='active',
                payment_amount=checkout_session.amount_total / 100,  # Convert from cents
                payment_method='stripe',
                transaction_id=checkout_session.payment_intent
            )
            
            db.session.add(new_membership)
            db.session.commit()
            
            return render_template('upgrade_success.html', 
                                 plan_type=plan_type,
                                 billing_cycle=billing_cycle)
        
        return redirect('/membership?error=payment_failed')
        
    except Exception as e:
        return redirect(f'/membership?error={str(e)}')

@membership_upgrade_bp.route('/api/current-membership')
def get_current_membership():
    """Get current user's membership details"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        membership = Membership.query.filter_by(
            user_id=user_id, 
            status='active'
        ).first()
        
        if not membership:
            return jsonify({
                'plan': 'free',
                'status': 'none',
                'features': ['Browse listings', 'Contact owners']
            })
        
        return jsonify({
            'plan': membership.membership_type,
            'status': membership.status,
            'payment_amount': membership.payment_amount,
            'created_at': membership.created_at.isoformat(),
            'is_active': membership.is_active()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
