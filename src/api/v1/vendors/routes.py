"""
Vendor API routes.
"""
from flask import Blueprint, request, jsonify
from src.application.use_cases.register_vendor import RegisterVendorUseCase, RegisterVendorRequest
from src.application.use_cases.vendor_login import VendorLoginUseCase, VendorLoginRequest
from src.application.use_cases.create_trip import CreateTripUseCase, CreateTripRequest
from src.infrastructure.database.repositories import VendorRepository, TripRepository
from src.security.jwt_handler import JWTHandler
from src.middlewares.auth_middleware import token_required
from flask import current_app


vendors_bp = Blueprint('vendors', __name__, url_prefix='/api/v1/vendors')


@vendors_bp.route('/register', methods=['POST'])
def register_vendor():
    """Register a new vendor."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'business_name', 'phone', 'bank_account']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create use case
        vendor_repo = VendorRepository(current_app.db.session)
        use_case = RegisterVendorUseCase(vendor_repo)
        
        request_obj = RegisterVendorRequest(
            email=data['email'],
            password=data['password'],
            business_name=data['business_name'],
            phone=data['phone'],
            bank_account=data['bank_account'],
            tax_id=data.get('tax_id', '')
        )
        
        response = use_case.execute(request_obj)
        
        return jsonify({
            'vendor_id': response.vendor_id,
            'email': response.email,
            'business_name': response.business_name,
            'status': response.status,
            'message': response.message
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Registration failed: ' + str(e)}), 500


@vendors_bp.route('/login', methods=['POST'])
def login_vendor():
    """Login vendor and get JWT token."""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        vendor_repo = VendorRepository(current_app.db.session)
        jwt_handler = JWTHandler()
        use_case = VendorLoginUseCase(vendor_repo, jwt_handler)
        
        request_obj = VendorLoginRequest(
            email=data['email'],
            password=data['password']
        )
        
        response = use_case.execute(request_obj)
        
        return jsonify({
            'vendor_id': response.vendor_id,
            'email': response.email,
            'business_name': response.business_name,
            'token': response.token,
            'status': response.status
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': 'Login failed: ' + str(e)}), 500


@vendors_bp.route('/<vendor_id>', methods=['GET'])
@token_required
def get_vendor(vendor_id):
    """Get vendor profile."""
    try:
        vendor_repo = VendorRepository(current_app.db.session)
        vendor = vendor_repo.find_by_id(vendor_id)
        
        if not vendor:
            return jsonify({'error': 'Vendor not found'}), 404
        
        return jsonify({
            'vendor_id': vendor.id,
            'email': vendor.email,
            'business_name': vendor.business_name,
            'phone': vendor.phone,
            'status': vendor.status.value,
            'is_active': vendor.is_active,
            'created_at': vendor.created_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@vendors_bp.route('/<vendor_id>', methods=['PUT'])
@token_required
def update_vendor(vendor_id):
    """Update vendor profile."""
    try:
        data = request.get_json()
        vendor_repo = VendorRepository(current_app.db.session)
        
        # Only vendor can update their own profile
        vendor = vendor_repo.find_by_id(vendor_id)
        if not vendor:
            return jsonify({'error': 'Vendor not found'}), 404
        
        # Update allowed fields
        allowed_fields = ['phone', 'business_name', 'bank_account']
        for field in allowed_fields:
            if field in data:
                setattr(vendor, field, data[field])
        
        updated = vendor_repo.update(vendor_id, **data)
        
        return jsonify({
            'message': 'Vendor updated successfully',
            'vendor_id': updated.id,
            'business_name': updated.business_name,
            'phone': updated.phone
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@vendors_bp.route('/<vendor_id>/trips', methods=['GET'])
def get_vendor_trips(vendor_id):
    """Get all trips for a vendor."""
    try:
        trip_repo = TripRepository(current_app.db.session)
        trips = trip_repo.find_by_vendor(vendor_id)
        
        return jsonify({
            'vendor_id': vendor_id,
            'trips': [
                {
                    'trip_id': trip.id,
                    'location': trip.location,
                    'price': trip.price,
                    'trip_date': trip.trip_date.isoformat(),
                    'max_capacity': trip.max_capacity,
                    'current_bookings': trip.current_bookings
                }
                for trip in trips
            ],
            'total': len(trips)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
