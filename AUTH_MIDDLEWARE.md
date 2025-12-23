# Auth Middleware - Complete Implementation Guide

## Overview

The authentication middleware provides three decorators for protecting Flask routes with JWT token verification:

1. **`@token_required`** - Strict authentication (token mandatory)
2. **`@admin_required`** - Admin-only authentication
3. **`@optional_token`** - Optional authentication

---

## 1. @token_required - Mandatory Token

**Use for:** Protected routes that require authentication

**Behavior:**
- Checks for "Authorization: Bearer <token>" header
- Validates JWT signature and expiration
- Stores user_id in Flask's g object
- Returns 401 if missing or invalid

**Example:**

```python
from flask import Blueprint, jsonify, g
from src.middlewares.auth_middleware import token_required

users_bp = Blueprint('users', __name__, url_prefix='/api/v1/users')

@users_bp.route('/<user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """Get user profile - requires authentication."""
    current_user = g.user_id  # Available from middleware
    
    if current_user != user_id:
        return jsonify({"error": "Forbidden"}), 403
    
    # Get user from database
    user = UserRepository(db.session).find_by_id(user_id)
    return jsonify({"id": user.id, "email": user.email}), 200

@users_bp.route('/<user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    """Update user profile - requires authentication."""
    current_user = g.user_id
    
    if current_user != user_id:
        return jsonify({"error": "Forbidden"}), 403
    
    # Update logic
    return jsonify({"message": "Updated"}), 200
```

**Response Examples:**

```bash
# Missing token
curl http://localhost:5000/api/v1/users/123
# Response: 401 {"error": "Unauthorized", "message": "Missing authorization header"}

# Invalid token
curl -H "Authorization: Bearer invalid_token" http://localhost:5000/api/v1/users/123
# Response: 401 {"error": "Unauthorized", "message": "Invalid or expired token"}

# Valid token
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." http://localhost:5000/api/v1/users/123
# Response: 200 {"id": "123", "email": "user@example.com"}
```

---

## 2. @admin_required - Admin-Only Access

**Use for:** Admin endpoints that require admin role

**Behavior:**
- Same as token_required
- Checks token has "role": "admin" in payload
- Returns 403 if user is not admin

**Example:**

```python
from src.middlewares.auth_middleware import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')

@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_all_users():
    """List all users - admin only."""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    users, total = UserRepository(db.session).find_all(page, limit)
    
    return jsonify({
        "users": [{"id": u.id, "email": u.email} for u in users],
        "total": total,
        "page": page
    }), 200

@admin_bp.route('/analytics', methods=['GET'])
@admin_required
def get_analytics():
    """Get platform analytics - admin only."""
    total_users = UserRepository(db.session).find_all()[1]
    total_bookings = BookingRepository(db.session).find_all()[1]
    total_revenue = PaymentRepository(db.session).sum_by_status("completed")
    
    return jsonify({
        "total_users": total_users,
        "total_bookings": total_bookings,
        "total_revenue": total_revenue
    }), 200
```

**Response Examples:**

```bash
# Non-admin user tries to access
curl -H "Authorization: Bearer user_token" http://localhost:5000/api/v1/admin/users
# Response: 403 {"error": "Forbidden", "message": "Admin access required"}

# Admin user accesses
curl -H "Authorization: Bearer admin_token" http://localhost:5000/api/v1/admin/users
# Response: 200 {"users": [...], "total": 100, "page": 1}
```

---

## 3. @optional_token - Optional Authentication

**Use for:** Public routes that work better with auth but don't require it

