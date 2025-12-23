"""
Payment domain service.
"""


class PaymentService:
    """Domain service for payment operations."""
    
    def __init__(self, payment_gateway):
        self.payment_gateway = payment_gateway
    
    def process_payment(self, booking_id: str, amount: float) -> bool:
        """Process payment for a booking."""
        # Delegate to payment gateway
        pass
    
    def refund_payment(self, payment_id: str) -> bool:
        """Refund a payment."""
        # Delegate to payment gateway
        pass
