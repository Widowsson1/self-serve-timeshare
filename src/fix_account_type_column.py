#!/usr/bin/env python3
"""
Fix script to add missing account_type column to user table
"""

import sqlite3
import os

def fix_account_type_column():
    """Add account_type column to user table if it doesn't exist"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
    
    print(f"🔄 Fixing account_type column in database: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if account_type column exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'account_type' not in columns:
            print("➕ Adding account_type column to user table...")
            
            # Add the account_type column with default value 'subscriber'
            cursor.execute("""
                ALTER TABLE user 
                ADD COLUMN account_type VARCHAR(20) DEFAULT 'subscriber'
            """)
            
            # Update existing users to have 'subscriber' account type
            cursor.execute("""
                UPDATE user 
                SET account_type = 'subscriber' 
                WHERE account_type IS NULL
            """)
            
            conn.commit()
            print("✅ Successfully added account_type column")
        else:
            print("✅ account_type column already exists")
        
        # Verify the fix
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        print(f"📊 Total users in database: {user_count}")
        
        conn.close()
        print("✅ Database fix completed successfully")
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        raise

if __name__ == '__main__':
    fix_account_type_column()

