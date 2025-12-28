"""
Unit tests for domain models and value objects.
Tests: User, Booking entities and Money, Email value objects.
"""
import pytest
from datetime import datetime, timedelta


class TestUserEntity:
    """Test User entity."""
    
    def test_create_user(self):
        """Test creating a user."""
        from src.domain.entities.user import User
        
        user = User(
            id='user123',
            email='john@example.com',
            name='John Doe',
            phone='+1234567890'
        )
        
        assert user.id == 'user123'
        assert user.email == 'john@example.com'
        assert user.name == 'John Doe'
    
    def test_user_password_hashing(self):
        """Test that user password is hashed."""
        from src.domain.entities.user import User
        
        user = User(
            id='user123',
            email='john@example.com',
            name='John Doe'
        )
        
        user.set_password('SecurePassword123!')
        
        # Password should not be plain text
        assert user.password_hash != 'SecurePassword123!'
        # Password should be verifiable
        assert user.check_password('SecurePassword123!')
    
    def test_user_password_verification(self):
        """Test password verification."""
        from src.domain.entities.user import User
        
        user = User(
            id='user123',
            email='john@example.com',
            name='John Doe'
        )
        
        user.set_password('SecurePassword123!')
        
        # Correct password should verify
        assert user.check_password('SecurePassword123!')
        # Wrong password should not verify
        assert not user.check_password('WrongPassword')


class TestBookingEntity:
    """Test Booking entity."""
    
    def test_create_booking(self):
        """Test creating a booking."""
        from src.domain.entities.booking import Booking
        from src.domain.value_objects.money import Money
        
        trip_date = datetime.now() + timedelta(days=7)
        
        booking = Booking(
            id='book123',
            user_id='user123',
            vendor_id='vendor456',
            trip_date=trip_date,
            location='New York',
            total_price=Money(500.00, 'USD'),
            status='pending'
        )
        
        assert booking.id == 'book123'
        assert booking.user_id == 'user123'
        assert booking.status == 'pending'
    
    def test_booking_status_transitions(self):
        """Test booking status transitions."""
        from src.domain.entities.booking import Booking
        from src.domain.value_objects.money import Money
        
        trip_date = datetime.now() + timedelta(days=7)
        booking = Booking(
            id='book123',
            user_id='user123',
            vendor_id='vendor456',
            trip_date=trip_date,
            location='New York',
            total_price=Money(500.00, 'USD'),
            status='pending'
        )
        
        # Valid transitions
        booking.status = 'confirmed'
        assert booking.status == 'confirmed'


class TestMoneyValueObject:
    """Test Money value object."""
    
    def test_create_money(self):
        """Test creating a Money object."""
        from src.domain.value_objects.money import Money
        
        money = Money(100.00, 'USD')
        
        assert money.amount == 100.00
        assert money.currency == 'USD'
    
    def test_money_equality(self):
        """Test money equality."""
        from src.domain.value_objects.money import Money
        
        money1 = Money(100.00, 'USD')
        money2 = Money(100.00, 'USD')
        money3 = Money(150.00, 'USD')
        
        assert money1 == money2
        assert money1 != money3
    
    def test_money_addition(self):
        """Test adding money objects."""
        from src.domain.value_objects.money import Money
        
        money1 = Money(100.00, 'USD')
        money2 = Money(50.00, 'USD')
        
        result = money1 + money2
        
        assert result.amount == 150.00
        assert result.currency == 'USD'


class TestEmailValueObject:
    """Test Email value object."""
    
    def test_create_email(self):
        """Test creating an Email."""
        from src.domain.value_objects.email import Email
        
        email = Email('john@example.com')
        
        assert email.value == 'john@example.com'
    
    def test_email_validation(self):
        """Test email validation."""
        from src.domain.value_objects.email import Email
        
        # Valid emails should work
        Email('john@example.com')
        Email('user.name+tag@example.co.uk')
        
        # Invalid emails should raise
        with pytest.raises(ValueError):
            Email('invalid-email')
    
    def test_email_equality(self):
        """Test email equality."""
        from src.domain.value_objects.email import Email
        
        email1 = Email('john@example.com')
        email2 = Email('john@example.com')
        email3 = Email('jane@example.com')
        
        assert email1 == email2
        assert email1 != email3
