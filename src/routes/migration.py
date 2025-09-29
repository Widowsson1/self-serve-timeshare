from flask import Blueprint, jsonify
import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

migration_bp = Blueprint('migration', __name__)

@migration_bp.route('/api/migrate-database', methods=['POST'])
def migrate_database():
    """API endpoint to migrate database schema"""
    try:
        # Find database file
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
            db_path = 'database.db'
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if reset_token column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        changes_made = []
        
        if 'reset_token' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN reset_token TEXT")
            changes_made.append('Added reset_token column')
            
        if 'reset_token_expires' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN reset_token_expires DATETIME")
            changes_made.append('Added reset_token_expires column')
        
        # Create test user if it doesn't exist
        cursor.execute("SELECT id FROM user WHERE username = ?", ('testuser',))
        if not cursor.fetchone():
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
            changes_made.append('Created test user')
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Database migration completed',
            'changes': changes_made
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

