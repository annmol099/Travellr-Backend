"""
Trips API routes.
"""
from flask import Blueprint, request, jsonify
from src.application.use_cases.create_trip import CreateTripUseCase, CreateTripRequest
from src.infrastructure.database.repositories import TripRepository, VendorRepository
from src.middlewares.auth_middleware import token_required
from flask import current_app


trips_bp = Blueprint('trips', __name__, url_prefix='/api/v1/trips')


@trips_bp.route('/', methods=['POST'])
@token_required
def create_trip():
    """Create a new trip (vendor only)."""
    try:
        data = request.get_json()
        
        required_fields = ['vendor_id', 'location', 'price', 'trip_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        trip_repo = TripRepository(current_app.db.session)
        vendor_repo = VendorRepository(current_app.db.session)
        use_case = CreateTripUseCase(trip_repo, vendor_repo)
        
        request_obj = CreateTripRequest(
            vendor_id=data['vendor_id'],
            location=data['location'],
            description=data.get('description', ''),
            price=float(data['price']),
            trip_date=data['trip_date'],
            max_capacity=int(data.get('max_capacity', 10))
        )
        
        response = use_case.execute(request_obj)
        
        return jsonify({
            'trip_id': response.trip_id,
            'vendor_id': response.vendor_id,
            'location': response.location,
            'price': response.price,
            'trip_date': response.trip_date,
            'message': response.message
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Trip creation failed: ' + str(e)}), 500


@trips_bp.route('/<trip_id>', methods=['GET'])
def get_trip(trip_id):
    """Get trip details."""
    try:
        trip_repo = TripRepository(current_app.db.session)
        trip = trip_repo.find_by_id(trip_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        return jsonify({
            'trip_id': trip.id,
            'vendor_id': trip.vendor_id,
            'location': trip.location,
            'description': trip.description,
            'price': trip.price,
            'trip_date': trip.trip_date.isoformat(),
            'max_capacity': trip.max_capacity,
            'current_bookings': trip.current_bookings,
            'available_spots': trip.max_capacity - trip.current_bookings
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trips_bp.route('/', methods=['GET'])
def list_trips():
    """List all trips with pagination."""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        trip_repo = TripRepository(current_app.db.session)
        trips, total = trip_repo.find_all(page, limit)
        
        return jsonify({
            'trips': [
                {
                    'trip_id': trip.id,
                    'vendor_id': trip.vendor_id,
                    'location': trip.location,
                    'price': trip.price,
                    'trip_date': trip.trip_date.isoformat(),
                    'available_spots': trip.max_capacity - trip.current_bookings
                }
                for trip in trips
            ],
            'total': total,
            'page': page,
            'limit': limit
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trips_bp.route('/<trip_id>', methods=['PUT'])
@token_required
def update_trip(trip_id):
    """Update trip (vendor only)."""
    try:
        data = request.get_json()
        trip_repo = TripRepository(current_app.db.session)
        
        trip = trip_repo.find_by_id(trip_id)
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        # Update allowed fields
        allowed_fields = ['location', 'description', 'price', 'max_capacity']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        updated = trip_repo.update(trip_id, **update_data)
        
        return jsonify({
            'message': 'Trip updated successfully',
            'trip_id': updated.id,
            'location': updated.location,
            'price': updated.price
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trips_bp.route('/<trip_id>', methods=['DELETE'])
@token_required
def delete_trip(trip_id):
    """Delete trip (vendor only)."""
    try:
        trip_repo = TripRepository(current_app.db.session)
        
        if not trip_repo.delete(trip_id):
            return jsonify({'error': 'Trip not found'}), 404
        
        return jsonify({'message': 'Trip deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
