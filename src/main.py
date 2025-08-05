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
from src.routes.seo import seo_bp

app = Flask(__name__, static_folder='static', static_url_path='/static')

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
app.register_blueprint(seo_bp)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DATABASE_PATH'] = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
db.init_app(app)

# Import all models to ensure they are registered
from src.models.user import User
from src.models.listing import Listing

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory('static', 'dashboard.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

