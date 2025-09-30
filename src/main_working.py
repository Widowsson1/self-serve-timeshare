from flask import Flask, render_template, session, request, jsonify, send_from_directory
import os
from datetime import datetime

# Import working models and routes
from models.user_fixed import db, User
from models.listing import Listing
from routes.auth_working import auth_working_bp
from routes.payment_working import payment_working_bp
from routes.listing_working import listing_working_bp

app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'working_app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_working_bp)
app.register_blueprint(payment_working_bp)
app.register_blueprint(listing_working_bp)

# Create database tables
with app.app_context():
    # Ensure database directory exists
    db_dir = os.path.join(os.path.dirname(__file__), 'database')
    os.makedirs(db_dir, exist_ok=True)
    
    # Create all tables
    db.create_all()
    
    # Create test user if doesn't exist
    if not User.query.filter_by(username='testuser').first():
        test_user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_active=True,
            email_verified=True,
            account_type='free'
        )
        test_user.set_password('password123')
        db.session.add(test_user)
        db.session.commit()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/get-started')
def get_started():
    return render_template('get_started.html')

@app.route('/browse-listings')
def browse_listings():
    return render_template('browse_listings.html')

# Static file serving
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

# Template serving
@app.route('/templates/<path:filename>')
def template_files(filename):
    return send_from_directory('templates', filename)

# API for memberships
@app.route('/api/memberships')
def get_memberships():
    return jsonify({
        'success': True,
        'memberships': [
            {'id': 1, 'name': 'Free', 'price': 0},
            {'id': 2, 'name': 'Starter', 'price': 29},
            {'id': 3, 'name': 'Basic', 'price': 49},
            {'id': 4, 'name': 'Premium', 'price': 99},
            {'id': 5, 'name': 'Unlimited', 'price': 199}
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

