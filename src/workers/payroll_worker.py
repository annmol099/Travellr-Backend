"""
Payroll worker for processing vendor payments.
Calculates earnings, processes payments, and generates receipts.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class PayrollWorker:
    """Worker for processing vendor payroll."""
    
    COMMISSION_RATE = 0.20  # Platform takes 20%, vendor gets 80%
    MINIMUM_PAYOUT = 50.0  # Minimum $50 to trigger payout
    
    def __init__(self, vendor_repository=None, booking_repository=None, 
                 payment_repository=None, payment_gateway=None, notification_service=None):
        self.vendor_repo = vendor_repository
        self.booking_repo = booking_repository
        self.payment_repo = payment_repository
        self.payment_gateway = payment_gateway
        self.notification_service = notification_service
    
    def process_weekly_payroll(self) -> Dict:
        """
        Process weekly vendor payroll.
        Runs every Monday at 8 AM.
        
        Returns:
            Dict with processing results
        """
        try:
            logger.info("Starting weekly payroll processing")
            
            # Calculate last 7 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            results = self._process_payroll_period(
                start_date=start_date,
                end_date=end_date,
                period="weekly"
            )
            
            logger.info(f"Weekly payroll completed: {results}")
            return results
        
        except Exception as e:
            logger.error(f"Error processing weekly payroll: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def process_monthly_payroll(self) -> Dict:
        """
        Process monthly vendor payroll.
        Runs on 1st of each month.
        
        Returns:
            Dict with processing results
        """
        try:
            logger.info("Starting monthly payroll processing")
            
            # Calculate last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            results = self._process_payroll_period(
                start_date=start_date,
                end_date=end_date,
                period="monthly"
            )
            
            logger.info(f"Monthly payroll completed: {results}")
            return results
        
        except Exception as e:
            logger.error(f"Error processing monthly payroll: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def _process_payroll_period(self, start_date: datetime, end_date: datetime, 
                                period: str) -> Dict:
        """
        Process payroll for a specific period.
        
        Args:
            start_date: Period start date
            end_date: Period end date
            period: 'weekly' or 'monthly'
        
        Returns:
            Processing results
        """
        total_processed = 0
        total_amount = 0.0
        successful_payouts = []
        failed_payouts = []
        
        try:
            # Get all vendors (TODO: Filter active vendors)
            vendors = []
            
            for vendor_id in vendors:
                # Calculate earnings for this period
                earnings = self.calculate_vendor_earnings(
                    vendor_id=vendor_id,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if earnings and earnings['amount'] >= self.MINIMUM_PAYOUT:
                    # Process payment
                    payout_result = self._process_vendor_payout(
                        vendor_id=vendor_id,
                        amount=earnings['amount'],
                        bookings=earnings['bookings'],
                        period=period
                    )
                    
                    if payout_result['success']:
                        successful_payouts.append({
                            'vendor_id': vendor_id,
                            'amount': earnings['amount']
                        })
                        total_amount += earnings['amount']
                        total_processed += 1
                    else:
                        failed_payouts.append({
                            'vendor_id': vendor_id,
                            'amount': earnings['amount'],
                            'error': payout_result.get('error')
                        })
        
        except Exception as e:
            logger.error(f"Error in payroll period processing: {str(e)}")
        
        return {
            "status": "completed",
            "period": period,
            "total_processed": total_processed,
            "total_amount": total_amount,
            "successful_payouts": successful_payouts,
            "failed_payouts": failed_payouts,
            "timestamp": datetime.now().isoformat()
        }
    
    def calculate_vendor_earnings(self, vendor_id: str, start_date: datetime, 
                                  end_date: datetime) -> Optional[Dict]:
        """
        Calculate vendor earnings for a period.
        Uses 80/20 commission split (vendor gets 80%).
        
        Args:
            vendor_id: Vendor ID
            start_date: Period start
            end_date: Period end
        
        Returns:
            Dict with earnings and booking list, or None
        """
        try:
            # Get completed bookings for this vendor in period
            # TODO: Query booking_repo for completed bookings
            bookings = [
                # {"id": "book1", "total_price": 100},
                # {"id": "book2", "total_price": 150},
            ]
            
            if not bookings:
                return None
            
            # Calculate total revenue from bookings
            total_revenue = sum(b.get('total_price', 0) for b in bookings)
            
            # Apply 80/20 split (vendor gets 80%)
            vendor_earnings = total_revenue * (1 - self.COMMISSION_RATE)
            
            return {
                "vendor_id": vendor_id,
                "amount": vendor_earnings,
                "total_revenue": total_revenue,
                "commission_rate": self.COMMISSION_RATE,
                "bookings": bookings,
                "booking_count": len(bookings)
            }
        
        except Exception as e:
            logger.error(f"Error calculating earnings for vendor {vendor_id}: {str(e)}")
            return None
    
    def _process_vendor_payout(self, vendor_id: str, amount: float, 
                               bookings: List, period: str) -> Dict:
        """
        Process actual payout to vendor.
        
        Args:
            vendor_id: Vendor ID
            amount: Payout amount
            bookings: List of bookings for this payout
            period: 'weekly' or 'monthly'
        
        Returns:
            Payout result
        """
        try:
            # Process payment via payment gateway
            payment_result = self.payment_gateway.process_payment(
                amount=amount,
                recipient_type="vendor",
                recipient_id=vendor_id,
                description=f"{period.title()} payout for {len(bookings)} bookings"
            ) if self.payment_gateway else {"success": True}
            
            if not payment_result.get('success'):
                return {"success": False, "error": payment_result.get('error')}
            
            # Create payment record
            payment_record = {
                "vendor_id": vendor_id,
                "amount": amount,
                "type": "vendor_payout",
                "period": period,
                "booking_ids": [b.get('id') for b in bookings],
                "transaction_id": payment_result.get('transaction_id'),
                "status": "completed",
                "created_at": datetime.now().isoformat()
            }
            
            # Save payment record to database
            if self.payment_repo:
                self.payment_repo.save(payment_record)
            
            # Generate receipt
            receipt = self._generate_payout_receipt(payment_record)
            
            # Send notification to vendor
            if self.notification_service:
                self.notification_service.send_vendor_payout(
                    vendor_id=vendor_id,
                    amount=amount,
                    receipt=receipt
                )
            
            logger.info(f"Payout processed for vendor {vendor_id}: ${amount}")
            return {"success": True, "payment_record": payment_record}
        
        except Exception as e:
            logger.error(f"Error processing payout for vendor {vendor_id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _generate_payout_receipt(self, payment_record: Dict) -> Dict:
        """
        Generate payout receipt for vendor.
        
        Args:
            payment_record: Payment record details
        
        Returns:
            Receipt details
        """
        receipt = {
            "receipt_id": f"RECEIPT-{payment_record.get('vendor_id')}-{datetime.now().timestamp()}",
            "vendor_id": payment_record.get('vendor_id'),
            "amount": payment_record.get('amount'),
            "period": payment_record.get('period'),
            "booking_count": len(payment_record.get('booking_ids', [])),
            "booking_ids": payment_record.get('booking_ids', []),
            "transaction_id": payment_record.get('transaction_id'),
            "issued_at": datetime.now().isoformat(),
            "status": "issued"
        }
        
        logger.info(f"Receipt generated: {receipt['receipt_id']}")
        return receipt
