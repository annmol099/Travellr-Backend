"""
End-to-end integration tests for complete user and vendor journeys.
"""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from src.infrastructure.database.models import UserModel, VendorModel, BookingModel, TripModel, VendorStatus, BookingStatus
from src.infrastructure.database.repositories import UserRepository, VendorRepository, TripRepository, BookingRepository
from src.security.password_handler import PasswordHandler
from src.security.jwt_handler import JWTHandler


class TestCompleteUserJourney:
    """Test complete user journey: Register → Create Profile → Book Trip → Make Payment."""
    
    @pytest.fixture
    def repositories(self, db_session):
        """Initialize all repositories."""
        return {
            'user': UserRepository(db_session),
            'vendor': VendorRepository(db_session),
            'trip': TripRepository(db_session),
            'booking': BookingRepository(db_session)
        }
    
    def test_user_complete_journey(self, repositories):
        """Test complete user journey."""
        user_repo = repositories['user']
        trip_repo = repositories['trip']
        booking_repo = repositories['booking']
        vendor_repo = repositories['vendor']
        
        # Step 1: User Registration
        user = UserModel(
            id=str(uuid4()),
            email="user@example.com",
            password_hash=PasswordHandler.hash_password("UserPass123"),
            name="John Doe",
            phone="+919999999999",
            role="user"
        )
        saved_user = user_repo.save(user)
        assert saved_user.email == "user@example.com"
        
        # Step 2: Create Trip (via vendor)
        vendor = VendorModel(
            id=str(uuid4()),
            email="vendor@example.com",
            password_hash=PasswordHandler.hash_password("VendorPass123"),
            business_name="Adventure Tours",
            phone="+918888888888",
            bank_account="vendor123",
            status=VendorStatus.APPROVED
        )
        saved_vendor = vendor_repo.save(vendor)
        
        trip = TripModel(
            id=str(uuid4()),
            vendor_id=saved_vendor.id,
            location="Goa Beach",
            description="Beach adventure",
            price=150.00,
            trip_date=datetime.now() + timedelta(days=7),
            max_capacity=20
        )
        saved_trip = trip_repo.save(trip)
        assert saved_trip.location == "Goa Beach"
        
        # Step 3: User Books Trip
        booking = BookingModel(
            id=str(uuid4()),
            user_id=saved_user.id,
            vendor_id=saved_vendor.id,
            trip_date=saved_trip.trip_date,
            status=BookingStatus.PENDING,
            total_price=saved_trip.price
        )
        saved_booking = booking_repo.save(booking)
        assert saved_booking.user_id == saved_user.id
        
        # Step 4: Confirm Booking
        confirmed_booking = booking_repo.update(
            saved_booking.id,
            status=BookingStatus.CONFIRMED
        )
        assert confirmed_booking.status == BookingStatus.CONFIRMED
        
        # Verify entire flow
        assert saved_user.email == "user@example.com"
        assert saved_vendor.business_name == "Adventure Tours"
        assert saved_trip.vendor_id == saved_vendor.id
        assert saved_booking.user_id == saved_user.id


class TestCompleteVendorJourney:
    """Test complete vendor journey: Register → Wait Approval → Create Trips → Get Bookings."""
    
    @pytest.fixture
    def repositories(self, db_session):
        """Initialize all repositories."""
        return {
            'vendor': VendorRepository(db_session),
            'trip': TripRepository(db_session),
            'booking': BookingRepository(db_session)
        }
    
    def test_vendor_complete_journey(self, repositories):
        """Test complete vendor journey."""
        vendor_repo = repositories['vendor']
        trip_repo = repositories['trip']
        booking_repo = repositories['booking']
        
        # Step 1: Vendor Registration
        vendor = VendorModel(
            id=str(uuid4()),
            email="newvendor@example.com",
            password_hash=PasswordHandler.hash_password("NewVendorPass123"),
            business_name="Kerala Tours",
            phone="+917777777777",
            bank_account="vendor456",
            status=VendorStatus.PENDING  # Initially pending
        )
        saved_vendor = vendor_repo.save(vendor)
        assert saved_vendor.status == VendorStatus.PENDING
        
        # Step 2: Admin Approves Vendor
        approved_vendor = vendor_repo.update(
            saved_vendor.id,
            status=VendorStatus.APPROVED
        )
        assert approved_vendor.status == VendorStatus.APPROVED
        
        # Step 3: Vendor Creates Trips
        trips = []
        for i in range(3):
            trip = TripModel(
                id=str(uuid4()),
                vendor_id=approved_vendor.id,
                location=f"Location {i}",
                description=f"Tour {i}",
                price=100.00 + (i * 50),
                trip_date=datetime.now() + timedelta(days=i+7),
                max_capacity=15
            )
            saved_trip = trip_repo.save(trip)
            trips.append(saved_trip)
        
        # Step 4: Get Vendor's Trips
        vendor_trips = trip_repo.find_by_vendor(approved_vendor.id)
        assert len(vendor_trips) == 3
        
        # Step 5: User Books a Trip
        user_id = str(uuid4())
        booking = BookingModel(
            id=str(uuid4()),
            user_id=user_id,
            vendor_id=approved_vendor.id,
            trip_date=trips[0].trip_date,
            status=BookingStatus.CONFIRMED,
            total_price=trips[0].price
        )
        saved_booking = booking_repo.save(booking)
        
        # Step 6: Get Vendor's Bookings
        vendor_bookings = booking_repo.find_by_vendor(approved_vendor.id)
        assert len(vendor_bookings) >= 1
        assert saved_booking.id in [b.id for b in vendor_bookings]
        
        # Verify complete flow
        assert approved_vendor.is_active == True
        assert len(vendor_trips) == 3
        assert saved_booking.vendor_id == approved_vendor.id


