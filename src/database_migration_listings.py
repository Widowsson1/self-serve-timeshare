#!/usr/bin/env python3
"""
Database Migration Script for Timeshare Listings
Adds listing, listing_photo, and favorite tables to the database
"""

import sqlite3
import os
from datetime import datetime

def run_listings_migration():
    """Run the database migration to add listing-related tables"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    print(f"🔄 Starting listings database migration...")
    print(f"📍 Database path: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Add account_type column to user table if it doesn't exist
        print("🔧 Adding account_type column to user table...")
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN account_type VARCHAR(20) DEFAULT 'subscriber'")
            print("✅ Added account_type column to user table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("✅ account_type column already exists in user table")
            else:
                raise e
        
        # 2. Create listing table
        print("🔧 Creating listing table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                property_type VARCHAR(50) NOT NULL,
                resort_name VARCHAR(200) NOT NULL,
                city VARCHAR(100) NOT NULL,
                state VARCHAR(50) NOT NULL,
                country VARCHAR(50) NOT NULL,
                zip_code VARCHAR(20),
                bedrooms INTEGER,
                bathrooms REAL,
                sleeps INTEGER,
                unit_size VARCHAR(50),
                floor VARCHAR(20),
                view_type VARCHAR(100),
                ownership_type VARCHAR(50),
                week_number VARCHAR(20),
                season VARCHAR(20),
                usage_type VARCHAR(20),
                sale_price DECIMAL(10, 2),
                rental_price_weekly DECIMAL(10, 2),
                rental_price_nightly DECIMAL(10, 2),
                maintenance_fee DECIMAL(10, 2),
                available_dates TEXT,
                check_in_day VARCHAR(20),
                amenities TEXT,
                contact_method VARCHAR(20) DEFAULT 'email',
                contact_phone VARCHAR(20),
                contact_email VARCHAR(120),
                status VARCHAR(20) DEFAULT 'active',
                is_featured BOOLEAN DEFAULT 0,
                featured_until DATETIME,
                photo_count INTEGER DEFAULT 0,
                main_photo_url VARCHAR(500),
                view_count INTEGER DEFAULT 0,
                inquiry_count INTEGER DEFAULT 0,
                favorite_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_viewed DATETIME,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        ''')
        print("✅ Created listing table")
        
        # 3. Create listing_photo table
        print("🔧 Creating listing_photo table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listing_photo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id INTEGER NOT NULL,
                filename VARCHAR(255) NOT NULL,
                original_filename VARCHAR(255),
                file_path VARCHAR(500) NOT NULL,
                file_size INTEGER,
                width INTEGER,
                height INTEGER,
                caption VARCHAR(255),
                sort_order INTEGER DEFAULT 0,
                is_main BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (listing_id) REFERENCES listing (id) ON DELETE CASCADE
            )
        ''')
        print("✅ Created listing_photo table")
        
        # 4. Create favorite table
        print("🔧 Creating favorite table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorite (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                listing_id INTEGER NOT NULL,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (listing_id) REFERENCES listing (id) ON DELETE CASCADE,
                UNIQUE(user_id, listing_id)
            )
        ''')
        print("✅ Created favorite table")
        
        # 5. Create indexes for better performance
        print("🔧 Creating database indexes...")
        
        # Listing indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_listing_user_id ON listing(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_listing_status ON listing(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_listing_property_type ON listing(property_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_listing_city_state ON listing(city, state)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_listing_created_at ON listing(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_listing_is_featured ON listing(is_featured)')
        
        # Photo indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_listing_photo_listing_id ON listing_photo(listing_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_listing_photo_is_main ON listing_photo(is_main)')
        
        # Favorite indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_favorite_user_id ON favorite(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_favorite_listing_id ON favorite(listing_id)')
        
        print("✅ Created database indexes")
        
        # Commit all changes
        conn.commit()
        
        # 6. Verify tables were created
        print("🔍 Verifying table creation...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['listing', 'listing_photo', 'favorite']
        for table in required_tables:
            if table in tables:
                print(f"✅ Table '{table}' exists")
            else:
                print(f"❌ Table '{table}' missing")
        
        # 7. Show table counts
        print("📊 Current table counts:")
        for table in ['user', 'membership', 'listing', 'listing_photo', 'favorite']:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   {table}: {count} records")
        
        conn.close()
        print("✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database migration failed: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 Running Timeshare Listings Database Migration")
    print("=" * 50)
    success = run_listings_migration()
    if success:
        print("🎉 Migration completed successfully!")
    else:
        print("💥 Migration failed!")
        exit(1)

