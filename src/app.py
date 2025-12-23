"""
Application factory and configuration.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import sys

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from config.settings import DevelopmentConfig, ProductionConfig, TestingConfig
from security.jwt_handler import JWTHandler
from infrastructure.database.models import Base

# Initialize SQLAlchemy
db = SQLAlchemy()


def create_app(config_name: str = "development") -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    if config_name == "production":
        app.config.from_object(ProductionConfig)
    elif config_name == "testing":
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize JWT handler
    jwt_handler = JWTHandler(
        secret_key=app.config['SECRET_KEY'],
        algorithm=app.config['JWT_ALGORITHM']
    )
    
    # Create database tables
    with app.app_context():
        from infrastructure.database.models import Base
        Base.metadata.create_all(db.engine)
    
    # Debug route
    @app.route("/", methods=["GET"])
    def health_check():
        return {"status": "Server is running", "message": "Welcome to Travellr API"}, 200
    
    # Register blueprints
    try:
        from api.v1.auth.routes import auth_bp, init_auth
        init_auth(db, jwt_handler)
        app.register_blueprint(auth_bp, url_prefix="/api/v1")
        print("✓ Auth routes registered")
    except Exception as e:
        print(f"✗ Auth routes failed: {e}")
    
    try:
        from api.v1.users.routes import users_bp, init_users
        init_users(db)
        app.register_blueprint(users_bp, url_prefix="/api/v1")
        print("✓ Users routes registered")
    except Exception as e:
        print(f"✗ Users routes failed: {e}")
    
    try:
        from api.v1.bookings.routes import bookings_bp, init_bookings
        init_bookings(db)
        app.register_blueprint(bookings_bp, url_prefix="/api/v1")
        print("✓ Bookings routes registered")
    except Exception as e:
        print(f"✗ Bookings routes failed: {e}")
    
    try:
        from api.v1.payments.routes import payments_bp, init_payments
        init_payments(db)
        app.register_blueprint(payments_bp, url_prefix="/api/v1")
        print("✓ Payments routes registered")
    except Exception as e:
        print(f"✗ Payments routes failed: {e}")
    
    try:
        from api.v1.admin.routes import admin_bp, init_admin
        init_admin(db)
        app.register_blueprint(admin_bp, url_prefix="/api/v1")
        print("✓ Admin routes registered")
    except Exception as e:
        print(f"✗ Admin routes failed: {e}")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Resource not found", "status": "error"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {"error": "Internal server error", "status": "error"}, 500
    
    return app
