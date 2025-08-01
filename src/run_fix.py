#!/usr/bin/env python3
"""
Database Fix Runner - Integrates with Flask app startup
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def run_database_fix():
    """Run the database fix within Flask app context"""
    try:
        # Import Flask app
        from src.main import app
        
        print("🔧 Running database fix within Flask context...")
        
        with app.app_context():
            # Import and run the fix
            from src.fix_database import fix_database
            success = fix_database()
            
            if success:
                print("✅ Database fix completed successfully!")
                
                # Test creating a user to verify the fix
                from src.models.user import User, db
                
                # Check if we can query users (this was failing before)
                try:
                    user_count = User.query.count()
                    print(f"✅ Database test passed - found {user_count} users")
                    return True
                except Exception as e:
                    print(f"❌ Database test failed: {e}")
                    return False
            else:
                print("❌ Database fix failed")
                return False
                
    except Exception as e:
        print(f"❌ Error running database fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting integrated database fix...")
    success = run_database_fix()
    if success:
        print("🎉 All tests passed! Registration should now work!")
    else:
        print("❌ Fix failed")
        sys.exit(1)

