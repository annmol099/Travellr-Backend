"""
SQLAlchemy database models.
"""
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import enum


Base = declarative_base()


class UserModel(Base):
    """SQLAlchemy User model."""
    
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(20))
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class BookingStatus(enum.Enum):
    """Booking status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BookingModel(Base):
    """SQLAlchemy Booking model."""
    
    __tablename__ = "bookings"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    vendor_id = Column(String(36), nullable=False)
    trip_date = Column(DateTime, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    total_price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class PaymentModel(Base):
    """SQLAlchemy Payment model."""
    
    __tablename__ = "payments"
    
    id = Column(String(36), primary_key=True)
    booking_id = Column(String(36), ForeignKey("bookings.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
