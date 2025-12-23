"""
Booking domain events.
"""
from domain.events.domain_event import DomainEvent


class BookingCreatedEvent(DomainEvent):
    """Event raised when a booking is created."""
    
    def __init__(self, booking_id: str, user_id: str, vendor_id: str, **kwargs):
        super().__init__("booking.created", booking_id, kwargs)


class BookingCancelledEvent(DomainEvent):
    """Event raised when a booking is cancelled."""
    
    def __init__(self, booking_id: str, reason: str, **kwargs):
        super().__init__("booking.cancelled", booking_id, {"reason": reason, **kwargs})


class BookingCompletedEvent(DomainEvent):
    """Event raised when a booking is completed."""
    
    def __init__(self, booking_id: str, **kwargs):
        super().__init__("booking.completed", booking_id, kwargs)
