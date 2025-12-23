"""
Notification worker for sending emails, SMS, push notifications.
"""
from infrastructure.database.models import BookingModel,UserModel


class NotificationWorker:
    """Worker for processing notifications."""
    
    def __init__(self, email_service, sms_service, push_service):
        self.email_service = email_service
        self.sms_service = sms_service
        self.push_service = push_service

        #fetch user_id and booking_id 
    def _get_user_and_booking(self,user_id:str,booking_id:str):
        user=UserModel.objects.get(id=user_id)
        booking=BookingModel.objects.get(id=booking_id)

        return user,booking
    def send_booking_confirmation(self, user_id: str, booking_id: str):
        """Send booking confirmation notification."""
        user,booking=self._get_user_and_booking(user_id,booking_id)

        message = (
            f"Hi {user.first_name}, "
            f"your booking #{booking.id} is confirmed."
        )

        self.email_service.send(
            to=user.email,
            subject="Booking Confirmed",
            body=message
        )

        self.sms_service.send(
            to=user.phone_number,
            message=message
        )

        self.push_service.send(
            user_id=user.id,
            title="Booking Confirmed",
            body=message
        )

        return True
    
    def send_booking_cancelled(self, user_id: str, booking_id: str):
        """Send booking cancellation notification."""
        user,booking=self._get_user_and_booking(user_id,booking_id)

        message=(
            f"Hi {user.first_name}, "
            f"your booking #{booking.id} has been cancelled."
        )
        self.email_service.send(
            to=user.email,
            subject="Booking Cancelled",
            body=message
        )

        self.sms_service.send(
            to=user.phone_number,
            message=message
        )

        self.push_service.send(
            user_id=user.id,
            title="Booking Cancelled",
            body=message
        )

        return True
    
    def send_payment_reminder(self, user_id: str, booking_id: str):
        """Send payment reminder notification."""
        user, booking = self._get_user_and_booking(user_id, booking_id)

        message = (
            f"Hi {user.first_name}, "
            f"payment is pending for booking #{booking.id}. "
            f"Please complete it soon."
        )

        self.email_service.send(
            to=user.email,
            subject="Payment Reminder",
            body=message
        )

        self.sms_service.send(
            to=user.phone_number,
            message=message
        )

        self.push_service.send(
            user_id=user.id,
            title="Payment Pending",
            body=message
        )

        return True
        
