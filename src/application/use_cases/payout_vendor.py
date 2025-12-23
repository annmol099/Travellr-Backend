"""
Payout Vendor use case.
"""
from datetime import datetime, timedelta
from domain.events.domain_event import DomainEvent


class PayoutVendorRequest:
    """Request object for vendor payout."""
    
    def __init__(self, vendor_id: str, period: str = "monthly"):
        self.vendor_id = vendor_id
        self.period = period  # "weekly" or "monthly"


class PayoutVendorResponse:
    """Response object for vendor payout."""
    
    def __init__(self, vendor_id: str, amount: float, status: str, message: str):
        self.vendor_id = vendor_id
        self.amount = amount
        self.status = status
        self.message = message


class PayoutVendorUseCase:
    """Use case for processing vendor payouts."""
    
    def __init__(self, vendor_repository, payment_service, booking_repository, event_bus):
        self.vendor_repository = vendor_repository
        self.payment_service = payment_service
        self.booking_repository = booking_repository
        self.event_bus = event_bus
    
    def execute(self, request: PayoutVendorRequest) -> PayoutVendorResponse:
        """
        Execute the vendor payout use case.
        
        Steps:
        1. Fetch vendor
        2. Calculate earnings based on period
        3. Validate minimum payout amount
        4. Process payment to vendor
        5. Update vendor payment status
        6. Emit vendor payout event
        7. Return response
        """
        try:
            # Step 1: Fetch vendor
            vendor = self.vendor_repository.find_by_id(request.vendor_id)
            
            if not vendor:
                raise ValueError(f"Vendor {request.vendor_id} not found")
            
            # Step 2: Calculate earnings
            earnings = self._calculate_earnings(
                vendor_id=request.vendor_id,
                period=request.period
            )
            
            if earnings <= 0:
                raise ValueError("No earnings to payout for this period")
            
            # Step 3: Validate minimum payout amount (e.g., minimum $50)
            MIN_PAYOUT = 50
            if earnings < MIN_PAYOUT:
                raise ValueError(f"Earnings below minimum payout amount (${MIN_PAYOUT})")
            
            # Step 4: Process payment
            payment_result = self.payment_service.process_vendor_payment(
                vendor_id=request.vendor_id,
                amount=earnings,
                currency="USD"
            )
            
            if not payment_result:
                raise Exception("Payment processing failed")
            
            # Step 5: Update vendor payment status
            vendor.last_payout_date = datetime.now()
            self.vendor_repository.save(vendor)
            
            # Step 6: Emit vendor payout event
            event = DomainEvent(
                event_type="vendor.payout",
                aggregate_id=request.vendor_id,
                data={
                    "vendor_id": request.vendor_id,
                    "amount": earnings,
                    "period": request.period,
                    "timestamp": datetime.now().isoformat()
                }
            )
            self.event_bus.publish(event)
            
            # Step 7: Return response
            return PayoutVendorResponse(
                vendor_id=request.vendor_id,
                amount=earnings,
                status="completed",
                message=f"Payout of ${earnings} processed successfully"
            )
            
        except Exception as e:
            raise Exception(f"Failed to process vendor payout: {str(e)}")
    
    def _calculate_earnings(self, vendor_id: str, period: str) -> float:
        """
        Calculate vendor earnings for the given period.
        
        Formula: Sum of (booking.total_price * commission_rate)
        Commission rate: 20% (platform takes 20%, vendor gets 80%)
        """
        COMMISSION_RATE = 0.80  # Vendor gets 80%
        
        # Get date range based on period
        now = datetime.now()
        if period == "weekly":
            start_date = now - timedelta(days=7)
        elif period == "monthly":
            start_date = now - timedelta(days=30)
        else:
            raise ValueError(f"Invalid period: {period}")
        
        # Fetch bookings for vendor in this period
        bookings = self.booking_repository.find_by_vendor_id_and_date_range(
            vendor_id=vendor_id,
            start_date=start_date,
            end_date=now
        )
        
        # Calculate total earnings
        total_earnings = 0
        for booking in bookings:
            if booking.status.value == "completed":  # Only completed bookings
                total_earnings += booking.total_price * COMMISSION_RATE
        
        return round(total_earnings, 2)

