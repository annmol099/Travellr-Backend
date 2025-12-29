"""
Vendor domain entity.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class VendorStatus(Enum):
    """Vendor status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


@dataclass
class Vendor:
    """Vendor domain entity."""
    
    id: str
    email: str
    password_hash: str
    business_name: str
    phone: str
    bank_account: str
    tax_id: str = ""
    status: VendorStatus = VendorStatus.PENDING
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def set_password(self, password: str) -> None:
        """Hash and set password."""
        from src.security.password_handler import PasswordHandler
        self.password_hash = PasswordHandler.hash_password(password)
    
    def check_password(self, password: str) -> bool:
        """Verify password."""
        from src.security.password_handler import PasswordHandler
        return PasswordHandler.verify_password(password, self.password_hash)
    
    def approve(self) -> None:
        """Approve vendor account."""
        self.status = VendorStatus.APPROVED
        self.updated_at = datetime.now()
    
    def reject(self) -> None:
        """Reject vendor account."""
        self.status = VendorStatus.REJECTED
        self.updated_at = datetime.now()
    
    def suspend(self) -> None:
        """Suspend vendor account."""
        self.status = VendorStatus.SUSPENDED
        self.updated_at = datetime.now()
    
    def is_approved(self) -> bool:
        """Check if vendor is approved."""
        return self.status == VendorStatus.APPROVED
