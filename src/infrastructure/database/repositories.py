"""
Repository implementations for database access.
"""
from typing import Optional, List


class UserRepository:
    """Repository for User entities."""
    
    def __init__(self, session):
        self.session = session
    
    def save(self, user):
        """Save a user to the database."""
        pass
    
    def find_by_id(self, user_id: str):
        """Find a user by ID."""
        pass
    
    def find_by_email(self, email: str):
        """Find a user by email."""
        pass
    
    def find_all(self) -> List:
        """Find all users."""
        pass


class BookingRepository:
    """Repository for Booking entities."""
    
    def __init__(self, session):
        self.session = session
    
    def save(self, booking):
        """Save a booking to the database."""
        pass
    
    def find_by_id(self, booking_id: str) -> Optional:
        """Find a booking by ID."""
        pass
    
    def find_by_user_id(self, user_id: str) -> List:
        """Find all bookings for a user."""
        pass
    
    def find_by_vendor_id(self, vendor_id: str) -> List:
        """Find all bookings for a vendor."""
        pass


class PaymentRepository:
    """Repository for Payment entities."""
    
    def __init__(self, session):
        self.session = session
    
    def save(self, payment):
        """Save a payment to the database."""
        pass
    
    def find_by_id(self, payment_id: str):
        """Find a payment by ID."""
        pass
    
    def find_by_booking_id(self, booking_id: str):
        """Find payments for a booking."""
        pass