**Behavior:**
- Accepts token if provided
- Validates it (doesn't fail if invalid, just skips auth)
- Route can check if `g.user_id` exists
- No error if token missing

**Example:**

```python
from src.middlewares.auth_middleware import optional_token

bookings_bp = Blueprint('bookings', __name__, url_prefix='/api/v1/bookings')

@bookings_bp.route('/', methods=['GET'])
@optional_token
def list_bookings():
    """
    List bookings - works for both authenticated and anonymous users.
    
    Authenticated: Returns user's bookings
    Anonymous: Returns public/available bookings
    """
    if hasattr(g, 'user_id'):
        # Authenticated user - get their bookings
        page = request.args.get('page', 1, type=int)
        bookings, total = BookingRepository(db.session).find_by_user_id(
            g.user_id, page, 10
        )
        return jsonify({
            "bookings": [b.to_dict() for b in bookings],
            "total": total,
            "scope": "personal"
        }), 200
    else:
        # Anonymous user - get public available bookings
        public_bookings = BookingRepository(db.session).find_all(
            status="available"
        )
        return jsonify({
            "bookings": [b.to_dict() for b in public_bookings],
            "scope": "public"
        }), 200
```

**Response Examples:**

```bash
# Anonymous user
curl http://localhost:5000/api/v1/bookings/
# Response: 200 {"bookings": [available_bookings], "scope": "public"}

# Authenticated user
curl -H "Authorization: Bearer token" http://localhost:5000/api/v1/bookings/
# Response: 200 {"bookings": [user_bookings], "scope": "personal"}

# Invalid token (still works, just no auth)
curl -H "Authorization: Bearer invalid" http://localhost:5000/api/v1/bookings/
# Response: 200 {"bookings": [public_bookings], "scope": "public"}
```

---

## Integration in Routes

### Example: Complete API Module with Auth

```python
# src/api/v1/bookings/routes.py

from flask import Blueprint, request, jsonify, g
from src.middlewares.auth_middleware import token_required, optional_token
from src.infrastructure.database.repositories import BookingRepository
from src.infrastructure.database.models import BookingModel, db
from src.application.use_cases.create_booking import CreateBookingUseCase
from datetime import datetime
import uuid

bookings_bp = Blueprint('bookings', __name__, url_prefix='/api/v1/bookings')

@bookings_bp.route('/', methods=['POST'])
@token_required
def create_booking():
    """Create a new booking - requires authentication."""
    data = request.get_json()
    
    # Use current user from middleware
    user_id = g.user_id
    
    # Validate input
    if not data.get('vendor_id') or not data.get('trip_date') or not data.get('total_price'):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        # Parse date
        trip_date = datetime.fromisoformat(data['trip_date'])
        
        # Create booking use case
        use_case = CreateBookingUseCase(
            BookingRepository(db.session),
            payment_service=None,
            event_bus=None
        )
        
        result = use_case.execute({
            'user_id': user_id,
            'vendor_id': data['vendor_id'],
            'trip_date': trip_date,
            'total_price': data['total_price']
        })
        
        return jsonify(result), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bookings_bp.route('/<booking_id>', methods=['GET'])
@optional_token
def get_booking(booking_id):
    """Get booking details - optional auth for owner verification."""
    booking = BookingRepository(db.session).find_by_id(booking_id)
    
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    
    # If authenticated, check if user is owner
    if hasattr(g, 'user_id') and booking.user_id != g.user_id:
        return jsonify({"error": "Forbidden"}), 403
    
    return jsonify({
        "id": booking.id,
        "user_id": booking.user_id,
        "vendor_id": booking.vendor_id,
        "trip_date": booking.trip_date.isoformat(),
        "status": booking.status,
        "total_price": booking.total_price
    }), 200

@bookings_bp.route('/<booking_id>/cancel', methods=['POST'])
@token_required
def cancel_booking(booking_id):
    """Cancel booking - requires authentication."""
    user_id = g.user_id
    
    booking = BookingRepository(db.session).find_by_id(booking_id)
    
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    
    if booking.user_id != user_id:
        return jsonify({"error": "Forbidden"}), 403
    
    # Cancel logic
    try:
        booking.status = "cancelled"
        BookingRepository(db.session).save(booking)
        return jsonify({"message": "Booking cancelled"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
```

---

## How It Works

### Token Format

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3MDM0NTAwMDAsImV4cCI6MTcwMzQ1MzYwMH0.signature
```

### Token Payload (decoded)

```json
{
  "user_id": "123",
  "role": "user",
  "iat": 1703450000,
  "exp": 1703453600
}
```

### Middleware Flow

```
Request comes in
    ↓
Check Authorization header
    ↓
Parse "Bearer <token>"
    ↓
Verify JWT signature and expiration
    ↓
Extract user_id and role
    ↓
Store in Flask's g object
    ↓
Continue to route handler
```

---

## Accessing User Info in Routes

```python
from flask import g

@app.route('/api/v1/profile')
@token_required
def get_profile():
    # Access authenticated user
    user_id = g.user_id
    
    # Access full token payload if needed
    token_payload = g.token_payload  # {"user_id": "123", "role": "user", ...}
    
    return {"user_id": user_id}, 200
```

---

## Error Responses

### 401 Unauthorized - Missing Token
```json
{
  "error": "Unauthorized",
  "message": "Missing authorization header"
}
```

### 401 Unauthorized - Invalid Format
```json
{
  "error": "Unauthorized",
  "message": "Invalid authorization header format. Expected: 'Bearer <token>'"
}
```

### 401 Unauthorized - Expired/Invalid Token
```json
{
  "error": "Unauthorized",
  "message": "Token has expired"
}
```

### 403 Forbidden - Not Admin
```json
{
  "error": "Forbidden",
  "message": "Admin access required"
}
```

---

## Summary

| Decorator | Token Required | Role Check | Returns 401 | Returns 403 |
|-----------|---|---|---|---|
| `@token_required` | Yes | No | Yes | No |
| `@admin_required` | Yes | Yes (admin) | Yes | Yes |
| `@optional_token` | No | No | No | No |

---

## Testing

### With Postman

1. **Get Token:**
   ```
   POST http://localhost:5000/api/v1/auth/login
   Body: {"email": "user@example.com", "password": "password"}
   ```

2. **Use Token in Protected Route:**
   ```
   GET http://localhost:5000/api/v1/users/123
   Headers: Authorization: Bearer <token_from_step_1>
   ```

### With curl

```bash
# Login
TOKEN=$(curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.token')

# Use token on protected route
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/v1/users/123
```

---

**Auth Middleware: 100% COMPLETE ✅**
