"""
Payment gateway integrations.
"""


class PaymentGateway:
    """Abstract payment gateway interface."""
    
    def process_payment(self, amount: float, currency: str, payment_method: str) -> dict:
        """Process a payment."""
        raise NotImplementedError
    
    def refund_payment(self, transaction_id: str) -> dict:
        """Refund a payment."""
        raise NotImplementedError


class StripePaymentGateway(PaymentGateway):
    """Stripe payment gateway implementation."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def process_payment(self, amount: float, currency: str, payment_method: str) -> dict:
        """Process payment via Stripe."""
        # Implementation using Stripe API
        pass
    
    def refund_payment(self, transaction_id: str) -> dict:
        """Refund payment via Stripe."""
        # Implementation using Stripe API
        pass
