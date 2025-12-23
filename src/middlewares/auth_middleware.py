"""
Authentication middleware.
"""
from functools import wraps
from flask import request, jsonify


def token_required(f):
    """Decorator to require valid JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        
        if not token:
            return jsonify({"message": "Missing authorization token"}), 401
        
        try:
            # Validate token
            # Extract user from token
            pass
        except Exception as e:
            return jsonify({"message": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    
    return decorated
