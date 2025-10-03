import os
import sys
import threading
import time
import requests
from datetime import datetime

# Environment variables are loaded directly from Render

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from models.user import db
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
from src.routes.analytics import analytics_bp
from src.routes.auth import auth_bp
from src.routes.auth_simple import auth_simple_bp
from src.routes.get_started import get_started_bp
from src.routes.migration import migration_bp
from src.routes.membership_upgrade import membership_upgrade_bp
from src.routes.web_migration import web_migration_bp
from src.routes.user_api import user_api_bp
from src.routes.plan_upgrade import plan_upgrade_bp
from src.logging_config import setup_logging

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Setup logging
setup_logging(app)

CORS(app)

# Configure session
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SESSION_TYPE'] = 'filesystem'

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
app.register_blueprint(analytics_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(auth_simple_bp)
app.register_blueprint(get_started_bp)
app.register_blueprint(migration_bp)
app.register_blueprint(membership_upgrade_bp)
app.register_blueprint(web_migration_bp)
app.register_blueprint(user_api_bp)
app.register_blueprint(plan_upgrade_bp)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DATABASE_PATH'] = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
db.init_app(app)

# Import all models to ensure they are registered
from models.user import User
from models.listing import Listing

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory('static', 'dashboard.html')

# Render wake-up ping endpoint
@app.route('/ping')
def ping():
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.now().isoformat(),
        'message': 'SelfServe Timeshare is awake'
    })

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'SelfServe Timeshare'
    })

def keep_alive():
    """Function to ping the server every 14 minutes to prevent sleeping"""
    while True:
        try:
            # Wait 14 minutes (840 seconds) - Render free tier sleeps after 15 minutes of inactivity
            time.sleep(840)
            
            # Get the app URL from environment or use default
            app_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://self-serve-timeshare.onrender.com')
            
            # Ping the health endpoint
            response = requests.get(f"{app_url}/ping", timeout=30)
            print(f"Keep-alive ping sent at {datetime.now()}: Status {response.status_code}")
            
        except Exception as e:
            print(f"Keep-alive ping failed at {datetime.now()}: {e}")

# Start keep-alive thread when app starts
def start_keep_alive():
    """Start the keep-alive thread"""
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    print("Keep-alive system started - pinging every 14 minutes")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Start keep-alive system
    start_keep_alive()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # For production deployment (Gunicorn), start keep-alive when module is imported
    with app.app_context():
        db.create_all()
    start_keep_alive()

