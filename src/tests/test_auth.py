"""
Unit tests for authentication endpoints.
Tests: register, login, logout, token validation.
"""
import json
import pytest
from datetime import datetime, timedelta


class TestAuthEndpoints:
    """Test authentication routes."""
    
    def test_register_user_success(self, client):
        """Test successful user registration."""
        response = client.post('/api/v1/auth/register', json={
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'name': 'Test User'
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'user_id' in data
        assert data['email'] == 'newuser@example.com'
    
    def test_register_user_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post('/api/v1/auth/register', json={
            'email': 'invalid-email',
            'password': 'SecurePass123!',
            'name': 'Test User'
        })
        
        assert response.status_code == 400
    
    def test_register_user_weak_password(self, client):
        """Test registration with weak password."""
        response = client.post('/api/v1/auth/register', json={
            'email': 'newuser@example.com',
            'password': '123',
            'name': 'Test User'
        })
        
        assert response.status_code == 400
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email."""
        # Register first user
        client.post('/api/v1/auth/register', json={
            'email': 'duplicate@example.com',
            'password': 'SecurePass123!',
            'name': 'First User'
        })
        
        # Try to register with same email
        response = client.post('/api/v1/auth/register', json={
            'email': 'duplicate@example.com',
            'password': 'SecurePass123!',
            'name': 'Second User'
        })
        
        assert response.status_code == 409
    
    def test_login_success(self, client):
        """Test successful login."""
        # Register user first
        client.post('/api/v1/auth/register', json={
            'email': 'testuser@example.com',
            'password': 'SecurePass123!',
            'name': 'Test User'
        })
        
        # Login
        response = client.post('/api/v1/auth/login', json={
            'email': 'testuser@example.com',
            'password': 'SecurePass123!'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data
        assert 'user_id' in data
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/api/v1/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'WrongPassword'
        })
        
        assert response.status_code == 401
    
    def test_login_wrong_password(self, client):
        """Test login with wrong password."""
        # Register user
        client.post('/api/v1/auth/register', json={
            'email': 'testuser@example.com',
            'password': 'SecurePass123!',
            'name': 'Test User'
        })
        
        # Try login with wrong password
        response = client.post('/api/v1/auth/login', json={
            'email': 'testuser@example.com',
            'password': 'WrongPassword'
        })
        
        assert response.status_code == 401


class TestTokenValidation:
    """Test JWT token validation."""
    
    def test_protected_route_without_token(self, client):
        """Test accessing protected route without token."""
        response = client.get('/api/v1/users/profile')
        
        assert response.status_code == 401
    
    def test_protected_route_with_invalid_token(self, client):
        """Test accessing protected route with invalid token."""
        headers = {'Authorization': 'Bearer invalid.token.here'}
        response = client.get('/api/v1/users/profile', headers=headers)
        
        assert response.status_code == 401
    
    def test_protected_route_with_valid_token(self, client):
        """Test accessing protected route with valid token."""
        # Register and login
        client.post('/api/v1/auth/register', json={
            'email': 'testuser@example.com',
            'password': 'SecurePass123!',
            'name': 'Test User'
        })
        
        login_response = client.post('/api/v1/auth/login', json={
            'email': 'testuser@example.com',
            'password': 'SecurePass123!'
        })
        
        token = json.loads(login_response.data)['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get('/api/v1/users/profile', headers=headers)
        
        assert response.status_code == 200


class TestLogout:
    """Test logout functionality."""
    
    def test_logout_success(self, client):
        """Test successful logout."""
        # Register and login first
        client.post('/api/v1/auth/register', json={
            'email': 'testuser@example.com',
            'password': 'SecurePass123!',
            'name': 'Test User'
        })
        
        login_response = client.post('/api/v1/auth/login', json={
            'email': 'testuser@example.com',
            'password': 'SecurePass123!'
        })
        
        token = json.loads(login_response.data)['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.post('/api/v1/auth/logout', headers=headers)
        
        assert response.status_code == 200
