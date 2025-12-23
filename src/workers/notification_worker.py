"""
Notification worker for sending emails, SMS, push notifications.
"""


class NotificationWorker:
    """Worker for processing notifications."""
    
    def __init__(self, email_service, sms_service, push_service):
        self.email_service = email_service
        self.sms_service = sms_service
        self.push_service = push_service
    
    def send_booking_confirmation(self, user_id: str, booking_id: str):
        """Send booking confirmation notification."""
        pass
    
    def send_booking_cancelled(self, user_id: str, booking_id: str):
        """Send booking cancellation notification."""
        pass
    
    def send_payment_reminder(self, user_id: str, booking_id: str):
        """Send payment reminder notification."""
        pass
