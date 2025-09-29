#!/usr/bin/env python3
"""
Database migration script to add password reset functionality
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add password reset columns to user table"""
    
    # Database path (adjust as needed for your deployment)
    db_paths = [
        'database.db',
        'src/database.db',
        '/tmp/database.db',
        'instance/database.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("Database file not found. Creating new database...")
        db_path = 'database.db'
    
    print(f"Using database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if reset_token column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'reset_token' not in columns:
            print("Adding reset_token column...")
            cursor.execute("ALTER TABLE user ADD COLUMN reset_token TEXT")
            
        if 'reset_token_expires' not in columns:
            print("Adding reset_token_expires column...")
            cursor.execute("ALTER TABLE user ADD COLUMN reset_token_expires DATETIME")
        
        conn.commit()
        print("Database migration completed successfully!")
        
        # Verify the columns were added
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        print("\nCurrent user table schema:")
        for column in columns:
            print(f"  {column[1]} ({column[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"Migration error: {str(e)}")
        return False
    
    return True

def create_test_user():
    """Create a test user for testing purposes"""
    try:
        from werkzeug.security import generate_password_hash
        
        db_path = 'database.db'
        if not os.path.exists(db_path):
            db_path = 'src/database.db'
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if testuser already exists
        cursor.execute("SELECT id FROM user WHERE username = ?", ('testuser',))
        if cursor.fetchone():
            print("Test user already exists")
            conn.close()
            return
        
        # Create test user
        password_hash = generate_password_hash('password123')
        cursor.execute("""
            INSERT INTO user (username, email, password_hash, first_name, last_name, 
                            is_active, email_verified, account_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'testuser',
            'test@example.com', 
            password_hash,
            'Test',
            'User',
            1,  # is_active
            1,  # email_verified
            'subscriber',
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
        print("Test user created successfully!")
        
    except Exception as e:
        print(f"Error creating test user: {str(e)}")

if __name__ == "__main__":
    print("Starting database migration...")
    if migrate_database():
        print("\nCreating test user...")
        create_test_user()
        print("\nMigration completed!")
    else:
        print("Migration failed!")

