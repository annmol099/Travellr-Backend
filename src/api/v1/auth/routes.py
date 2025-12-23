"""
Authentication routes.
"""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
import uuid
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from api.v1.auth.schemas import RegisterSchema, LoginSchema, TokenResponseSchema
from security.password_handler import PasswordHandler
from security.jwt_handler import JWTHandler
from infrastructure.database.models import UserModel

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Initialize extensions (will be set by app)
db = None
jwt_handler = None
password_handler = PasswordHandler()


def init_auth(database, jwt):
    """Initialize auth routes with database and JWT handler."""
    global db, jwt_handler
    db = database
    jwt_handler = jwt


@auth_bp.route("/register", methods=["POST"])
def register():
    """User registration endpoint."""
    try:
        # Validate request data
        schema = RegisterSchema()
        data = schema.load(request.get_json())
        
        # Check if user already exists
        existing_user = db.session.query(UserModel).filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({
                "error": "User with this email already exists",
                "status": "error"
            }), 400
        
        # Create new user
        user_id = str(uuid.uuid4())
        password_hash = password_handler.hash_password(data['password'])
        
        new_user = UserModel(
            id=user_id,
            email=data['email'],
            password_hash=password_hash,
            name=data['name'],
            phone=data.get('phone', None),
            role='user',
            is_active=True
        )
        
        # Save to database
        db.session.add(new_user)
        db.session.commit()
        
        # Generate JWT token
        access_token = jwt_handler.generate_token(user_id)
        
        response_schema = TokenResponseSchema()
        return jsonify({
            "message": "User registered successfully",
            "access_token": access_token,
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "name": new_user.name,
                "phone": new_user.phone,
                "role": new_user.role,
                "is_active": new_user.is_active,
                "created_at": new_user.created_at.isoformat()
            },
            "status": "success"
        }), 201
        
    except ValidationError as e:
        return jsonify({
            "error": "Validation failed",
            "details": e.messages,
            "status": "error"
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Registration failed",
            "message": str(e),
            "status": "error"
        }), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """User login endpoint."""
    try:
        # Validate request data
        schema = LoginSchema()
        data = schema.load(request.get_json())
        
        # Find user by email
        user = db.session.query(UserModel).filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({
                "error": "Invalid email or password",
                "status": "error"
            }), 401
        
        # Verify password
        if not password_handler.verify_password(data['password'], user.password_hash):
            return jsonify({
                "error": "Invalid email or password",
                "status": "error"
            }), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({
                "error": "User account is deactivated",
                "status": "error"
            }), 403
        
        # Generate JWT token
        access_token = jwt_handler.generate_token(user.id)
        
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "phone": user.phone,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat()
            },
            "status": "success"
        }), 200
        
    except ValidationError as e:
        return jsonify({
            "error": "Validation failed",
            "details": e.messages,
            "status": "error"
        }), 400
    except Exception as e:
        return jsonify({
            "error": "Login failed",
            "message": str(e),
            "status": "error"
        }), 500


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """User logout endpoint."""
    # In a real app, you'd add token to blacklist here
    return jsonify({
        "message": "Logout successful",
        "status": "success"
    }), 200
