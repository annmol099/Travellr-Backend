"""
Cancel Booking use case.
"""


class CancelBookingUseCase:
    """Use case for cancelling an existing booking."""
    
    def __init__(self, booking_repository, refund_service):
        self.booking_repository = booking_repository
        self.refund_service = refund_service
    
    def execute(self, booking_id):
        """Execute the cancel booking use case."""
        # Fetch booking
        # Validate cancellation eligibility
        # Process refund
        # Update booking status
        # Emit booking cancelled event
        pass
