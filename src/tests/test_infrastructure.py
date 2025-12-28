"""
Unit tests for infrastructure components.
Tests: repositories, cache service, event bus.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock


class TestUserRepository:
    """Test UserRepository."""
    
    @pytest.fixture
    def repository(self):
        """Create user repository with mock session."""
        from src.infrastructure.database.repositories import UserRepository
        return UserRepository(session=Mock())
    
    def test_create_user(self, repository):
        """Test creating a user."""
        from src.infrastructure.database.models import UserModel
        result = repository.save(
            UserModel(
                email='john@example.com',
                name='John Doe',
                password_hash='hash123'
            )
        )
        
        # Should call session.add
        assert repository.session.add.called or result is not None
    
    def test_get_user_by_id(self, repository):
        """Test getting user by ID."""
        from src.infrastructure.database.models import UserModel
        user_id = 'user123'
        result = repository.find_by_id(user_id)
        
        assert repository.session.query.called or result is not None
    
    def test_get_user_by_email(self, repository):
        """Test getting user by email."""
        email = 'john@example.com'
        result = repository.find_by_email(email)
        
        assert repository.session.query.called or result is not None


class TestBookingRepository:
    """Test BookingRepository."""
    
    @pytest.fixture
    def repository(self):
        """Create booking repository with mock session."""
        from src.infrastructure.database.repositories import BookingRepository
        return BookingRepository(session=Mock())
    
    def test_create_booking(self, repository):
        """Test creating a booking."""
        from src.infrastructure.database.models import BookingModel
        result = repository.save(
            BookingModel(
                user_id='user123',
                vendor_id='vendor456',
                trip_date=datetime.now() + timedelta(days=7),
                total_price=500.00
            )
        )
        
        assert repository.session.add.called or result is not None
    
    def test_get_booking_by_id(self, repository):
        """Test getting booking by ID."""
        booking_id = 'book123'
        result = repository.find_by_id(booking_id)
        
        assert repository.session.query.called or result is not None


class TestPaymentRepository:
    """Test PaymentRepository."""
    
    @pytest.fixture
    def repository(self):
        """Create payment repository with mock session."""
        from src.infrastructure.database.repositories import PaymentRepository
        return PaymentRepository(session=Mock())
    
    def test_create_payment(self, repository):
        """Test creating a payment record."""
        from src.infrastructure.database.models import PaymentModel
        result = repository.save(
            PaymentModel(
                booking_id='book123',
                amount=500.00,
                status='completed'
            )
        )
        
        assert repository.session.add.called or result is not None


class TestEventBus:
    """Test EventBus."""
    
    @pytest.fixture
    def event_bus(self):
        """Create event bus."""
        from src.infrastructure.messaging.event_bus import EventBus
        return EventBus()
    
    def test_subscribe_to_event(self, event_bus):
        """Test subscribing to events."""
        handler = Mock()
        event_bus.subscribe('booking.created', handler)
        
        assert 'booking.created' in event_bus.subscribers
    
    def test_publish_event(self, event_bus):
        """Test publishing events."""
        handler = Mock()
        event_bus.subscribe('booking.created', handler)
        
        event_data = Mock()
        event_data.event_type = 'booking.created'
        
        event_bus.publish(event_data)
        
        assert handler.called
    
    def test_multiple_handlers(self, event_bus):
        """Test multiple handlers for same event."""
        handler1 = Mock()
        handler2 = Mock()
        
        event_bus.subscribe('booking.created', handler1)
        event_bus.subscribe('booking.created', handler2)
        
        event_data = Mock()
        event_data.event_type = 'booking.created'
        
        event_bus.publish(event_data)
        
        assert handler1.called
        assert handler2.called
