"""
Payment gateway integrations.
"""
import stripe
from typing import Dict, Optional


class PaymentGateway:
    """Abstract payment gateway interface."""
    
    def process_payment(self, amount: float, currency: str, payment_method: str) -> Dict:
        """Process a payment."""
        raise NotImplementedError
    
    def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> Dict:
        """Refund a payment."""
        raise NotImplementedError
    
    def get_payment_status(self, transaction_id: str) -> Dict:
        """Get payment status."""
        raise NotImplementedError


class StripePaymentGateway(PaymentGateway):
    """Stripe payment gateway implementation."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        stripe.api_key = api_key
    
    def process_payment(self, amount: float, currency: str = "usd", 
                       payment_method: str = None, metadata: Dict = None) -> Dict:
        """
        Process payment via Stripe.
        
        Args:
            amount: Amount in cents (e.g., 5000 = $50.00)
            currency: Currency code (default: usd)
            payment_method: Stripe payment method ID
            metadata: Additional metadata to attach to payment
        
        Returns:
            Dict with payment details including id, status, amount
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency.lower(),
                payment_method=payment_method,
                confirm=True,
                metadata=metadata or {}
            )
            
            return {
                "success": True,
                "transaction_id": intent.id,
                "status": intent.status,
                "amount": amount,
                "currency": currency,
                "created": intent.created
            }
            
        except stripe.error.CardError as e:
            return {
                "success": False,
                "error": "Card declined",
                "message": str(e),
                "status": "failed"
            }
        except stripe.error.RateLimitError as e:
            return {
                "success": False,
                "error": "Rate limited",
                "message": str(e),
                "status": "failed"
            }
        except stripe.error.InvalidRequestError as e:
            return {
                "success": False,
                "error": "Invalid request",
                "message": str(e),
                "status": "failed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Payment failed",
                "message": str(e),
                "status": "error"
            }
    
    def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> Dict:
        """
        Refund a payment via Stripe.
        
        Args:
            transaction_id: Stripe payment intent ID
            amount: Amount to refund in dollars (None = full refund)
        
        Returns:
            Dict with refund details
        """
        try:
            refund_params = {
                "payment_intent": transaction_id
            }
            
            if amount:
                refund_params["amount"] = int(amount * 100)
            
            refund = stripe.Refund.create(**refund_params)
            
            return {
                "success": True,
                "refund_id": refund.id,
                "status": refund.status,
                "amount": refund.amount / 100,
                "created": refund.created
            }
            
        except stripe.error.InvalidRequestError as e:
            return {
                "success": False,
                "error": "Refund failed",
                "message": str(e),
                "status": "failed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Refund error",
                "message": str(e),
                "status": "error"
            }
    
    def get_payment_status(self, transaction_id: str) -> Dict:
        """
        Get payment status from Stripe.
        
        Args:
            transaction_id: Stripe payment intent ID
        
        Returns:
            Dict with payment status details
        """
        try:
            intent = stripe.PaymentIntent.retrieve(transaction_id)
            
            return {
                "success": True,
                "transaction_id": intent.id,
                "status": intent.status,
                "amount": intent.amount / 100,
                "currency": intent.currency,
                "created": intent.created,
                "client_secret": intent.client_secret
            }
            
        except stripe.error.InvalidRequestError as e:
            return {
                "success": False,
                "error": "Payment not found",
                "message": str(e),
                "status": "not_found"
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Error fetching payment",
                "message": str(e),
                "status": "error"
            }


class MockPaymentGateway(PaymentGateway):
    """Mock payment gateway for testing."""
    
    def process_payment(self, amount: float, currency: str = "usd",
                       payment_method: str = None, metadata: Dict = None) -> Dict:
        """Mock payment processing."""
        import uuid
        
        return {
            "success": True,
            "transaction_id": str(uuid.uuid4()),
            "status": "succeeded",
            "amount": amount,
            "currency": currency,
            "created": None
        }
    
    def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> Dict:
        """Mock refund processing."""
        import uuid
        
        return {
            "success": True,
            "refund_id": str(uuid.uuid4()),
            "status": "succeeded",
            "amount": amount or 0,
            "created": None
        }
    
    def get_payment_status(self, transaction_id: str) -> Dict:
        """Mock payment status check."""
        return {
            "success": True,
            "transaction_id": transaction_id,
            "status": "succeeded",
            "amount": 0,
            "currency": "usd",
            "created": None
        }
