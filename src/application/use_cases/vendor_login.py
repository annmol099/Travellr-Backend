"""
Vendor login use case.
"""
from dataclasses import dataclass
from src.security.jwt_handler import JWTHandler


@dataclass
class VendorLoginRequest:
    """Vendor login request."""
    email: str
    password: str


@dataclass
class VendorLoginResponse:
    """Vendor login response."""
    vendor_id: str
    email: str
    business_name: str
    token: str
    status: str


class VendorLoginUseCase:
    """Use case for vendor login."""
    
    def __init__(self, vendor_repository, jwt_handler: JWTHandler):
        self.vendor_repository = vendor_repository
        self.jwt_handler = jwt_handler
    
    def execute(self, request: VendorLoginRequest) -> VendorLoginResponse:
        """Execute vendor login."""
        # Validate inputs
        if not request.email or not request.password:
            raise ValueError("Email and password are required")
        
        # Find vendor
        vendor = self.vendor_repository.find_by_email(request.email)
        if not vendor:
            raise ValueError("Invalid email or password")
        
        # Check if vendor is approved
        from src.infrastructure.database.models import VendorStatus
        if vendor.status != VendorStatus.APPROVED:
            raise ValueError(f"Account not approved. Current status: {vendor.status.value}")
        
        # Verify password
        from src.security.password_handler import PasswordHandler
        if not PasswordHandler.verify_password(request.password, vendor.password_hash):
            raise ValueError("Invalid email or password")
        
        # Generate JWT token
        token = self.jwt_handler.generate_token(
            user_id=vendor.id,
            email=vendor.email,
            role="vendor"
        )
        
        return VendorLoginResponse(
            vendor_id=vendor.id,
            email=vendor.email,
            business_name=vendor.business_name,
            token=token,
            status=vendor.status.value
        )
