"""
Trip management tests.
"""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from src.infrastructure.database.models import TripModel, VendorModel, VendorStatus
from src.application.use_cases.create_trip import CreateTripUseCase, CreateTripRequest
from src.infrastructure.database.repositories import TripRepository, VendorRepository
from src.security.password_handler import PasswordHandler


class TestTripEntity:
    """Test Trip domain model."""
    
    def test_trip_creation(self):
        """Test creating a trip."""
        trip = TripModel(
            id=str(uuid4()),
            vendor_id=str(uuid4()),
            location="Goa Beach",
            description="Amazing beach tour",
            price=150.00,
            trip_date=datetime.now() + timedelta(days=7),
            max_capacity=20
        )
        
        assert trip.location == "Goa Beach"
        assert trip.price == 150.00
        assert trip.max_capacity == 20
        assert trip.current_bookings == 0
    
    def test_trip_available_spots(self):
        """Test calculating available spots."""
        trip = TripModel(
            id=str(uuid4()),
            vendor_id=str(uuid4()),
            location="Goa Beach",
            description="Beach tour",
            price=150.00,
            trip_date=datetime.now() + timedelta(days=7),
            max_capacity=20,
            current_bookings=5
        )
        
        available = trip.max_capacity - trip.current_bookings
        assert available == 15
    
    def test_trip_is_full(self):
        """Test checking if trip is full."""
        trip = TripModel(
            id=str(uuid4()),
            vendor_id=str(uuid4()),
            location="Goa Beach",
            description="Beach tour",
            price=150.00,
            trip_date=datetime.now() + timedelta(days=7),
            max_capacity=10,
            current_bookings=10
        )
        
        is_full = trip.current_bookings >= trip.max_capacity
        assert is_full == True


class TestTripRepository:
    """Test TripRepository."""
    
    @pytest.fixture
    def trip_repo(self, db_session):
        """Create trip repository."""
        return TripRepository(db_session)
    
    @pytest.fixture
    def vendor_repo(self, db_session):
        """Create vendor repository."""
        return VendorRepository(db_session)
    
    @pytest.fixture
    def sample_vendor(self, vendor_repo):
        """Create sample vendor."""
        vendor = VendorModel(
            id=str(uuid4()),
            email="vendor@example.com",
            password_hash="hash",
            business_name="Test Tours",
            phone="+919999999999",
            bank_account="1234567890",
            status=VendorStatus.APPROVED
        )
        return vendor_repo.save(vendor)
    
    @pytest.fixture
    def sample_trip(self, sample_vendor):
        """Create sample trip."""
        return TripModel(
            id=str(uuid4()),
            vendor_id=sample_vendor.id,
            location="Goa Beach",
            description="Amazing beach tour",
            price=150.00,
            trip_date=datetime.now() + timedelta(days=7),
            max_capacity=20
        )
    
    def test_save_trip(self, trip_repo, sample_trip):
        """Test saving a trip."""
        saved = trip_repo.save(sample_trip)
        
        assert saved.id == sample_trip.id
        assert saved.location == "Goa Beach"
        assert saved.vendor_id == sample_trip.vendor_id
    
    def test_find_trip_by_id(self, trip_repo, sample_trip):
        """Test finding trip by ID."""
        trip_repo.save(sample_trip)
        
        found = trip_repo.find_by_id(sample_trip.id)
        assert found is not None
        assert found.location == "Goa Beach"
    
    def test_find_trip_by_vendor(self, trip_repo, sample_vendor, sample_trip):
        """Test finding trips by vendor."""
        trip_repo.save(sample_trip)
        
        trips = trip_repo.find_by_vendor(sample_vendor.id)
        assert len(trips) >= 1
        assert sample_trip.id in [t.id for t in trips]
    
    def test_update_trip(self, trip_repo, sample_trip):
        """Test updating trip."""
        trip_repo.save(sample_trip)
        
        updated = trip_repo.update(sample_trip.id, location="Kerala Backwaters")
        assert updated.location == "Kerala Backwaters"
    
    def test_delete_trip(self, trip_repo, sample_trip):
        """Test deleting trip."""
        trip_repo.save(sample_trip)
        
        deleted = trip_repo.delete(sample_trip.id)
        assert deleted == True
        
        found = trip_repo.find_by_id(sample_trip.id)
        assert found is None
    
    def test_find_all_trips_pagination(self, trip_repo, sample_vendor):
        """Test finding all trips with pagination."""
        # Create multiple trips
        for i in range(15):
            trip = TripModel(
                id=str(uuid4()),
                vendor_id=sample_vendor.id,
                location=f"Location {i}",
                description=f"Tour {i}",
                price=100.0 + i,
                trip_date=datetime.now() + timedelta(days=i+1),
                max_capacity=10
            )
            trip_repo.save(trip)
        
        # Get page 1
        trips, total = trip_repo.find_all(page=1, limit=10)
        assert len(trips) == 10
        assert total >= 15
        
        # Get page 2
        trips2, total2 = trip_repo.find_all(page=2, limit=10)
        assert len(trips2) >= 1


