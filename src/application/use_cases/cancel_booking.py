"""
Cancel Booking use case.
"""
from infrastructure.database.models import BookingStatus
from domain.events.booking_events import BookingCancelledEvent


class CancelBookingRequest:
    """Request object for cancelling a booking."""
    
    def __init__(self, booking_id: str, reason: str = "User requested cancellation"):
        self.booking_id = booking_id
        self.reason = reason


class CancelBookingResponse:
    """Response object for booking cancellation."""
    
    def __init__(self, booking_id: str, status: str, message: str):
        self.booking_id = booking_id
        self.status = status
        self.message = message


class CancelBookingUseCase:
    """Use case for cancelling an existing booking."""
    
    def __init__(self, booking_repository, refund_service, event_bus):
        self.booking_repository = booking_repository
        self.refund_service = refund_service
        self.event_bus = event_bus
    
    def execute(self, request: CancelBookingRequest) -> CancelBookingResponse:
        """
        Execute the cancel booking use case.
        
        Steps:
        1. Fetch booking from repository
        2. Validate cancellation eligibility
        3. Process refund if applicable
        4. Update booking status to cancelled
        5. Emit booking cancelled event
        6. Return response
        """
        try:
            # Step 1: Fetch booking
            booking = self.booking_repository.find_by_id(request.booking_id)
            
            if not booking:
                raise ValueError(f"Booking {request.booking_id} not found")
            
            # Step 2: Validate cancellation eligibility
            if booking.status == BookingStatus.CANCELLED:
                raise ValueError("Booking is already cancelled")
            
            if booking.status == BookingStatus.COMPLETED:
                raise ValueError("Cannot cancel a completed booking")
            
            # Step 3: Process refund if payment was made
            if booking.status in [BookingStatus.CONFIRMED, BookingStatus.COMPLETED]:
                refund_result = self.refund_service.refund_booking(
                    booking_id=request.booking_id,
                    amount=booking.total_price
                )
                
                if not refund_result:
                    raise Exception("Refund processing failed")
            
            # Step 4: Update booking status
            booking.status = BookingStatus.CANCELLED
            self.booking_repository.save(booking)
            
            # Step 5: Emit booking cancelled event
            event = BookingCancelledEvent(
                booking_id=request.booking_id,
                reason=request.reason
            )
            self.event_bus.publish(event)
            
            # Step 6: Return response
            return CancelBookingResponse(
                booking_id=request.booking_id,
                status="cancelled",
                message="Booking cancelled successfully"
            )
            
        except Exception as e:
            raise Exception(f"Failed to cancel booking: {str(e)}")

