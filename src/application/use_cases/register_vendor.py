"""
Register vendor use case.
"""
from dataclasses import dataclass
from uuid import uuid4
from src.domain.entities.vendor import Vendor, VendorStatus


@dataclass
class RegisterVendorRequest:
    """Register vendor request."""
    email: str
    password: str
    business_name: str
    phone: str
    bank_account: str
    tax_id: str = ""


@dataclass
class RegisterVendorResponse:
    """Register vendor response."""
    vendor_id: str
    email: str
    business_name: str
    status: str
    message: str


class RegisterVendorUseCase:
    """Use case for vendor registration."""
    
    def __init__(self, vendor_repository):
        self.vendor_repository = vendor_repository
    
    def execute(self, request: RegisterVendorRequest) -> RegisterVendorResponse:
        """Execute vendor registration."""
        # Validate inputs
        if not request.email or "@" not in request.email:
            raise ValueError("Invalid email format")
        
        if not request.password or len(request.password) < 6:
            raise ValueError("Password must be at least 6 characters")
        
        if not request.business_name or len(request.business_name) < 2:
            raise ValueError("Business name is required")
        
        if not request.phone:
            raise ValueError("Phone is required")
        
        if not request.bank_account:
            raise ValueError("Bank account is required")
        
        # Check if vendor already exists
        if self.vendor_repository.exists(request.email):
            raise ValueError("Email already registered")
        
        # Create vendor
        vendor = Vendor(
            id=str(uuid4()),
            email=request.email.lower(),
            password_hash="",  # Will be set below
            business_name=request.business_name,
            phone=request.phone,
            bank_account=request.bank_account,
            tax_id=request.tax_id,
            status=VendorStatus.PENDING
        )
        
        # Set password
        vendor.set_password(request.password)
        
        # Save to database
        from src.infrastructure.database.models import VendorModel
        vendor_model = VendorModel(
            id=vendor.id,
            email=vendor.email,
            password_hash=vendor.password_hash,
            business_name=vendor.business_name,
            phone=vendor.phone,
            bank_account=vendor.bank_account,
            tax_id=vendor.tax_id,
            status=vendor.status
        )
        
        saved_vendor = self.vendor_repository.save(vendor_model)
        
        return RegisterVendorResponse(
            vendor_id=saved_vendor.id,
            email=saved_vendor.email,
            business_name=saved_vendor.business_name,
            status=saved_vendor.status.value,
            message="Registration successful! Awaiting admin approval."
        )
