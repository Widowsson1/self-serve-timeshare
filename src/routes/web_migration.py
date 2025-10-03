from flask import Blueprint, jsonify, request
import sqlite3
import os
from models.user import db

web_migration_bp = Blueprint('web_migration', __name__)

@web_migration_bp.route('/admin/migrate-database', methods=['GET', 'POST'])
def migrate_database_web():
    """Web-accessible database migration endpoint"""
    try:
        # Get database path from app config
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'app.db')
        
        if not os.path.exists(db_path):
            return jsonify({
                'error': 'Database file not found',
                'path_checked': db_path
            }), 404
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrations_applied = []
        
        # Add reset_token column if missing
        if 'reset_token' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN reset_token TEXT")
            migrations_applied.append('Added reset_token column')
        
        # Add reset_token_expires column if missing
        if 'reset_token_expires' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN reset_token_expires DATETIME")
            migrations_applied.append('Added reset_token_expires column')
        
        conn.commit()
        
        # Verify final schema
        cursor.execute("PRAGMA table_info(user)")
        final_columns = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'migrations_applied': migrations_applied,
            'final_schema': [{'name': col[1], 'type': col[2]} for col in final_columns],
            'database_path': db_path
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@web_migration_bp.route('/admin/check-database', methods=['GET'])
def check_database():
    """Check database schema status"""
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'app.db')
        
        if not os.path.exists(db_path):
            return jsonify({
                'error': 'Database file not found',
                'path_checked': db_path
            }), 404
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get user table schema
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        
        # Check for required columns
        column_names = [col[1] for col in columns]
        required_columns = ['reset_token', 'reset_token_expires']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        conn.close()
        
        return jsonify({
            'database_path': db_path,
            'user_table_columns': [{'name': col[1], 'type': col[2]} for col in columns],
            'missing_columns': missing_columns,
            'migration_needed': len(missing_columns) > 0
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
