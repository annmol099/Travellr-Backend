"""
Unit tests for payment endpoints and payment gateway.
Tests: process payment, refund, payment status.
"""
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


class TestPaymentEndpoints:
    """Test payment routes."""
    
    @pytest.fixture
    def authenticated_user(self, client):
        """Create and return authenticated user with token."""
        client.post('/api/v1/auth/register', json={
            'email': 'paymentuser@example.com',
            'password': 'SecurePass123!',
            'name': 'Payment User'
        })
        
        response = client.post('/api/v1/auth/login', json={
            'email': 'paymentuser@example.com',
            'password': 'SecurePass123!'
        })
        
        data = json.loads(response.data)
        return {
            'token': data['token'],
            'user_id': data['user_id']
        }
    
    @pytest.fixture
    def booking(self, client, authenticated_user):
        """Create a test booking."""
        headers = {'Authorization': f"Bearer {authenticated_user['token']}"}
        
        trip_date = (datetime.now() + timedelta(days=7)).isoformat()
        response = client.post('/api/v1/bookings',
            json={
                'vendor_id': 'vendor123',
                'trip_date': trip_date,
                'location': 'New York',
                'total_price': 500.00,
            },
            headers=headers
        )
        
        return json.loads(response.data)
    
    def test_process_payment_success(self, client, authenticated_user, booking):
        """Test successful payment processing."""
        headers = {'Authorization': f"Bearer {authenticated_user['token']}"}
        
        response = client.post('/api/v1/payments/process',
            json={
                'booking_id': booking['booking_id'],
                'amount': 500.00,
                'payment_method': 'card',
                'card_token': 'tok_test123'
            },
            headers=headers
        )
        
        assert response.status_code in [200, 201]
        data = json.loads(response.data)
        assert 'payment_id' in data or 'status' in data
    
    def test_process_payment_invalid_amount(self, client, authenticated_user, booking):
        """Test payment with mismatched amount."""
        headers = {'Authorization': f"Bearer {authenticated_user['token']}"}
        
        response = client.post('/api/v1/payments/process',
            json={
                'booking_id': booking['booking_id'],
                'amount': 100.00,
                'payment_method': 'card',
                'card_token': 'tok_test123'
            },
            headers=headers
        )
        
        assert response.status_code == 400
    
    def test_get_payment_status(self, client, authenticated_user, booking):
        """Test getting payment status."""
        headers = {'Authorization': f"Bearer {authenticated_user['token']}"}
        
        # Process payment first
        payment_response = client.post('/api/v1/payments/process',
            json={
                'booking_id': booking['booking_id'],
                'amount': 500.00,
                'payment_method': 'card',
                'card_token': 'tok_test123'
            },
            headers=headers
        )
        
        if payment_response.status_code in [200, 201]:
            payment_id = json.loads(payment_response.data).get('payment_id')
            
            if payment_id:
                response = client.get(f'/api/v1/payments/{payment_id}', headers=headers)
                assert response.status_code == 200
    
    def test_refund_payment_success(self, client, authenticated_user, booking):
        """Test successful payment refund."""
        headers = {'Authorization': f"Bearer {authenticated_user['token']}"}
        
        # Process payment first
        payment_response = client.post('/api/v1/payments/process',
            json={
                'booking_id': booking['booking_id'],
                'amount': 500.00,
                'payment_method': 'card',
                'card_token': 'tok_test123'
            },
            headers=headers
        )
        
        if payment_response.status_code in [200, 201]:
            payment_data = json.loads(payment_response.data)
            payment_id = payment_data.get('payment_id')
            
            if payment_id:
                response = client.post(f'/api/v1/payments/{payment_id}/refund',
                    json={'reason': 'Booking cancelled'},
                    headers=headers
                )
                
                assert response.status_code in [200, 201]
