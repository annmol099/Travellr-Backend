"""
SQLAlchemy database models.
"""
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Boolean, Enum, ForeignKey, Integer
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


class VendorStatus(enum.Enum):
    """Vendor status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class VendorModel(Base):
    """SQLAlchemy Vendor model."""
    
    __tablename__ = "vendors"
    
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    business_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    bank_account = Column(String(255), nullable=False)
    tax_id = Column(String(100))
    status = Column(Enum(VendorStatus), default=VendorStatus.PENDING)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class TripModel(Base):
    """SQLAlchemy Trip model."""
    
    __tablename__ = "trips"
    
    id = Column(String(36), primary_key=True)
    vendor_id = Column(String(36), ForeignKey("vendors.id"), nullable=False)
    location = Column(String(255), nullable=False)
    description = Column(String(1000))
    price = Column(Float, nullable=False)
    trip_date = Column(DateTime, nullable=False)
    max_capacity = Column(Integer, default=10)
    current_bookings = Column(Integer, default=0)
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
