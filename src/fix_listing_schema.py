#!/usr/bin/env python3
"""
Fix listing table schema to match the model definition
"""

import sqlite3
import os

def fix_listing_schema():
    """Drop and recreate listing table with correct schema"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
    print(f"🔧 Fixing listing table schema...")
    print(f"📍 Database path: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Drop existing listing table
        print("🗑️ Dropping existing listing table...")
        cursor.execute("DROP TABLE IF EXISTS listing")
        
        # Create new listing table with correct schema
        print("🔧 Creating new listing table with correct schema...")
        cursor.execute('''
            CREATE TABLE listing (
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
                bathrooms FLOAT,
                sleeps INTEGER,
                unit_size VARCHAR(50),
                floor VARCHAR(20),
                view_type VARCHAR(100),
                ownership_type VARCHAR(50),
                week_number VARCHAR(20),
                season VARCHAR(20),
                usage_type VARCHAR(20),
                sale_price NUMERIC(10, 2),
                rental_price_weekly NUMERIC(10, 2),
                rental_price_nightly NUMERIC(10, 2),
                maintenance_fee NUMERIC(10, 2),
                available_dates TEXT,
                check_in_day VARCHAR(20),
                amenities TEXT,
                contact_method VARCHAR(20) DEFAULT 'email',
                contact_phone VARCHAR(20),
                contact_email VARCHAR(100),
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
        
        # Create indexes
        print("🔧 Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_listing_user_id ON listing(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_listing_status ON listing(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_listing_property_type ON listing(property_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_listing_city ON listing(city)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_listing_state ON listing(state)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_listing_created_at ON listing(created_at)")
        
        conn.commit()
        conn.close()
        
        print("✅ Listing table schema fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing listing schema: {e}")
        raise

if __name__ == "__main__":
    fix_listing_schema()

