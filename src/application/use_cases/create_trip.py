"""
Create trip use case.
"""
from dataclasses import dataclass
from uuid import uuid4
from datetime import datetime


@dataclass
class CreateTripRequest:
    """Create trip request."""
    vendor_id: str
    location: str
    description: str
    price: float
    trip_date: str  # ISO format
    max_capacity: int = 10


@dataclass
class CreateTripResponse:
    """Create trip response."""
    trip_id: str
    vendor_id: str
    location: str
    price: float
    trip_date: str
    message: str


class CreateTripUseCase:
    """Use case for creating a trip."""
    
    def __init__(self, trip_repository, vendor_repository):
        self.trip_repository = trip_repository
        self.vendor_repository = vendor_repository
    
    def execute(self, request: CreateTripRequest) -> CreateTripResponse:
        """Execute trip creation."""
        # Validate vendor exists and is approved
        vendor = self.vendor_repository.find_by_id(request.vendor_id)
        if not vendor:
            raise ValueError("Vendor not found")
        
        from src.infrastructure.database.models import VendorStatus
        if vendor.status != VendorStatus.APPROVED:
            raise ValueError("Only approved vendors can create trips")
        
        # Validate trip data
        if not request.location:
            raise ValueError("Location is required")
        
        if request.price <= 0:
            raise ValueError("Price must be greater than 0")
        
        if request.max_capacity <= 0:
            raise ValueError("Capacity must be greater than 0")
        
        try:
            trip_date = datetime.fromisoformat(request.trip_date)
        except (ValueError, TypeError):
            raise ValueError("Invalid trip date format. Use ISO format: YYYY-MM-DDTHH:MM:SS")
        
        # Create trip
        from src.infrastructure.database.models import TripModel
        trip = TripModel(
            id=str(uuid4()),
            vendor_id=request.vendor_id,
            location=request.location,
            description=request.description,
            price=request.price,
            trip_date=trip_date,
            max_capacity=request.max_capacity,
            current_bookings=0
        )
        
        saved_trip = self.trip_repository.save(trip)
        
        return CreateTripResponse(
            trip_id=saved_trip.id,
            vendor_id=saved_trip.vendor_id,
            location=saved_trip.location,
            price=saved_trip.price,
            trip_date=saved_trip.trip_date.isoformat(),
            message="Trip created successfully!"
        )
