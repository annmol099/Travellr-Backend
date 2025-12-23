"""
Booking management routes.
"""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from infrastructure.database.models import BookingModel, BookingStatus, UserModel

bookings_bp = Blueprint("bookings", __name__, url_prefix="/bookings")

# Will be set by app
db = None

def init_bookings(database):
    """Initialize bookings routes with database."""
    global db
    db = database


@bookings_bp.route("", methods=["POST"])
def create_booking():
    """Create a new booking."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["user_id", "vendor_id", "trip_date", "total_price"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing required field: {field}",
                    "status": "error"
                }), 400
        
        # Check if user exists
        user = db.session.query(UserModel).filter_by(id=data['user_id']).first()
        if not user:
            return jsonify({
                "error": "User not found",
                "status": "error"
            }), 404
        
        # Create booking
        booking_id = str(uuid.uuid4())
        booking = BookingModel(
            id=booking_id,
            user_id=data['user_id'],
            vendor_id=data['vendor_id'],
            trip_date=data['trip_date'],
            total_price=data['total_price'],
            status=BookingStatus.PENDING
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            "message": "Booking created successfully",
            "booking": {
                "id": booking.id,
                "user_id": booking.user_id,
                "vendor_id": booking.vendor_id,
                "trip_date": booking.trip_date.isoformat(),
                "status": booking.status.value,
                "total_price": booking.total_price,
                "created_at": booking.created_at.isoformat()
            },
            "status": "success"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Failed to create booking",
            "message": str(e),
            "status": "error"
        }), 500


@bookings_bp.route("/<booking_id>", methods=["GET"])
def get_booking(booking_id):
    """Get booking details."""
    try:
        booking = db.session.query(BookingModel).filter_by(id=booking_id).first()
        
        if not booking:
            return jsonify({
                "error": "Booking not found",
                "status": "error"
            }), 404
        
        return jsonify({
            "booking": {
                "id": booking.id,
                "user_id": booking.user_id,
                "vendor_id": booking.vendor_id,
                "trip_date": booking.trip_date.isoformat(),
                "status": booking.status.value,
                "total_price": booking.total_price,
                "created_at": booking.created_at.isoformat(),
                "updated_at": booking.updated_at.isoformat()
            },
            "status": "success"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to fetch booking",
            "message": str(e),
            "status": "error"
        }), 500


@bookings_bp.route("/<booking_id>", methods=["PUT"])
def update_booking(booking_id):
    """Update booking."""
    try:
        booking = db.session.query(BookingModel).filter_by(id=booking_id).first()
        
        if not booking:
            return jsonify({
                "error": "Booking not found",
                "status": "error"
            }), 404
        
        data = request.get_json()
        
        if 'total_price' in data:
            booking.total_price = data['total_price']
        
        db.session.commit()
        
        return jsonify({
            "message": "Booking updated successfully",
            "booking": {
                "id": booking.id,
                "user_id": booking.user_id,
                "vendor_id": booking.vendor_id,
                "total_price": booking.total_price,
                "status": booking.status.value
            },
            "status": "success"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Failed to update booking",
            "message": str(e),
            "status": "error"
        }), 500


@bookings_bp.route("/<booking_id>/cancel", methods=["POST"])
def cancel_booking(booking_id):
    """Cancel a booking."""
    try:
        booking = db.session.query(BookingModel).filter_by(id=booking_id).first()
        
        if not booking:
            return jsonify({
                "error": "Booking not found",
                "status": "error"
            }), 404
        
        if booking.status == BookingStatus.CANCELLED:
            return jsonify({
                "error": "Booking is already cancelled",
                "status": "error"
            }), 400
        
        booking.status = BookingStatus.CANCELLED
        db.session.commit()
        
        return jsonify({
            "message": "Booking cancelled successfully",
            "booking": {
                "id": booking.id,
                "status": booking.status.value,
                "updated_at": booking.updated_at.isoformat()
            },
            "status": "success"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Failed to cancel booking",
            "message": str(e),
            "status": "error"
        }), 500
