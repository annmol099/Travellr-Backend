"""
Integration tests for API endpoints.
Tests: Full flow from API request to response.
"""
import json
import pytest
from datetime import datetime, timedelta


class TestBookingIntegration:
    """Integration tests for booking flow."""
    
    def test_complete_booking_flow(self, client):
        """Test complete flow: register → login → create booking."""
        # Register
        register_response = client.post('/api/v1/auth/register', json={
            'email': 'integration@example.com',
            'password': 'SecurePass123!',
            'name': 'Integration Test'
        })
        assert register_response.status_code == 201
        
        # Login
        login_response = client.post('/api/v1/auth/login', json={
            'email': 'integration@example.com',
            'password': 'SecurePass123!'
        })
        assert login_response.status_code == 200
        token = json.loads(login_response.data)['token']
        
        # Create booking
        headers = {'Authorization': f'Bearer {token}'}
        trip_date = (datetime.now() + timedelta(days=7)).isoformat()
        
        booking_response = client.post('/api/v1/bookings',
            json={
                'vendor_id': 'vendor123',
                'trip_date': trip_date,
                'location': 'New York',
                'total_price': 500.00,
            },
            headers=headers
        )
        assert booking_response.status_code == 201
        
        booking = json.loads(booking_response.data)
        assert 'booking_id' in booking
    
    def test_booking_and_payment_flow(self, client):
        """Test flow: create booking → process payment."""
        # Setup: Register and login
        client.post('/api/v1/auth/register', json={
            'email': 'paymentflow@example.com',
            'password': 'SecurePass123!',
            'name': 'Payment Flow Test'
        })
        
        login_response = client.post('/api/v1/auth/login', json={
            'email': 'paymentflow@example.com',
            'password': 'SecurePass123!'
        })
        token = json.loads(login_response.data)['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create booking
        trip_date = (datetime.now() + timedelta(days=7)).isoformat()
        booking_response = client.post('/api/v1/bookings',
            json={
                'vendor_id': 'vendor123',
                'trip_date': trip_date,
                'location': 'New York',
                'total_price': 500.00,
            },
            headers=headers
        )
        booking = json.loads(booking_response.data)
        booking_id = booking['booking_id']
        
        # Process payment
        payment_response = client.post('/api/v1/payments/process',
            json={
                'booking_id': booking_id,
                'amount': 500.00,
                'payment_method': 'card',
                'card_token': 'tok_test123'
            },
            headers=headers
        )
        
        assert payment_response.status_code in [200, 201]


class TestErrorHandling:
    """Integration tests for error handling."""
    
    def test_404_not_found(self, client):
        """Test 404 error handling."""
        response = client.get('/api/v1/bookings/nonexistent123')
        
        assert response.status_code == 404
    
    def test_400_bad_request(self, client):
        """Test 400 error handling."""
        response = client.post('/api/v1/auth/register', json={
            'email': 'invalid-email',
            'password': 'short',
            'name': 'Test'
        })
        
        assert response.status_code == 400
    
    def test_401_unauthorized(self, client):
        """Test 401 error handling."""
        response = client.get('/api/v1/users/profile')
        
        assert response.status_code == 401
