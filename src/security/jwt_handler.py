"""
JWT token handling and generation.
"""
import jwt
from datetime import datetime, timedelta


class JWTHandler:
    """Handler for JWT token operations."""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def generate_token(self, user_id: str, expires_in: int = 3600) -> str:
        """Generate a JWT token for a user."""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(seconds=expires_in),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        """Verify and decode a JWT token."""
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
