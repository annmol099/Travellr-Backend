"""
Authentication middleware for token verification.
"""
from functools import wraps
from flask import request, jsonify, g
from src.security.jwt_handler import JWTHandler


def token_required(f):
    """
    Decorator to require valid JWT token on protected routes.
    
    Usage:
        @app.route('/api/v1/protected')
        @token_required
        def protected_route():
            user_id = g.user_id
            return {"message": "Success"}
    
    Returns:
        401 - Missing authorization header
        401 - Invalid/expired token
        401 - Malformed authorization header
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return jsonify({
                "error": "Unauthorized",
                "message": "Missing authorization header"
            }), 401
        
        try:
            # Parse "Bearer <token>" format
            parts = auth_header.split()
            
            if len(parts) != 2 or parts[0].lower() != "bearer":
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Invalid authorization header format. Expected: 'Bearer <token>'"
                }), 401
            
            token = parts[1]
            
            # Verify token with JWT handler
            jwt_handler = JWTHandler()
            payload = jwt_handler.verify_token(token)
            
            if not payload or "user_id" not in payload:
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Invalid token payload"
                }), 401
            
            # Store user_id in Flask's g object for route access
            g.user_id = payload["user_id"]
            g.token_payload = payload
            
        except ValueError as e:
            # Token expired or invalid signature
            return jsonify({
                "error": "Unauthorized",
                "message": str(e)
            }), 401
        except Exception as e:
            # Other errors (malformed token, etc)
            return jsonify({
                "error": "Unauthorized",
                "message": "Token verification failed"
            }), 401
        
        # Token is valid, proceed to route
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """
    Decorator to require valid JWT token with admin role.
    
    Checks:
    1. Token is valid
    2. Token has admin role in payload
    
    Usage:
        @app.route('/api/v1/admin/panel')
        @admin_required
        def admin_panel():
            return {"message": "Admin access"}
    
    Returns:
        401 - Missing/invalid token
        403 - Token valid but not admin
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # First check token is valid (same as token_required)
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return jsonify({
                "error": "Unauthorized",
                "message": "Missing authorization header"
            }), 401
        
        try:
            # Parse "Bearer <token>" format
            parts = auth_header.split()
            
            if len(parts) != 2 or parts[0].lower() != "bearer":
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Invalid authorization header format"
                }), 401
            
            token = parts[1]
            
            # Verify token
            jwt_handler = JWTHandler()
            payload = jwt_handler.verify_token(token)
            
            if not payload or "user_id" not in payload:
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Invalid token"
                }), 401
            
            # Check for admin role
            role = payload.get("role", "user")
            if role != "admin":
                return jsonify({
                    "error": "Forbidden",
                    "message": "Admin access required"
                }), 403
            
            # Store in g object
            g.user_id = payload["user_id"]
            g.token_payload = payload
            
        except ValueError:
            return jsonify({
                "error": "Unauthorized",
                "message": "Invalid or expired token"
            }), 401
        except Exception:
            return jsonify({
                "error": "Unauthorized",
                "message": "Token verification failed"
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated


def optional_token(f):
    """
    Decorator for routes that work with or without authentication.
    
    If token is provided:
    - Validates it
    - Stores user_id in g.user_id
    - Route can check if g.user_id exists
    
    If no token:
    - Continues without authentication
    - g.user_id will not be set
    
    Usage:
        @app.route('/api/v1/public/bookings')
        @optional_token
        def public_bookings():
            if hasattr(g, 'user_id'):
                # Authenticated user
                return get_user_bookings(g.user_id)
            else:
                # Anonymous user
                return get_public_bookings()
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        
        # If no token, just continue
        if not auth_header:
            return f(*args, **kwargs)
        
        try:
            # Parse token if provided
            parts = auth_header.split()
            
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
                jwt_handler = JWTHandler()
                payload = jwt_handler.verify_token(token)
                
                if payload and "user_id" in payload:
                    g.user_id = payload["user_id"]
                    g.token_payload = payload
        
        except (ValueError, Exception):
            # If token verification fails, just continue without auth
            # (This is optional authentication)
            pass
        
        return f(*args, **kwargs)
    
    return decorated
