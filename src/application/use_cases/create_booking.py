"""
Create Booking use case.
"""
from datetime import datetime
from infrastructure.database.models import BookingModel, BookingStatus
from domain.events.booking_events import BookingCreatedEvent


class CreateBookingRequest:
    """Request object for creating a booking."""
    
    def __init__(self, user_id: str, vendor_id: str, trip_date, total_price: float):
        self.user_id = user_id
        self.vendor_id = vendor_id
        self.trip_date = trip_date
        self.total_price = total_price


class CreateBookingResponse:
    """Response object for booking creation."""
    
    def __init__(self, booking_id: str, status: str, message: str):
        self.booking_id = booking_id
        self.status = status
        self.message = message


class CreateBookingUseCase:
    """Use case for creating a new booking."""
    
    def __init__(self, booking_repository, payment_service, event_bus):
        self.booking_repository = booking_repository
        self.payment_service = payment_service
        self.event_bus = event_bus
    
    def execute(self, request: CreateBookingRequest) -> CreateBookingResponse:
        """
        Execute the create booking use case.
        
        Steps:
        1. Validate input
        2. Create booking entity
        3. Save to repository
        4. Emit booking created event
        5. Return response
        """
        try:
            # Step 1: Validate input
            if not request.user_id:
                raise ValueError("user_id is required")
            if not request.vendor_id:
                raise ValueError("vendor_id is required")
            if not request.trip_date:
                raise ValueError("trip_date is required")
            if request.total_price <= 0:
                raise ValueError("total_price must be greater than 0")
            
            # Step 2: Create booking entity
            import uuid
            booking_id = str(uuid.uuid4())
            
            booking = BookingModel(
                id=booking_id,
                user_id=request.user_id,
                vendor_id=request.vendor_id,
                trip_date=request.trip_date,
                total_price=request.total_price,
                status=BookingStatus.PENDING
            )
            
            # Step 3: Save to repository
            self.booking_repository.save(booking)
            
            # Step 4: Emit booking created event
            event = BookingCreatedEvent(
                booking_id=booking_id,
                user_id=request.user_id,
                vendor_id=request.vendor_id
            )
            self.event_bus.publish(event)
            
            # Step 5: Return response
            return CreateBookingResponse(
                booking_id=booking_id,
                status="pending",
                message="Booking created successfully"
            )
            
        except Exception as e:
            raise Exception(f"Failed to create booking: {str(e)}")

