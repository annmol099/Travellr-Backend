"""
Notification worker for sending emails, SMS, push notifications.
Subscribes to domain events and sends notifications via email, SMS, and push.
"""
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending emails."""
    
    def __init__(self, smtp_config: Dict[str, Any] = None):
        """Initialize email service."""
        self.smtp_config = smtp_config or {}
    
    def send(self, to_email: str, subject: str, body: str, html: bool = False) -> bool:
        """Send email."""
        try:
            logger.info(f"Email sent to {to_email}: {subject}")
            print(f"[EMAIL] To: {to_email}")
            print(f"[EMAIL] Subject: {subject}")
            print(f"[EMAIL] Body: {body}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False


class SMSService:
    """SMS service for sending SMS messages."""
    
    def __init__(self, provider_config: Dict[str, Any] = None):
        """Initialize SMS service (Twilio, etc)."""
        self.provider_config = provider_config or {}
    
    def send(self, phone: str, message: str) -> bool:
        """Send SMS message."""
        try:
            logger.info(f"SMS sent to {phone}: {message}")
            print(f"[SMS] To: {phone}")
            print(f"[SMS] Message: {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return False


class PushService:
    """Push notification service."""
    
    def __init__(self, push_config: Dict[str, Any] = None):
        """Initialize push service (Firebase, etc)."""
        self.push_config = push_config or {}
    
    def send(self, user_id: str, title: str, message: str, data: Dict = None) -> bool:
        """Send push notification."""
        try:
            logger.info(f"Push sent to user {user_id}: {title}")
            print(f"[PUSH] User: {user_id}")
            print(f"[PUSH] Title: {title}")
            print(f"[PUSH] Message: {message}")
            if data:
                print(f"[PUSH] Data: {data}")
            return True
        except Exception as e:
            logger.error(f"Failed to send push notification: {str(e)}")
            return False


class NotificationWorker:
    """Worker for processing notifications."""
    
    def __init__(self, email_service=None, sms_service=None, push_service=None, user_repo=None, booking_repo=None):
        self.email_service = email_service or EmailService()
        self.sms_service = sms_service or SMSService()
        self.push_service = push_service or PushService()
        self.user_repo = user_repo
        self.booking_repo = booking_repo
    
    def send_booking_confirmation(self, user_id: str, booking_id: str, booking_data: Dict) -> bool:
        """
        Send booking confirmation notification (Email + SMS + Push).
        
        Args:
            user_id: User ID
            booking_id: Booking ID
            booking_data: Booking details dict
        """
        try:
            user_email = booking_data.get('user_email', '')
            user_phone = booking_data.get('user_phone', '')
            trip_date = booking_data.get('trip_date', 'N/A')
            total_price = booking_data.get('total_price', 0)
            
            # Email notification
            email_subject = f"Booking Confirmed! - Reference {booking_id}"
            email_body = f"""Dear Customer,

Your booking has been successfully confirmed!

Booking Details:
- Booking ID: {booking_id}
- Trip Date: {trip_date}
- Total Price: ${total_price}
- Status: CONFIRMED

Your vendor will contact you shortly with more details.

Best regards,
Travellr Team"""
            self.email_service.send(user_email, email_subject, email_body)
            
            # SMS notification
            sms_message = f"Hi! Your booking {booking_id[:8]} is confirmed for {trip_date}. Check your email for details."
            self.sms_service.send(user_phone, sms_message)
            
            # Push notification
            self.push_service.send(
                user_id,
                title="Booking Confirmed!",
                message=f"Your booking for {trip_date} is confirmed.",
                data={"booking_id": booking_id, "status": "confirmed"}
            )
            
            logger.info(f"Booking confirmation notifications sent for booking {booking_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending booking confirmation: {str(e)}")
            return False
    
    def send_booking_cancelled(self, user_id: str, booking_id: str, booking_data: Dict, reason: str = "") -> bool:
        """
        Send booking cancellation notification.
        
        Args:
            user_id: User ID
            booking_id: Booking ID
            booking_data: Booking details
            reason: Cancellation reason
        """
        try:
            user_email = booking_data.get('user_email', '')
            user_phone = booking_data.get('user_phone', '')
            total_price = booking_data.get('total_price', 0)
            
            # Email notification
            email_subject = f"Booking Cancelled - Reference {booking_id}"
            email_body = f"""Dear Customer,

Your booking has been cancelled.

Booking Details:
- Booking ID: {booking_id}
- Status: CANCELLED
- Refund Amount: ${total_price}
- Reason: {reason or 'Customer requested cancellation'}

Your refund will be processed within 3-5 business days.

Best regards,
Travellr Team"""
            self.email_service.send(user_email, email_subject, email_body)
            
            # SMS notification
            sms_message = f"Your booking {booking_id[:8]} has been cancelled. Refund of ${total_price} will be processed shortly."
            self.sms_service.send(user_phone, sms_message)
            
            # Push notification
            self.push_service.send(
                user_id,
                title="Booking Cancelled",
                message=f"Your booking {booking_id[:8]} has been cancelled. Refund initiated.",
                data={"booking_id": booking_id, "status": "cancelled"}
            )
            
            logger.info(f"Booking cancellation notifications sent for booking {booking_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending cancellation notification: {str(e)}")
            return False
    
    def send_payment_reminder(self, user_id: str, booking_id: str, booking_data: Dict, days_until: int = 1) -> bool:
        """
        Send payment reminder notification.
        
        Args:
            user_id: User ID
            booking_id: Booking ID
            booking_data: Booking details
            days_until: Days until trip
        """
        try:
            user_email = booking_data.get('user_email', '')
            user_phone = booking_data.get('user_phone', '')
            trip_date = booking_data.get('trip_date', 'N/A')
            total_price = booking_data.get('total_price', 0)
            
            # Email notification
            email_subject = f"Payment Reminder - Booking {booking_id}"
            email_body = f"""Dear Customer,

This is a friendly reminder that your trip is coming up in {days_until} day(s)!

Please complete your payment to confirm your booking.

Booking Details:
- Booking ID: {booking_id}
- Trip Date: {trip_date}
- Amount Due: ${total_price}

Complete payment now to avoid cancellation.

Best regards,
Travellr Team"""
            self.email_service.send(user_email, email_subject, email_body)
            
            # SMS notification
            sms_message = f"Reminder: Your trip is in {days_until} day(s)! Complete payment of ${total_price} now for booking {booking_id[:8]}."
            self.sms_service.send(user_phone, sms_message)
            
            # Push notification
            self.push_service.send(
                user_id,
                title="Payment Reminder",
                message=f"Complete payment for your trip on {trip_date}",
                data={"booking_id": booking_id, "type": "payment_reminder"}
            )
            
            logger.info(f"Payment reminder notifications sent for booking {booking_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending payment reminder: {str(e)}")
            return False
