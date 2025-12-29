"""
Vendor management tests.
"""
import pytest
from uuid import uuid4
from src.domain.entities.vendor import Vendor, VendorStatus
from src.infrastructure.database.models import VendorModel, VendorStatus as DBVendorStatus
from src.application.use_cases.register_vendor import RegisterVendorUseCase, RegisterVendorRequest
from src.application.use_cases.vendor_login import VendorLoginUseCase, VendorLoginRequest
from src.infrastructure.database.repositories import VendorRepository
from src.security.jwt_handler import JWTHandler
from src.security.password_handler import PasswordHandler


class TestVendorEntity:
    """Test Vendor domain entity."""
    
    def test_vendor_creation(self):
        """Test creating a vendor entity."""
        vendor = Vendor(
            id=str(uuid4()),
            email="vendor@example.com",
            password_hash="",
            business_name="Test Tours",
            phone="+919999999999",
            bank_account="1234567890"
        )
        
        assert vendor.email == "vendor@example.com"
        assert vendor.business_name == "Test Tours"
        assert vendor.status == VendorStatus.PENDING
    
    def test_vendor_set_password(self):
        """Test setting and verifying vendor password."""
        vendor = Vendor(
            id=str(uuid4()),
            email="vendor@example.com",
            password_hash="",
            business_name="Test Tours",
            phone="+919999999999",
            bank_account="1234567890"
        )
        
        vendor.set_password("TestPass123")
        assert vendor.password_hash != ""
        assert vendor.check_password("TestPass123") == True
        assert vendor.check_password("WrongPass") == False
    
    def test_vendor_approve(self):
        """Test vendor approval."""
        vendor = Vendor(
            id=str(uuid4()),
            email="vendor@example.com",
            password_hash="",
            business_name="Test Tours",
            phone="+919999999999",
            bank_account="1234567890"
        )
        
        assert vendor.status == VendorStatus.PENDING
        vendor.approve()
        assert vendor.status == VendorStatus.APPROVED
        assert vendor.is_approved() == True
    
    def test_vendor_reject(self):
        """Test vendor rejection."""
        vendor = Vendor(
            id=str(uuid4()),
            email="vendor@example.com",
            password_hash="",
            business_name="Test Tours",
            phone="+919999999999",
            bank_account="1234567890"
        )
        
        vendor.reject()
        assert vendor.status == VendorStatus.REJECTED
        assert vendor.is_approved() == False
    
    def test_vendor_suspend(self):
        """Test vendor suspension."""
        vendor = Vendor(
            id=str(uuid4()),
            email="vendor@example.com",
            password_hash="",
            business_name="Test Tours",
            phone="+919999999999",
            bank_account="1234567890"
        )
        
        vendor.suspend()
        assert vendor.status == VendorStatus.SUSPENDED


class TestVendorRepository:
    """Test VendorRepository."""
    
    @pytest.fixture
    def vendor_repo(self, db_session):
        """Create vendor repository."""
        return VendorRepository(db_session)
    
    @pytest.fixture
    def sample_vendor(self):
        """Create sample vendor."""
        return VendorModel(
            id=str(uuid4()),
            email="vendor@example.com",
            password_hash=PasswordHandler.hash_password("TestPass123"),
            business_name="Test Tours",
            phone="+919999999999",
            bank_account="1234567890"
        )
    
    def test_save_vendor(self, vendor_repo, sample_vendor):
        """Test saving a vendor."""
        saved = vendor_repo.save(sample_vendor)
        
        assert saved.id == sample_vendor.id
        assert saved.email == "vendor@example.com"
        assert saved.business_name == "Test Tours"
    
    def test_find_by_id(self, vendor_repo, sample_vendor):
        """Test finding vendor by ID."""
        vendor_repo.save(sample_vendor)
        
        found = vendor_repo.find_by_id(sample_vendor.id)
        assert found is not None
        assert found.email == "vendor@example.com"
    
    def test_find_by_email(self, vendor_repo, sample_vendor):
        """Test finding vendor by email."""
        vendor_repo.save(sample_vendor)
        
        found = vendor_repo.find_by_email("vendor@example.com")
        assert found is not None
        assert found.id == sample_vendor.id
    
    def test_find_by_email_not_found(self, vendor_repo):
        """Test finding non-existent vendor."""
        found = vendor_repo.find_by_email("nonexistent@example.com")
        assert found is None
    
    def test_vendor_exists(self, vendor_repo, sample_vendor):
        """Test checking vendor existence."""
        vendor_repo.save(sample_vendor)
        
        assert vendor_repo.exists("vendor@example.com") == True
        assert vendor_repo.exists("nonexistent@example.com") == False
    
    def test_update_vendor(self, vendor_repo, sample_vendor):
        """Test updating vendor."""
        vendor_repo.save(sample_vendor)
        
        updated = vendor_repo.update(sample_vendor.id, phone="+918888888888")
        assert updated.phone == "+918888888888"
    
    def test_delete_vendor(self, vendor_repo, sample_vendor):
        """Test deleting vendor."""
        vendor_repo.save(sample_vendor)
        
        deleted = vendor_repo.delete(sample_vendor.id)
        assert deleted == True
        
        found = vendor_repo.find_by_id(sample_vendor.id)
        assert found is None
    
    def test_find_pending_vendors(self, vendor_repo):
        """Test finding pending vendors."""
        vendor1 = VendorModel(
            id=str(uuid4()),
            email="vendor1@example.com",
            password_hash="hash",
            business_name="Tours 1",
            phone="+919999999999",
            bank_account="123",
            status=DBVendorStatus.PENDING
        )
        
        vendor2 = VendorModel(
            id=str(uuid4()),
            email="vendor2@example.com",
            password_hash="hash",
            business_name="Tours 2",
            phone="+919999999999",
            bank_account="456",
            status=DBVendorStatus.APPROVED
        )
        
        vendor_repo.save(vendor1)
        vendor_repo.save(vendor2)
        
        pending = vendor_repo.find_pending()
        assert len(pending) >= 1
        assert vendor1.id in [v.id for v in pending]


