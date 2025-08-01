import os
import sys

# Environment variables are loaded directly from Render

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.listing import listing_bp
from src.routes.membership import membership_bp
from src.routes.payment import payment_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Enable CORS for all routes
CORS(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(listing_bp, url_prefix='/api')
app.register_blueprint(membership_bp, url_prefix='/api')
app.register_blueprint(payment_bp, url_prefix='/payment')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DATABASE_PATH'] = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
db.init_app(app)

# Import all models to ensure they are registered
from src.models.user import User
from src.models.listing import Listing
from src.models.membership import Membership

with app.app_context():
    # Run direct database fix to ensure schema is correct
    try:
        from src.fix_database import fix_database
        print("🔧 Running database schema fix...")
        fix_database()
        print("✅ Database schema fix completed")
    except Exception as e:
        print(f"⚠️ Database fix warning: {e}")
    
    # Create all tables
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
