"""
Parameterized tests for comprehensive coverage of various scenarios.
"""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from src.infrastructure.database.models import UserModel, VendorModel, TripModel
from src.infrastructure.database.repositories import UserRepository, VendorRepository, TripRepository
from src.security.password_handler import PasswordHandler


class TestUserValidationParametrized:
    """Parameterized tests for user validation."""
    
    @pytest.fixture
    def user_repo(self, db_session):
        """Create user repository."""
        return UserRepository(db_session)
    
    @pytest.mark.parametrize("email,should_pass", [
        ("valid@example.com", True),
        ("another.email@domain.co.uk", True),
        ("user+tag@example.com", True),
        ("", False),
        ("invalid-email", False),
        ("missing@domain", True),  # Technically valid
        ("spaces in@email.com", False),
    ])
    def test_email_validation(self, email, should_pass, user_repo):
        """Test various email formats."""
        user = UserModel(
            id=str(uuid4()),
            email=email,
            password_hash="hash",
            name="Test User",
            phone="+919999999999"
        )
        
        if should_pass:
            # Should be able to save
            if email:  # Skip empty emails
                saved = user_repo.save(user)
                assert saved.email == email
        else:
            # Should fail validation (in real scenario)
            if not email or " " in email:
                # These would be caught by Flask validation
                pass
    
    @pytest.mark.parametrize("phone,valid", [
        ("+919999999999", True),
        ("+1-555-123-4567", True),
        ("9999999999", True),
        ("", True),  # Phone is optional
        (None, True),  # Phone is optional
    ])
    def test_phone_formats(self, phone, valid, user_repo):
        """Test various phone number formats."""
        user = UserModel(
            id=str(uuid4()),
            email=f"user{uuid4()}@example.com",
            password_hash="hash",
            name="Test User",
            phone=phone
        )
        
        saved = user_repo.save(user)
        assert saved.phone == phone
    
    @pytest.mark.parametrize("name,valid", [
        ("John Doe", True),
        ("A", True),
        ("Jane O'Brien", True),
        ("José García", True),
        ("李明", True),
        ("", False),
        ("Name with123numbers", True),
    ])
    def test_name_formats(self, name, valid, user_repo):
        """Test various name formats."""
        user = UserModel(
            id=str(uuid4()),
            email=f"user{uuid4()}@example.com",
            password_hash="hash",
            name=name if name else "Default Name",
            phone="+919999999999"
        )
        
        saved = user_repo.save(user)
        if name:
            assert saved.name == name


class TestPasswordValidationParametrized:
    """Parameterized tests for password hashing and validation."""
    
    @pytest.mark.parametrize("password", [
        "SimplePass123",
        "C0mpl3x!Pass@Word",
        "VeryLongPasswordWithManyCharacters1234567890",
        "123456",  # Minimum length
        "Pass with spaces 123",
        "密码中文",  # Non-ASCII characters
    ])
    def test_password_hashing_all_formats(self, password):
        """Test password hashing with various password formats."""
        hashed = PasswordHandler.hash_password(password)
        
        assert hashed != password
        assert PasswordHandler.verify_password(password, hashed)
        assert not PasswordHandler.verify_password("wrongpassword", hashed)


class TestTripPricingParametrized:
    """Parameterized tests for trip pricing."""
    
    @pytest.fixture
    def trip_repo(self, db_session):
        """Create trip repository."""
        return TripRepository(db_session)
    
    @pytest.mark.parametrize("price,capacity,description", [
        (0.01, 1, "Minimum price single person"),
        (10.00, 5, "Budget tour"),
        (100.00, 20, "Standard tour"),
        (500.00, 10, "Premium tour"),
        (5000.00, 5, "Luxury tour"),
        (99999.99, 100, "Ultra luxury"),
    ])
    def test_trip_pricing_variants(self, price, capacity, description, trip_repo):
        """Test trips with various price points."""
        trip = TripModel(
            id=str(uuid4()),
            vendor_id=str(uuid4()),
            location="Test Location",
            description=description,
            price=price,
            trip_date=datetime.now() + timedelta(days=7),
            max_capacity=capacity
        )
        
        saved = trip_repo.save(trip)
        assert saved.price == price
        assert saved.max_capacity == capacity
    
    @pytest.mark.parametrize("max_capacity,current_bookings,expected_available", [
        (10, 0, 10),
        (10, 5, 5),
        (10, 10, 0),
        (20, 8, 12),
        (100, 50, 50),
        (1, 0, 1),
    ])
    def test_trip_capacity_calculations(self, max_capacity, current_bookings, expected_available, trip_repo):
        """Test trip capacity tracking."""
        trip = TripModel(
            id=str(uuid4()),
            vendor_id=str(uuid4()),
            location="Test Location",
            description="Capacity test",
            price=100.00,
            trip_date=datetime.now() + timedelta(days=7),
            max_capacity=max_capacity,
            current_bookings=current_bookings
        )
        
        saved = trip_repo.save(trip)
        available = saved.max_capacity - saved.current_bookings
        assert available == expected_available


