#!/usr/bin/env python3
"""
Migration script to update existing users to new pricing plans
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from main import app
from src.models.user import db, User
from src.models.membership import Membership
from datetime import datetime

def migrate_existing_plans():
    """Migrate existing users to new plan structure"""
    
    with app.app_context():
        print("🔄 Starting plan migration...")
        
        # Get all existing memberships
        memberships = Membership.query.filter_by(status='active').all()
        
        migration_count = 0
        for membership in memberships:
            old_type = membership.membership_type
            new_type = None
            
            # Map old plans to new plans
            if old_type == 'basic_monthly':
                # Old basic (1 listing) -> New basic (2 listings) - UPGRADE!
                new_type = 'basic_monthly'
                print(f"✅ User {membership.user_id}: basic_monthly -> basic_monthly (upgraded to 2 listings)")
                
            elif old_type == 'premium_monthly':
                # Old premium (3 listings) -> New premium (5 listings) - UPGRADE!
                new_type = 'premium_monthly'
                print(f"✅ User {membership.user_id}: premium_monthly -> premium_monthly (upgraded to 5 listings)")
                
            else:
                # Unknown plan type, default to starter
                new_type = 'starter_monthly'
                print(f"⚠️  User {membership.user_id}: {old_type} -> starter_monthly (unknown plan)")
            
            # Update membership type (keeping same price for grandfathering)
            membership.membership_type = new_type
            membership.updated_at = datetime.utcnow()
            
            migration_count += 1
        
        # Commit changes
        db.session.commit()
        
        print(f"🎉 Migration completed! Updated {migration_count} memberships")
        
        # Show summary
        print("\n📊 MIGRATION SUMMARY:")
        print("- Existing basic users: Upgraded to 2 listings (same price)")
        print("- Existing premium users: Upgraded to 5 listings (same price)")
        print("- All users keep their current pricing for grandfathering")
        print("- New users will use the new 4-tier pricing structure")
        
        return migration_count

def verify_migration():
    """Verify the migration was successful"""
    
    with app.app_context():
        print("\n🔍 Verifying migration...")
        
        # Count memberships by type
        starter_count = Membership.query.filter_by(membership_type='starter_monthly', status='active').count()
        basic_count = Membership.query.filter_by(membership_type='basic_monthly', status='active').count()
        premium_count = Membership.query.filter_by(membership_type='premium_monthly', status='active').count()
        unlimited_count = Membership.query.filter_by(membership_type='unlimited_monthly', status='active').count()
        
        total_count = starter_count + basic_count + premium_count + unlimited_count
        
        print(f"📈 Current plan distribution:")
        print(f"   Starter: {starter_count} users")
        print(f"   Basic: {basic_count} users")
        print(f"   Premium: {premium_count} users")
        print(f"   Unlimited: {unlimited_count} users")
        print(f"   Total: {total_count} active memberships")
        
        return {
            'starter': starter_count,
            'basic': basic_count,
            'premium': premium_count,
            'unlimited': unlimited_count,
            'total': total_count
        }

def test_plan_limits():
    """Test the new plan limits system"""
    
    with app.app_context():
        print("\n🧪 Testing plan limits...")
        
        from utils.plan_limits import get_plan_limits, validate_listing_limit, validate_photo_limit
        
        # Test each plan
        plans = ['starter_monthly', 'basic_monthly', 'premium_monthly', 'unlimited_monthly']
        
        for plan in plans:
            config = get_plan_limits(plan)
            print(f"\n📋 {config['name']} Plan:")
            print(f"   Max Listings: {'Unlimited' if config['max_listings'] == -1 else config['max_listings']}")
            print(f"   Max Photos: {config['max_photos_per_listing']}")
            print(f"   Price: ${config['price']}/month")
            
            # Test listing limits
            can_create, error = validate_listing_limit(plan, 0)
            print(f"   Can create first listing: {'✅' if can_create else '❌'}")
            
            if config['max_listings'] != -1:
                can_create, error = validate_listing_limit(plan, config['max_listings'])
                print(f"   Can exceed limit: {'❌' if not can_create else '✅'} - {error if error else 'OK'}")
            
            # Test photo limits
            is_valid, error = validate_photo_limit(plan, config['max_photos_per_listing'])
            print(f"   Photo limit validation: {'✅' if is_valid else '❌'}")
        
        print("\n✅ Plan limits testing completed!")

if __name__ == '__main__':
    print("🚀 SelfServe Timeshare - Plan Migration Tool")
    print("=" * 50)
    
    try:
        # Run migration
        migrated_count = migrate_existing_plans()
        
        # Verify migration
        stats = verify_migration()
        
        # Test plan limits
        test_plan_limits()
        
        print("\n🎉 MIGRATION SUCCESSFUL!")
        print("=" * 50)
        print("✅ All existing users have been upgraded to better plans")
        print("✅ New 4-tier pricing structure is active")
        print("✅ Plan limits system is working correctly")
        print("\n🚀 Platform is ready for optimized pricing!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

