"""
Database migration utilities for SelfServe Timeshare
Handles schema updates and migrations automatically
"""

import sqlite3
import os
from flask import current_app

def get_db_path():
    """Get the database file path"""
    return current_app.config.get('DATABASE_PATH', 'database/app.db')

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    db_path = get_db_path()
    
    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        
        conn.close()
        return column_name in columns
    except sqlite3.OperationalError:
        # Table doesn't exist
        return False

def migrate_user_table():
    """Migrate user table to add missing columns"""
    db_path = get_db_path()
    
    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            print("User table doesn't exist, will be created by SQLAlchemy")
            conn.close()
            return
        
        # Check and add missing columns
        migrations_needed = []
        
        # Check for password_hash column
        if not check_column_exists('user', 'password_hash'):
            migrations_needed.append("ALTER TABLE user ADD COLUMN password_hash VARCHAR(255)")
            print("Adding password_hash column to user table")
        
        # Check for other potentially missing columns
        expected_columns = [
            ('first_name', 'VARCHAR(50)'),
            ('last_name', 'VARCHAR(50)'),
            ('phone', 'VARCHAR(20)'),
            ('is_active', 'BOOLEAN DEFAULT 1'),
            ('email_verified', 'BOOLEAN DEFAULT 0'),
            ('created_at', 'DATETIME'),
            ('updated_at', 'DATETIME'),
            ('last_login', 'DATETIME')
        ]
        
        for column_name, column_type in expected_columns:
            if not check_column_exists('user', column_name):
                migrations_needed.append(f"ALTER TABLE user ADD COLUMN {column_name} {column_type}")
                print(f"Adding {column_name} column to user table")
        
        # Execute migrations
        for migration in migrations_needed:
            try:
                cursor.execute(migration)
                print(f"✅ Executed: {migration}")
            except sqlite3.OperationalError as e:
                print(f"⚠️ Migration warning: {e}")
        
        # If we added password_hash, we need to handle existing users
        if any('password_hash' in migration for migration in migrations_needed):
            # Set a default password hash for existing users (they'll need to reset)
            cursor.execute("UPDATE user SET password_hash = 'needs_reset' WHERE password_hash IS NULL")
            print("✅ Set default password_hash for existing users")
        
        conn.commit()
        conn.close()
        print("✅ Database migration completed successfully")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        raise

def run_migrations():
    """Run all necessary database migrations"""
    print("🔄 Starting database migrations...")
    
    try:
        migrate_user_table()
        print("✅ All migrations completed successfully")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

