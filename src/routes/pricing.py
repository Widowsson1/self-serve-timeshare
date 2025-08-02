from flask import Blueprint, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.plan_limits import get_all_plans, get_plan_limits

pricing_bp = Blueprint('pricing', __name__)

@pricing_bp.route('/api/pricing/plans', methods=['GET'])
def get_pricing_plans():
    """Get all available pricing plans"""
    try:
        plans = get_all_plans()
        
        # Format plans for frontend consumption
        formatted_plans = []
        for plan_id, plan_config in plans.items():
            formatted_plan = {
                'id': plan_id,
                'name': plan_config['name'],
                'price': plan_config['price'],
                'max_listings': plan_config['max_listings'],
                'max_photos_per_listing': plan_config['max_photos_per_listing'],
                'features': plan_config['features'],
                'is_unlimited': plan_config['max_listings'] == -1,
                'display_listings': 'Unlimited' if plan_config['max_listings'] == -1 else str(plan_config['max_listings']),
                'popular': plan_id == 'basic_monthly',  # Mark basic as popular
                'recommended': plan_id == 'premium_monthly'  # Mark premium as recommended
            }
            formatted_plans.append(formatted_plan)
        
        # Sort plans by price
        formatted_plans.sort(key=lambda x: x['price'])
        
        return jsonify({
            'plans': formatted_plans,
            'currency': 'USD',
            'billing_cycle': 'monthly'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pricing_bp.route('/api/pricing/plan/<plan_id>', methods=['GET'])
def get_plan_details(plan_id):
    """Get details for a specific plan"""
    try:
        plan_config = get_plan_limits(plan_id)
        
        if not plan_config:
            return jsonify({'error': 'Plan not found'}), 404
        
        formatted_plan = {
            'id': plan_id,
            'name': plan_config['name'],
            'price': plan_config['price'],
            'max_listings': plan_config['max_listings'],
            'max_photos_per_listing': plan_config['max_photos_per_listing'],
            'features': plan_config['features'],
            'is_unlimited': plan_config['max_listings'] == -1,
            'display_listings': 'Unlimited' if plan_config['max_listings'] == -1 else str(plan_config['max_listings'])
        }
        
        return jsonify(formatted_plan)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pricing_bp.route('/api/pricing/compare', methods=['GET'])
def compare_plans():
    """Get plan comparison data"""
    try:
        plans = get_all_plans()
        
        comparison_data = {
            'features': [
                {
                    'name': 'Active Listings',
                    'starter_monthly': '1 listing',
                    'basic_monthly': '2 listings',
                    'premium_monthly': '5 listings',
                    'unlimited_monthly': 'Unlimited'
                },
                {
                    'name': 'Photos per Listing',
                    'starter_monthly': '6 photos',
                    'basic_monthly': '10 photos',
                    'premium_monthly': '20 photos',
                    'unlimited_monthly': '30 photos'
                },
                {
                    'name': 'Listing Analytics',
                    'starter_monthly': 'Basic',
                    'basic_monthly': 'Advanced',
                    'premium_monthly': 'Premium',
                    'unlimited_monthly': 'Premium + Insights'
                },
                {
                    'name': 'Support',
                    'starter_monthly': 'Email',
                    'basic_monthly': 'Priority Email',
                    'premium_monthly': 'Phone & Email',
                    'unlimited_monthly': 'Priority Phone & Email'
                },
                {
                    'name': 'Featured Listings',
                    'starter_monthly': '❌',
                    'basic_monthly': 'Optional',
                    'premium_monthly': '✅ Included',
                    'unlimited_monthly': '✅ Included'
                },
                {
                    'name': 'Search Placement',
                    'starter_monthly': 'Standard',
                    'basic_monthly': 'Standard',
                    'premium_monthly': 'Advanced',
                    'unlimited_monthly': 'Top Priority'
                },
                {
                    'name': 'Bulk Tools',
                    'starter_monthly': '❌',
                    'basic_monthly': '❌',
                    'premium_monthly': '❌',
                    'unlimited_monthly': '✅'
                },
                {
                    'name': 'API Access',
                    'starter_monthly': '❌',
                    'basic_monthly': '❌',
                    'premium_monthly': '❌',
                    'unlimited_monthly': '✅'
                }
            ],
            'plans': []
        }
        
        # Add plan headers
        for plan_id, plan_config in plans.items():
            comparison_data['plans'].append({
                'id': plan_id,
                'name': plan_config['name'],
                'price': plan_config['price']
            })
        
        # Sort plans by price
        comparison_data['plans'].sort(key=lambda x: x['price'])
        
        return jsonify(comparison_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