class TestCreateTripUseCase:
    """Test create trip use case."""
    
    @pytest.fixture
    def create_trip_use_case(self, db_session):
        """Create trip use case."""
        trip_repo = TripRepository(db_session)
        vendor_repo = VendorRepository(db_session)
        return CreateTripUseCase(trip_repo, vendor_repo)
    
    @pytest.fixture
    def approved_vendor(self, db_session):
        """Create approved vendor."""
        vendor = VendorModel(
            id=str(uuid4()),
            email="vendor@example.com",
            password_hash="hash",
            business_name="Test Tours",
            phone="+919999999999",
            bank_account="1234567890",
            status=VendorStatus.APPROVED
        )
        repo = VendorRepository(db_session)
        return repo.save(vendor)
    
    def test_create_trip_success(self, create_trip_use_case, approved_vendor):
        """Test successful trip creation."""
        request = CreateTripRequest(
            vendor_id=approved_vendor.id,
            location="Goa Beach",
            description="Amazing beach tour",
            price=150.00,
            trip_date=(datetime.now() + timedelta(days=7)).isoformat(),
            max_capacity=20
        )
        
        response = create_trip_use_case.execute(request)
        
        assert response.location == "Goa Beach"
        assert response.price == 150.00
        assert response.vendor_id == approved_vendor.id
    
    def test_create_trip_invalid_location(self, create_trip_use_case, approved_vendor):
        """Test trip creation with missing location."""
        request = CreateTripRequest(
            vendor_id=approved_vendor.id,
            location="",  # Empty location
            description="Beach tour",
            price=150.00,
            trip_date=(datetime.now() + timedelta(days=7)).isoformat()
        )
        
        with pytest.raises(ValueError, match="Location is required"):
            create_trip_use_case.execute(request)
    
    def test_create_trip_invalid_price(self, create_trip_use_case, approved_vendor):
        """Test trip creation with invalid price."""
        request = CreateTripRequest(
            vendor_id=approved_vendor.id,
            location="Goa Beach",
            description="Beach tour",
            price=-100.00,  # Negative price
            trip_date=(datetime.now() + timedelta(days=7)).isoformat()
        )
        
        with pytest.raises(ValueError, match="greater than 0"):
            create_trip_use_case.execute(request)
    
    def test_create_trip_invalid_date(self, create_trip_use_case, approved_vendor):
        """Test trip creation with invalid date."""
        request = CreateTripRequest(
            vendor_id=approved_vendor.id,
            location="Goa Beach",
            description="Beach tour",
            price=150.00,
            trip_date="invalid-date"
        )
        
        with pytest.raises(ValueError, match="Invalid trip date format"):
            create_trip_use_case.execute(request)
    
    def test_create_trip_invalid_capacity(self, create_trip_use_case, approved_vendor):
        """Test trip creation with invalid capacity."""
        request = CreateTripRequest(
            vendor_id=approved_vendor.id,
            location="Goa Beach",
            description="Beach tour",
            price=150.00,
            trip_date=(datetime.now() + timedelta(days=7)).isoformat(),
            max_capacity=0  # Invalid capacity
        )
        
        with pytest.raises(ValueError, match="greater than 0"):
            create_trip_use_case.execute(request)
    
    def test_create_trip_unapproved_vendor(self, db_session, create_trip_use_case):
        """Test trip creation by unapproved vendor."""
        # Create pending vendor
        vendor = VendorModel(
            id=str(uuid4()),
            email="pending@example.com",
            password_hash="hash",
            business_name="Pending Tours",
            phone="+919999999999",
            bank_account="1234567890",
            status=VendorStatus.PENDING
        )
        repo = VendorRepository(db_session)
        repo.save(vendor)
        
        request = CreateTripRequest(
            vendor_id=vendor.id,
            location="Goa Beach",
            description="Beach tour",
            price=150.00,
            trip_date=(datetime.now() + timedelta(days=7)).isoformat()
        )
        
        with pytest.raises(ValueError, match="Only approved vendors"):
            create_trip_use_case.execute(request)
    
    def test_create_trip_nonexistent_vendor(self, create_trip_use_case):
        """Test trip creation by non-existent vendor."""
        request = CreateTripRequest(
            vendor_id=str(uuid4()),  # Non-existent vendor
            location="Goa Beach",
            description="Beach tour",
            price=150.00,
            trip_date=(datetime.now() + timedelta(days=7)).isoformat()
        )
        
        with pytest.raises(ValueError, match="Vendor not found"):
            create_trip_use_case.execute(request)


class TestTripEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def trip_repo(self, db_session):
        """Create trip repository."""
        return TripRepository(db_session)
    
    def test_trip_with_very_high_price(self, trip_repo):
        """Test trip with very high price."""
        trip = TripModel(
            id=str(uuid4()),
            vendor_id=str(uuid4()),
            location="Luxury Tour",
            description="Ultra-luxury trip",
            price=999999.99,
            trip_date=datetime.now() + timedelta(days=7),
            max_capacity=5
        )
        
        saved = trip_repo.save(trip)
        assert saved.price == 999999.99
    
    def test_trip_with_very_small_price(self, trip_repo):
        """Test trip with very small price."""
        trip = TripModel(
            id=str(uuid4()),
            vendor_id=str(uuid4()),
            location="Budget Tour",
            description="Budget trip",
            price=0.01,
            trip_date=datetime.now() + timedelta(days=7),
            max_capacity=100
        )
        
        saved = trip_repo.save(trip)
        assert saved.price == 0.01
    
    def test_trip_with_long_description(self, trip_repo):
        """Test trip with very long description."""
        long_desc = "A" * 1000
        trip = TripModel(
            id=str(uuid4()),
            vendor_id=str(uuid4()),
            location="Goa",
            description=long_desc,
            price=150.00,
            trip_date=datetime.now() + timedelta(days=7),
            max_capacity=10
        )
        
        saved = trip_repo.save(trip)
        assert len(saved.description) == 1000
    
    def test_trip_far_in_future(self, trip_repo):
        """Test trip scheduled far in future."""
        far_future = datetime.now() + timedelta(days=365*2)  # 2 years
        trip = TripModel(
            id=str(uuid4()),
            vendor_id=str(uuid4()),
            location="Goa",
            description="Future tour",
            price=150.00,
            trip_date=far_future,
            max_capacity=10
        )
        
        saved = trip_repo.save(trip)
        assert saved.trip_date == far_future
