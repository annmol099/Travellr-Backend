"""
Pytest configuration and fixtures.
"""
import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app("testing")
    
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create database session for testing."""
    from app import db
    
    with app.app_context():
        # Create all tables
        db.create_all()
        yield db.session
        # Cleanup
        db.session.rollback()
        db.drop_all()

@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()
