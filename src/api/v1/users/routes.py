"""
User management routes.
"""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from infrastructure.database.models import UserModel

users_bp = Blueprint("users", __name__, url_prefix="/api/v1/users")

# Will be set by app
db = None

def init_users(database):
    """Initialize users routes with database."""
    global db
    db = database


@users_bp.route("/<user_id>", methods=["GET"])
def get_user(user_id):
    """Get user details."""
    try:
        user = db.session.query(UserModel).filter_by(id=user_id).first()
        
        if not user:
            return jsonify({
                "error": "User not found",
                "status": "error"
            }), 404
        
        return jsonify({
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
        
    except Exception as e:
        return jsonify({
            "error": "Failed to fetch user",
            "message": str(e),
            "status": "error"
        }), 500


@users_bp.route("/<user_id>", methods=["PUT"])
def update_user(user_id):
    """Update user information."""
    try:
        user = db.session.query(UserModel).filter_by(id=user_id).first()
        
        if not user:
            return jsonify({
                "error": "User not found",
                "status": "error"
            }), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            user.name = data['name']
        if 'phone' in data:
            user.phone = data['phone']
        
        db.session.commit()
        
        return jsonify({
            "message": "User updated successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "phone": user.phone,
                "role": user.role,
                "is_active": user.is_active
            },
            "status": "success"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Failed to update user",
            "message": str(e),
            "status": "error"
        }), 500


@users_bp.route("/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Delete user account."""
    try:
        user = db.session.query(UserModel).filter_by(id=user_id).first()
        
        if not user:
            return jsonify({
                "error": "User not found",
                "status": "error"
            }), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            "message": "User deleted successfully",
            "status": "success"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Failed to delete user",
            "message": str(e),
            "status": "error"
        }), 500
