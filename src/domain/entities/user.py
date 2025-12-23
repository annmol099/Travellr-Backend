"""
User domain entity.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """User entity representing a platform user."""
    
    id: str
    email: str
    name: str
    phone: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    
    def deactivate(self):
        """Deactivate user account."""
        self.is_active = False
    
    def activate(self):
        """Activate user account."""
        self.is_active = True