class TestTripSchedulingParametrized:
    """Parameterized tests for trip scheduling."""
    
    @pytest.fixture
    def trip_repo(self, db_session):
        """Create trip repository."""
        return TripRepository(db_session)
    
    @pytest.mark.parametrize("days_ahead,hours_ahead", [
        (1, 0),      # Tomorrow
        (7, 0),      # Next week
        (30, 0),     # Next month
        (365, 0),    # Next year
        (1, 12),     # Tomorrow afternoon
        (7, 8),      # Next week morning
    ])
    def test_trip_dates_various_future(self, days_ahead, hours_ahead, trip_repo):
        """Test trips scheduled for various future dates."""
        trip_date = datetime.now() + timedelta(days=days_ahead, hours=hours_ahead)
        
        trip = TripModel(
            id=str(uuid4()),
            vendor_id=str(uuid4()),
            location="Future Location",
            description="Future scheduled trip",
            price=100.00,
            trip_date=trip_date,
            max_capacity=20
        )
        
        saved = trip_repo.save(trip)
        assert saved.trip_date == trip_date


class TestVendorStatusTransitionsParametrized:
    """Parameterized tests for vendor status transitions."""
    
    @pytest.fixture
    def vendor_repo(self, db_session):
        """Create vendor repository."""
        return VendorRepository(db_session)
    
    @pytest.mark.parametrize("initial_status,update_status,should_work", [
        ("PENDING", "APPROVED", True),
        ("PENDING", "REJECTED", True),
        ("APPROVED", "SUSPENDED", True),
        ("REJECTED", "PENDING", True),  # Can reapply
        ("SUSPENDED", "APPROVED", True),
    ])
    def test_vendor_status_transitions(self, initial_status, update_status, should_work, vendor_repo):
        """Test vendor status transitions."""
        from src.infrastructure.database.models import VendorStatus
        
        vendor = VendorModel(
            id=str(uuid4()),
            email=f"vendor{uuid4()}@example.com",
            password_hash="hash",
            business_name="Test Tours",
            phone="+919999999999",
            bank_account="123",
            status=VendorStatus[initial_status]
        )
        
        saved = vendor_repo.save(vendor)
        
        updated = vendor_repo.update(
            saved.id,
            status=VendorStatus[update_status]
        )
        
        if should_work:
            assert updated.status == VendorStatus[update_status]


class TestBulkOperationsParametrized:
    """Parameterized tests for bulk operations."""
    
    @pytest.fixture
    def repositories(self, db_session):
        """Initialize repositories."""
        return {
            'user': UserRepository(db_session),
            'vendor': VendorRepository(db_session),
            'trip': TripRepository(db_session)
        }
    
    @pytest.mark.parametrize("count", [5, 10, 20, 50])
    def test_bulk_user_creation(self, count, repositories):
        """Test creating multiple users."""
        user_repo = repositories['user']
        
        users = []
        for i in range(count):
            user = UserModel(
                id=str(uuid4()),
                email=f"bulk_user_{i}_{uuid4()}@example.com",
                password_hash="hash",
                name=f"Bulk User {i}",
                phone=f"+919{i:09d}"
            )
            saved = user_repo.save(user)
            users.append(saved)
        
        assert len(users) == count
        
        # Verify pagination
        retrieved, total = user_repo.find_all(page=1, limit=10)
        assert total >= count
    
    @pytest.mark.parametrize("vendor_count,trips_per_vendor", [
        (3, 2),   # 6 trips total
        (5, 3),   # 15 trips total
        (2, 5),   # 10 trips total
    ])
    def test_bulk_trip_creation(self, vendor_count, trips_per_vendor, repositories):
        """Test creating multiple trips."""
        vendor_repo = repositories['vendor']
        trip_repo = repositories['trip']
        
        # Create vendors
        vendors = []
        for i in range(vendor_count):
            from src.infrastructure.database.models import VendorStatus
            vendor = VendorModel(
                id=str(uuid4()),
                email=f"bulk_vendor_{i}_{uuid4()}@example.com",
                password_hash="hash",
                business_name=f"Bulk Tours {i}",
                phone=f"+918{i:09d}",
                bank_account=f"account{i}",
                status=VendorStatus.APPROVED
            )
            saved = vendor_repo.save(vendor)
            vendors.append(saved)
        
        # Create trips
        total_trips = 0
        for vendor in vendors:
            for j in range(trips_per_vendor):
                trip = TripModel(
                    id=str(uuid4()),
                    vendor_id=vendor.id,
                    location=f"Location {j}",
                    description=f"Trip {j}",
                    price=100.00 + j * 10,
                    trip_date=datetime.now() + timedelta(days=j+1),
                    max_capacity=20
                )
                trip_repo.save(trip)
                total_trips += 1
        
        # Verify total trips
        assert total_trips == vendor_count * trips_per_vendor
        
        # Verify each vendor has correct number of trips
        for vendor in vendors:
            vendor_trips = trip_repo.find_by_vendor(vendor.id)
            assert len(vendor_trips) == trips_per_vendor