class TestVendorRegistration:
    """Test vendor registration use case."""
    
    @pytest.fixture
    def register_use_case(self, db_session):
        """Create registration use case."""
        vendor_repo = VendorRepository(db_session)
        return RegisterVendorUseCase(vendor_repo)
    
    def test_register_vendor_success(self, register_use_case):
        """Test successful vendor registration."""
        request = RegisterVendorRequest(
            email="newvendor@example.com",
            password="SecurePass123",
            business_name="New Tours",
            phone="+919999999999",
            bank_account="1234567890"
        )
        
        response = register_use_case.execute(request)
        
        assert response.email == "newvendor@example.com"
        assert response.business_name == "New Tours"
        assert response.status == "pending"
        assert response.message == "Registration successful! Awaiting admin approval."
    
    def test_register_vendor_invalid_email(self, register_use_case):
        """Test registration with invalid email."""
        request = RegisterVendorRequest(
            email="invalid-email",
            password="SecurePass123",
            business_name="New Tours",
            phone="+919999999999",
            bank_account="1234567890"
        )
        
        with pytest.raises(ValueError, match="Invalid email format"):
            register_use_case.execute(request)
    
    def test_register_vendor_weak_password(self, register_use_case):
        """Test registration with weak password."""
        request = RegisterVendorRequest(
            email="vendor@example.com",
            password="short",
            business_name="New Tours",
            phone="+919999999999",
            bank_account="1234567890"
        )
        
        with pytest.raises(ValueError, match="at least 6 characters"):
            register_use_case.execute(request)
    
    def test_register_vendor_missing_fields(self, register_use_case):
        """Test registration with missing fields."""
        request = RegisterVendorRequest(
            email="vendor@example.com",
            password="SecurePass123",
            business_name="",  # Missing
            phone="+919999999999",
            bank_account="1234567890"
        )
        
        with pytest.raises(ValueError):
            register_use_case.execute(request)
    
    def test_register_vendor_duplicate_email(self, register_use_case):
        """Test registration with duplicate email."""
        # Register first vendor
        request1 = RegisterVendorRequest(
            email="vendor@example.com",
            password="SecurePass123",
            business_name="Tours 1",
            phone="+919999999999",
            bank_account="1234567890"
        )
        register_use_case.execute(request1)
        
        # Try to register with same email
        request2 = RegisterVendorRequest(
            email="vendor@example.com",
            password="SecurePass123",
            business_name="Tours 2",
            phone="+919999999999",
            bank_account="9876543210"
        )
        
        with pytest.raises(ValueError, match="already registered"):
            register_use_case.execute(request2)


class TestVendorLogin:
    """Test vendor login use case."""
    
    @pytest.fixture
    def login_use_case(self, db_session):
        """Create login use case."""
        vendor_repo = VendorRepository(db_session)
        jwt_handler = JWTHandler()
        return VendorLoginUseCase(vendor_repo, jwt_handler)
    
    @pytest.fixture
    def approved_vendor(self, db_session):
        """Create an approved vendor."""
        vendor = VendorModel(
            id=str(uuid4()),
            email="vendor@example.com",
            password_hash=PasswordHandler.hash_password("TestPass123"),
            business_name="Test Tours",
            phone="+919999999999",
            bank_account="1234567890",
            status=DBVendorStatus.APPROVED
        )
        repo = VendorRepository(db_session)
        return repo.save(vendor)
    
    def test_vendor_login_success(self, login_use_case, approved_vendor):
        """Test successful vendor login."""
        request = VendorLoginRequest(
            email="vendor@example.com",
            password="TestPass123"
        )
        
        response = login_use_case.execute(request)
        
        assert response.email == "vendor@example.com"
        assert response.token is not None
        assert len(response.token) > 0
    
    def test_vendor_login_wrong_password(self, login_use_case, approved_vendor):
        """Test login with wrong password."""
        request = VendorLoginRequest(
            email="vendor@example.com",
            password="WrongPass"
        )
        
        with pytest.raises(ValueError, match="Invalid email or password"):
            login_use_case.execute(request)
    
    def test_vendor_login_nonexistent(self, login_use_case):
        """Test login with non-existent vendor."""
        request = VendorLoginRequest(
            email="nonexistent@example.com",
            password="TestPass123"
        )
        
        with pytest.raises(ValueError, match="Invalid email or password"):
            login_use_case.execute(request)
    
    def test_vendor_login_not_approved(self, db_session, login_use_case):
        """Test login when vendor not approved."""
        vendor = VendorModel(
            id=str(uuid4()),
            email="pending@example.com",
            password_hash=PasswordHandler.hash_password("TestPass123"),
            business_name="Pending Tours",
            phone="+919999999999",
            bank_account="1234567890",
            status=DBVendorStatus.PENDING
        )
        repo = VendorRepository(db_session)
        repo.save(vendor)
        
        request = VendorLoginRequest(
            email="pending@example.com",
            password="TestPass123"
        )
        
        with pytest.raises(ValueError, match="not approved"):
            login_use_case.execute(request)
