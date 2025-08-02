import os
import sys

# Environment variables are loaded directly from Render

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.payment import payment_bp
from src.routes.membership import membership_bp
from src.routes.listing import listing_bp
from src.routes.dashboard import dashboard_bp
from src.routes.pages import pages_bp
from src.routes.inquiry import inquiry_bp
from src.routes.favorites import favorites_bp
from src.routes.browser_auth import browser_auth_bp
from src.routes.pricing import pricing_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Enable CORS for all routes
CORS(app)

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(membership_bp)
app.register_blueprint(listing_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(pages_bp)
app.register_blueprint(inquiry_bp)
app.register_blueprint(favorites_bp)
app.register_blueprint(browser_auth_bp)
app.register_blueprint(pricing_bp)

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
    # Run database migrations before creating tables
    from src.database_migration import run_migrations
    run_migrations()
    
    # Create all tables
    db.create_all()

# Serve static files and homepage
@app.route('/')
def serve_homepage():
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404
    
    index_path = os.path.join(static_folder_path, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(static_folder_path, 'index.html')
    else:
        return "index.html not found", 404

# Serve static files
@app.route('/<path:filename>')
def serve_static(filename):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404
    
    # Only serve actual static files (with extensions)
    if '.' in filename and os.path.exists(os.path.join(static_folder_path, filename)):
        return send_from_directory(static_folder_path, filename)
    
    # For routes without extensions, return 404 to let blueprints handle them
    from flask import abort
    abort(404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
