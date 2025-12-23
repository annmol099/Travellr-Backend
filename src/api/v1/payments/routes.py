"""
Payment processing routes.
"""
from flask import Blueprint, request, jsonify
import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from infrastructure.database.models import PaymentModel, BookingModel

payments_bp = Blueprint("payments", __name__, url_prefix="/payments")

# Will be set by app
db = None

def init_payments(database):
    """Initialize payments routes with database."""
    global db
    db = database


@payments_bp.route("", methods=["POST"])
def process_payment():
    """Process a payment transaction."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["booking_id", "amount", "currency"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing required field: {field}",
                    "status": "error"
                }), 400
        
        # Check if booking exists
        booking = db.session.query(BookingModel).filter_by(id=data['booking_id']).first()
        if not booking:
            return jsonify({
                "error": "Booking not found",
                "status": "error"
            }), 404
        
        # Create payment record
        payment_id = str(uuid.uuid4())
        payment = PaymentModel(
            id=payment_id,
            booking_id=data['booking_id'],
            amount=data['amount'],
            currency=data.get('currency', 'USD'),
            status='completed'  # In real app, call Stripe here
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            "message": "Payment processed successfully",
            "payment": {
                "id": payment.id,
                "booking_id": payment.booking_id,
                "amount": payment.amount,
                "currency": payment.currency,
                "status": payment.status,
                "created_at": payment.created_at.isoformat()
            },
            "status": "success"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Payment processing failed",
            "message": str(e),
            "status": "error"
        }), 500


@payments_bp.route("/<payment_id>", methods=["GET"])
def get_payment(payment_id):
    """Get payment details."""
    try:
        payment = db.session.query(PaymentModel).filter_by(id=payment_id).first()
        
        if not payment:
            return jsonify({
                "error": "Payment not found",
                "status": "error"
            }), 404
        
        return jsonify({
            "payment": {
                "id": payment.id,
                "booking_id": payment.booking_id,
                "amount": payment.amount,
                "currency": payment.currency,
                "status": payment.status,
                "created_at": payment.created_at.isoformat()
            },
            "status": "success"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to fetch payment",
            "message": str(e),
            "status": "error"
        }), 500


@payments_bp.route("/<payment_id>/refund", methods=["POST"])
def refund_payment(payment_id):
    """Refund a payment."""
    try:
        payment = db.session.query(PaymentModel).filter_by(id=payment_id).first()
        
        if not payment:
            return jsonify({
                "error": "Payment not found",
                "status": "error"
            }), 404
        
        if payment.status == "refunded":
            return jsonify({
                "error": "Payment is already refunded",
                "status": "error"
            }), 400
        
        payment.status = "refunded"
        db.session.commit()
        
        return jsonify({
            "message": "Payment refunded successfully",
            "payment": {
                "id": payment.id,
                "booking_id": payment.booking_id,
                "amount": payment.amount,
                "status": payment.status,
                "updated_at": payment.updated_at.isoformat()
            },
            "status": "success"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Refund failed",
            "message": str(e),
            "status": "error"
        }), 500
