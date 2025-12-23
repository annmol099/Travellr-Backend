"""
Repository implementations for database access.
"""
from typing import Optional, List
from sqlalchemy.exc import SQLAlchemyError
from src.infrastructure.database.models import UserModel, BookingModel, PaymentModel


class UserRepository:
    """Repository for User entities."""
    
    def __init__(self, session):
        self.session = session
    
    def save(self, user: UserModel) -> UserModel:
        """Save a user to the database."""
        try:
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"Failed to save user: {str(e)}")
    
    def find_by_id(self, user_id: str) -> Optional[UserModel]:
        """Find a user by ID."""
        try:
            return self.session.query(UserModel).filter(
                UserModel.id == user_id
            ).first()
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to find user: {str(e)}")
    
    def find_by_email(self, email: str) -> Optional[UserModel]:
        """Find a user by email."""
        try:
            return self.session.query(UserModel).filter(
                UserModel.email == email.lower()
            ).first()
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to find user: {str(e)}")
    
    def find_all(self, page: int = 1, limit: int = 10) -> tuple:
        """Find all users with pagination."""
        try:
            offset = (page - 1) * limit
            users = self.session.query(UserModel).offset(offset).limit(limit).all()
            total = self.session.query(UserModel).count()
            return users, total
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to find users: {str(e)}")
    
    def update(self, user_id: str, **kwargs) -> Optional[UserModel]:
        """Update a user."""
        try:
            user = self.find_by_id(user_id)
            if not user:
                return None
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            self.session.commit()
            self.session.refresh(user)
            return user
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"Failed to update user: {str(e)}")
    
    def delete(self, user_id: str) -> bool:
        """Delete a user."""
        try:
            user = self.find_by_id(user_id)
            if not user:
                return False
            
            self.session.delete(user)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"Failed to delete user: {str(e)}")
    
    def exists(self, email: str) -> bool:
        """Check if user exists by email."""
        try:
            return self.session.query(UserModel).filter(
                UserModel.email == email.lower()
            ).first() is not None
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to check user existence: {str(e)}")


class BookingRepository:
    """Repository for Booking entities."""
    
    def __init__(self, session):
        self.session = session
    
    def save(self, booking: BookingModel) -> BookingModel:
        """Save a booking to the database."""
        try:
            self.session.add(booking)
            self.session.commit()
            self.session.refresh(booking)
            return booking
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"Failed to save booking: {str(e)}")
    
    def find_by_id(self, booking_id: str) -> Optional[BookingModel]:
        """Find a booking by ID."""
        try:
            return self.session.query(BookingModel).filter(
                BookingModel.id == booking_id
            ).first()
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to find booking: {str(e)}")
    
    def find_by_user_id(self, user_id: str, page: int = 1, 
                       limit: int = 10) -> tuple:
        """Find all bookings for a user with pagination."""
        try:
            offset = (page - 1) * limit
            bookings = self.session.query(BookingModel).filter(
                BookingModel.user_id == user_id
            ).offset(offset).limit(limit).all()
            total = self.session.query(BookingModel).filter(
                BookingModel.user_id == user_id
            ).count()
            return bookings, total
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to find bookings: {str(e)}")
    
    def find_by_vendor_id(self, vendor_id: str, page: int = 1,
                         limit: int = 10) -> tuple:
        """Find all bookings for a vendor with pagination."""
        try:
            offset = (page - 1) * limit
            bookings = self.session.query(BookingModel).filter(
                BookingModel.vendor_id == vendor_id
            ).offset(offset).limit(limit).all()
            total = self.session.query(BookingModel).filter(
                BookingModel.vendor_id == vendor_id
            ).count()
            return bookings, total
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to find vendor bookings: {str(e)}")
    
    def find_all(self, page: int = 1, limit: int = 10) -> tuple:
        """Find all bookings with pagination."""
        try:
            offset = (page - 1) * limit
            bookings = self.session.query(BookingModel).offset(offset).limit(limit).all()
            total = self.session.query(BookingModel).count()
            return bookings, total
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to find bookings: {str(e)}")
    
    def update(self, booking_id: str, **kwargs) -> Optional[BookingModel]:
        """Update a booking."""
        try:
            booking = self.find_by_id(booking_id)
            if not booking:
                return None
            
            for key, value in kwargs.items():
                if hasattr(booking, key):
                    setattr(booking, key, value)
            
            self.session.commit()
            self.session.refresh(booking)
            return booking
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"Failed to update booking: {str(e)}")
    
    def delete(self, booking_id: str) -> bool:
        """Delete a booking."""
        try:
            booking = self.find_by_id(booking_id)
            if not booking:
                return False
            
            self.session.delete(booking)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"Failed to delete booking: {str(e)}")
    
    def count_by_status(self, status: str) -> int:
        """Count bookings by status."""
        try:
            return self.session.query(BookingModel).filter(
                BookingModel.status == status
            ).count()
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to count bookings: {str(e)}")


class PaymentRepository:
    """Repository for Payment entities."""
    
    def __init__(self, session):
        self.session = session
    
    def save(self, payment: PaymentModel) -> PaymentModel:
        """Save a payment to the database."""
        try:
            self.session.add(payment)
            self.session.commit()
            self.session.refresh(payment)
            return payment
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"Failed to save payment: {str(e)}")
    
    def find_by_id(self, payment_id: str) -> Optional[PaymentModel]:
        """Find a payment by ID."""
        try:
            return self.session.query(PaymentModel).filter(
                PaymentModel.id == payment_id
            ).first()
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to find payment: {str(e)}")
    
    def find_by_booking_id(self, booking_id: str) -> List[PaymentModel]:
        """Find payments for a booking."""
        try:
            return self.session.query(PaymentModel).filter(
                PaymentModel.booking_id == booking_id
            ).all()
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to find payments: {str(e)}")
    
    def find_all(self, page: int = 1, limit: int = 10) -> tuple:
        """Find all payments with pagination."""
        try:
            offset = (page - 1) * limit
            payments = self.session.query(PaymentModel).offset(offset).limit(limit).all()
            total = self.session.query(PaymentModel).count()
            return payments, total
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to find payments: {str(e)}")
    
    def update(self, payment_id: str, **kwargs) -> Optional[PaymentModel]:
        """Update a payment."""
        try:
            payment = self.find_by_id(payment_id)
            if not payment:
                return None
            
            for key, value in kwargs.items():
                if hasattr(payment, key):
                    setattr(payment, key, value)
            
            self.session.commit()
            self.session.refresh(payment)
            return payment
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"Failed to update payment: {str(e)}")
    
    def delete(self, payment_id: str) -> bool:
        """Delete a payment."""
        try:
            payment = self.find_by_id(payment_id)
            if not payment:
                return False
            
            self.session.delete(payment)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"Failed to delete payment: {str(e)}")
    
    def sum_by_status(self, status: str) -> float:
        """Sum payments by status."""
        try:
            result = self.session.query(
                __import__('sqlalchemy').func.sum(PaymentModel.amount)
            ).filter(PaymentModel.status == status).scalar()
            return float(result or 0)
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to sum payments: {str(e)}")
