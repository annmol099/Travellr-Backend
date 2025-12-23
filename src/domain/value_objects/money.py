"""
Money value object.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    """Money value object representing an amount in a specific currency."""
    
    amount: float
    currency: str = "USD"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
    
    def add(self, other: "Money") -> "Money":
        """Add two money values."""
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: "Money") -> "Money":
        """Subtract two money values."""
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        return Money(self.amount - other.amount, self.currency)
