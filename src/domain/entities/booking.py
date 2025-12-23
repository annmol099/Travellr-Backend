"""
Booking domain entity.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class BookingStatus(Enum):
    """Booking status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Booking:
    """Booking entity representing a travel booking."""
    
    id: str
    user_id: str
    vendor_id: str
    trip_date: datetime
    status: BookingStatus = BookingStatus.PENDING
    total_price: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def confirm(self):
        """Confirm the booking."""
        self.status = BookingStatus.CONFIRMED
        self.updated_at = datetime.now()
    
    def complete(self):
        """Mark booking as completed."""
        self.status = BookingStatus.COMPLETED
        self.updated_at = datetime.now()
    
    def cancel(self):
        """Cancel the booking."""
        self.status = BookingStatus.CANCELLED
        self.updated_at = datetime.now()