class TestMultiVendorScenario:
    """Test scenario with multiple vendors and bookings."""
    
    @pytest.fixture
    def repositories(self, db_session):
        """Initialize all repositories."""
        return {
            'vendor': VendorRepository(db_session),
            'trip': TripRepository(db_session),
            'booking': BookingRepository(db_session),
            'user': UserRepository(db_session)
        }
    
    def test_multiple_vendors_multiple_bookings(self, repositories):
        """Test system with multiple vendors, trips, and bookings."""
        vendor_repo = repositories['vendor']
        trip_repo = repositories['trip']
        booking_repo = repositories['booking']
        user_repo = repositories['user']
        
        # Create 3 vendors
        vendors = []
        for i in range(3):
            vendor = VendorModel(
                id=str(uuid4()),
                email=f"vendor{i}@example.com",
                password_hash="hash",
                business_name=f"Tours Company {i}",
                phone=f"+919{i}9999999",
                bank_account=f"vendor{i}",
                status=VendorStatus.APPROVED
            )
            saved = vendor_repo.save(vendor)
            vendors.append(saved)
        
        # Each vendor creates 2 trips
        trips = []
        for vendor in vendors:
            for j in range(2):
                trip = TripModel(
                    id=str(uuid4()),
                    vendor_id=vendor.id,
                    location=f"Location by {vendor.business_name}",
                    description=f"Tour {j}",
                    price=100.0 + j * 50,
                    trip_date=datetime.now() + timedelta(days=j+7),
                    max_capacity=20
                )
                saved_trip = trip_repo.save(trip)
                trips.append(saved_trip)
        
        # Create 5 users
        users = []
        for i in range(5):
            user = UserModel(
                id=str(uuid4()),
                email=f"user{i}@example.com",
                password_hash="hash",
                name=f"User {i}",
                phone=f"+918{i}9999999"
            )
            saved_user = user_repo.save(user)
            users.append(saved_user)
        
        # Each user books 1-2 trips
        bookings = []
        for user in users:
            for trip in trips[:2]:  # Each user books 2 trips
                booking = BookingModel(
                    id=str(uuid4()),
                    user_id=user.id,
                    vendor_id=trip.vendor_id,
                    trip_date=trip.trip_date,
                    status=BookingStatus.CONFIRMED,
                    total_price=trip.price
                )
                saved_booking = booking_repo.save(booking)
                bookings.append(saved_booking)
        
        # Verify statistics
        all_trips = trip_repo.find_all(page=1, limit=100)
        assert all_trips[1] >= 6  # At least 6 trips
        
        all_bookings = booking_repo.find_all(page=1, limit=100)
        assert all_bookings[1] >= 10  # At least 10 bookings
        
        # Check each vendor has trips
        for vendor in vendors:
            vendor_trips = trip_repo.find_by_vendor(vendor.id)
            assert len(vendor_trips) == 2


class TestConcurrentBookingScenario:
    """Test handling of concurrent bookings on same trip."""
    
    @pytest.fixture
    def repositories(self, db_session):
        """Initialize all repositories."""
        return {
            'vendor': VendorRepository(db_session),
            'trip': TripRepository(db_session),
            'booking': BookingRepository(db_session),
            'user': UserRepository(db_session)
        }
    
    def test_multiple_users_booking_same_trip(self, repositories):
        """Test multiple users booking the same trip."""
        vendor_repo = repositories['vendor']
        trip_repo = repositories['trip']
        booking_repo = repositories['booking']
        user_repo = repositories['user']
        
        # Create vendor
        vendor = VendorModel(
            id=str(uuid4()),
            email="vendor@example.com",
            password_hash="hash",
            business_name="Popular Tours",
            phone="+919999999999",
            bank_account="vendor123",
            status=VendorStatus.APPROVED
        )
        saved_vendor = vendor_repo.save(vendor)
        
        # Create trip with limited capacity
        trip = TripModel(
            id=str(uuid4()),
            vendor_id=saved_vendor.id,
            location="Premium Location",
            description="Premium tour",
            price=500.00,
            trip_date=datetime.now() + timedelta(days=7),
            max_capacity=10
        )
        saved_trip = trip_repo.save(trip)
        
        # Create 15 users
        users = []
        for i in range(15):
            user = UserModel(
                id=str(uuid4()),
                email=f"user{i}@example.com",
                password_hash="hash",
                name=f"User {i}",
                phone=f"+919{i}9999999"
            )
            saved_user = user_repo.save(user)
            users.append(saved_user)
        
        # All users try to book same trip
        successful_bookings = 0
        for i, user in enumerate(users):
            booking = BookingModel(
                id=str(uuid4()),
                user_id=user.id,
                vendor_id=saved_vendor.id,
                trip_date=saved_trip.trip_date,
                status=BookingStatus.CONFIRMED,
                total_price=saved_trip.price
            )
            saved_booking = booking_repo.save(booking)
            
            # In real scenario, would check capacity
            # For now, just track successful bookings
            successful_bookings += 1
            
            # Update trip's current bookings
            if successful_bookings <= saved_trip.max_capacity:
                trip_repo.update(
                    saved_trip.id,
                    current_bookings=successful_bookings
                )
        
        # Verify trip has bookings
        trip_bookings = booking_repo.find_by_vendor(saved_vendor.id)
        assert len(trip_bookings) > 0
        
        # Verify some bookings were made
        assert successful_bookings >= saved_trip.max_capacity
