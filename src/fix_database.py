#!/usr/bin/env python3
"""
Manual Database Fix Script for SelfServe Timeshare
This script directly fixes the database schema by adding the missing password_hash column
"""

import sqlite3
import os
import sys

def fix_database():
    """Fix the database schema by adding missing columns"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
    
    print(f"🔧 Fixing database at: {db_path}")
    
    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        
        # Check if user table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():
            print("❌ User table doesn't exist - creating it")
            # Create the user table with correct schema
            cursor.execute("""
                CREATE TABLE user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    phone VARCHAR(20),
                    is_active BOOLEAN DEFAULT 1,
                    email_verified BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME
                )
            """)
            print("✅ Created user table with correct schema")
        else:
            print("✅ User table exists")
            
            # Check if password_hash column exists
            cursor.execute("PRAGMA table_info(user)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'password_hash' not in columns:
                print("🔧 Adding missing password_hash column")
                cursor.execute("ALTER TABLE user ADD COLUMN password_hash VARCHAR(255)")
                print("✅ Added password_hash column")
            else:
                print("✅ password_hash column already exists")
            
            # Check and add other missing columns
            missing_columns = []
            expected_columns = {
                'first_name': 'VARCHAR(50)',
                'last_name': 'VARCHAR(50)', 
                'phone': 'VARCHAR(20)',
                'is_active': 'BOOLEAN DEFAULT 1',
                'email_verified': 'BOOLEAN DEFAULT 0',
                'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
                'last_login': 'DATETIME'
            }
            
            for col_name, col_type in expected_columns.items():
                if col_name not in columns:
                    missing_columns.append((col_name, col_type))
            
            for col_name, col_type in missing_columns:
                print(f"🔧 Adding missing {col_name} column")
                cursor.execute(f"ALTER TABLE user ADD COLUMN {col_name} {col_type}")
                print(f"✅ Added {col_name} column")
        
        # Commit changes
        conn.commit()
        print("✅ Database changes committed")
        
        # Verify the fix
        cursor.execute("PRAGMA table_info(user)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"✅ Current user table columns: {', '.join(columns)}")
        
        if 'password_hash' in columns:
            print("🎉 SUCCESS! password_hash column is now present")
        else:
            print("❌ FAILED! password_hash column still missing")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting manual database fix...")
    success = fix_database()
    if success:
        print("🎉 Database fix completed successfully!")
        print("💡 The registration should now work without 500 errors")
    else:
        print("❌ Database fix failed")
        sys.exit(1)

