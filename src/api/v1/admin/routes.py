"""
Admin management routes.
"""
from flask import Blueprint, request, jsonify
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from infrastructure.database.models import UserModel, BookingModel, PaymentModel

admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")

# Will be set by app
db = None

def init_admin(database):
    """Initialize admin routes with database."""
    global db
    db = database


@admin_bp.route("/users", methods=["GET"])
def get_all_users():
    """Get all users (admin only)."""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Pagination
        users = db.session.query(UserModel).paginate(page=page, per_page=limit)
        
        users_data = [{
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        } for user in users.items]
        
        return jsonify({
            "users": users_data,
            "total": users.total,
            "pages": users.pages,
            "current_page": page,
            "status": "success"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to fetch users",
            "message": str(e),
            "status": "error"
        }), 500


@admin_bp.route("/bookings", methods=["GET"])
def get_all_bookings():
    """Get all bookings (admin only)."""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        bookings = db.session.query(BookingModel).paginate(page=page, per_page=limit)
        
        bookings_data = [{
            "id": booking.id,
            "user_id": booking.user_id,
            "vendor_id": booking.vendor_id,
            "trip_date": booking.trip_date.isoformat(),
            "status": booking.status.value,
            "total_price": booking.total_price,
            "created_at": booking.created_at.isoformat()
        } for booking in bookings.items]
        
        return jsonify({
            "bookings": bookings_data,
            "total": bookings.total,
            "pages": bookings.pages,
            "current_page": page,
            "status": "success"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to fetch bookings",
            "message": str(e),
            "status": "error"
        }), 500


@admin_bp.route("/analytics", methods=["GET"])
def get_analytics():
    """Get platform analytics (admin only)."""
    try:
        total_users = db.session.query(UserModel).count()
        total_bookings = db.session.query(BookingModel).count()
        total_payments = db.session.query(PaymentModel).count()
        
        # Calculate total revenue
        from sqlalchemy import func
        total_revenue = db.session.query(func.sum(PaymentModel.amount)).scalar() or 0
        
        return jsonify({
            "analytics": {
                "total_users": total_users,
                "total_bookings": total_bookings,
                "total_payments": total_payments,
                "total_revenue": total_revenue
            },
            "status": "success"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to fetch analytics",
            "message": str(e),
            "status": "error"
        }), 500
