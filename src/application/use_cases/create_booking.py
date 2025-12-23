"""
Create Booking use case.
"""


class CreateBookingUseCase:
    """Use case for creating a new booking."""
    
    def __init__(self, booking_repository, payment_service):
        self.booking_repository = booking_repository
        self.payment_service = payment_service
    
    def execute(self, request):
        """Execute the create booking use case."""
        # Validate input
        # Create booking entity
        # Save to repository
        # Emit booking created event
        pass
