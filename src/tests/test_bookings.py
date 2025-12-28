"""
Unit tests for booking endpoints and use cases.
Tests: create, read, update, cancel bookings.
"""
import json
import pytest
from datetime import datetime, timedelta


class TestBookingEndpoints:
    """Test booking routes."""
    
    @pytest.fixture
    def authenticated_user(self, client):
        """Create and return authenticated user with token."""
        client.post('/api/v1/auth/register', json={
            'email': 'bookinguser@example.com',
            'password': 'SecurePass123!',
            'name': 'Booking User'
        })
        
        response = client.post('/api/v1/auth/login', json={
            'email': 'bookinguser@example.com',
            'password': 'SecurePass123!'
        })
        
        data = json.loads(response.data)
        return {
            'token': data['token'],
            'user_id': data['user_id']
        }
    
    def test_create_booking_success(self, client, authenticated_user):
        """Test successful booking creation."""
        headers = {'Authorization': f"Bearer {authenticated_user['token']}"}
        
        trip_date = (datetime.now() + timedelta(days=7)).isoformat()
        
        response = client.post('/api/v1/bookings', 
            json={
                'vendor_id': 'vendor123',
                'trip_date': trip_date,
                'location': 'New York',
                'total_price': 500.00,
                'notes': 'Test booking'
            },
            headers=headers
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'booking_id' in data
        assert data['status'] == 'pending'
    
    def test_create_booking_invalid_date(self, client, authenticated_user):
        """Test booking with past date."""
        headers = {'Authorization': f"Bearer {authenticated_user['token']}"}
        
        trip_date = (datetime.now() - timedelta(days=7)).isoformat()
        
        response = client.post('/api/v1/bookings',
            json={
                'vendor_id': 'vendor123',
                'trip_date': trip_date,
                'location': 'New York',
                'total_price': 500.00,
            },
            headers=headers
        )
        
        assert response.status_code == 400
    
    def test_create_booking_invalid_price(self, client, authenticated_user):
        """Test booking with invalid price."""
        headers = {'Authorization': f"Bearer {authenticated_user['token']}"}
        
        trip_date = (datetime.now() + timedelta(days=7)).isoformat()
        
        response = client.post('/api/v1/bookings',
            json={
                'vendor_id': 'vendor123',
                'trip_date': trip_date,
                'location': 'New York',
                'total_price': -100.00,
            },
            headers=headers
        )
        
        assert response.status_code == 400
    
    def test_get_booking_success(self, client, authenticated_user):
        """Test getting a specific booking."""
        headers = {'Authorization': f"Bearer {authenticated_user['token']}"}
        
        # Create booking first
        trip_date = (datetime.now() + timedelta(days=7)).isoformat()
        create_response = client.post('/api/v1/bookings',
            json={
                'vendor_id': 'vendor123',
                'trip_date': trip_date,
                'location': 'New York',
                'total_price': 500.00,
            },
            headers=headers
        )
        
        booking_id = json.loads(create_response.data)['booking_id']
        
        # Get booking
        response = client.get(f'/api/v1/bookings/{booking_id}', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['booking_id'] == booking_id
    
    def test_list_user_bookings(self, client, authenticated_user):
        """Test listing user's bookings."""
        headers = {'Authorization': f"Bearer {authenticated_user['token']}"}
        
        # Create multiple bookings
        trip_date = (datetime.now() + timedelta(days=7)).isoformat()
        for i in range(3):
            client.post('/api/v1/bookings',
                json={
                    'vendor_id': f'vendor{i}',
                    'trip_date': trip_date,
                    'location': f'Location {i}',
                    'total_price': 100.00 + i * 50,
                },
                headers=headers
            )
        
        # Get bookings list
        response = client.get('/api/v1/bookings', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'bookings' in data
        assert len(data['bookings']) >= 3
    
    def test_cancel_booking_success(self, client, authenticated_user):
        """Test successful booking cancellation."""
        headers = {'Authorization': f"Bearer {authenticated_user['token']}"}
        
        # Create booking
        trip_date = (datetime.now() + timedelta(days=7)).isoformat()
        create_response = client.post('/api/v1/bookings',
            json={
                'vendor_id': 'vendor123',
                'trip_date': trip_date,
                'location': 'New York',
                'total_price': 500.00,
            },
            headers=headers
        )
        
        booking_id = json.loads(create_response.data)['booking_id']
        
        # Cancel booking
        response = client.post(f'/api/v1/bookings/{booking_id}/cancel',
            json={'reason': 'Changed my mind'},
            headers=headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'cancelled'
