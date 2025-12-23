"""
Payroll worker for processing vendor payments.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from infrastructure.database.models import BookingModel, BookingStatus, PaymentModel


class PayrollWorker:
    """Worker for processing vendor payroll."""

    def __init__(self, db_session, vendor_repository, payment_service):
        self.db = db_session
        self.vendor_repository = vendor_repository
        self.payment_service = payment_service

    def process_weekly_payroll(self):
        """Process weekly vendor payroll."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)

        vendors = self.vendor_repository.get_active_vendors(self.db)
        processed = 0

        for vendor in vendors:
            amount = self.calculate_vendor_earnings(
                vendor.id, start_date, end_date
            )

            if amount <= 0:
                continue

            payment_response = self.payment_service.pay(
                vendor=vendor,
                amount=amount,
                reference="WEEKLY_PAYROLL"
            )

            if payment_response["status"] == "SUCCESS":
                self._mark_bookings_paid(vendor.id, start_date, end_date)
                processed += 1

        self.db.commit()

        return {"weekly_vendors_paid": processed}

    def process_monthly_payroll(self):
        """Process monthly vendor payroll."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30)

        vendors = self.vendor_repository.get_active_vendors(self.db)
        processed = 0

        for vendor in vendors:
            amount = self.calculate_vendor_earnings(
                vendor.id, start_date, end_date
            )

            if amount <= 0:
                continue

            payment_response = self.payment_service.pay(
                vendor=vendor,
                amount=amount,
                reference="MONTHLY_PAYROLL"
            )

            if payment_response["status"] == "SUCCESS":
                self._mark_bookings_paid(vendor.id, start_date, end_date)
                processed += 1

        self.db.commit()

        return {"monthly_vendors_paid": processed}

    def calculate_vendor_earnings(self, vendor_id: str, start_date, end_date):
        """Calculate earnings for a vendor in a period."""
        total = (
            self.db.query(func.coalesce(func.sum(BookingModel.total_price), 0))
            .filter(
                BookingModel.vendor_id == vendor_id,
                BookingModel.status == BookingStatus.COMPLETED,
                BookingModel.created_at.between(start_date, end_date),
            )
            .scalar()
        )

        return float(total)

    def _mark_bookings_paid(self, vendor_id, start_date, end_date):
        """Mark vendor bookings as paid."""
        self.db.query(BookingModel).filter(
            BookingModel.vendor_id == vendor_id,
            BookingModel.status == BookingStatus.COMPLETED,
            BookingModel.created_at.between(start_date, end_date),
        ).update(
            {"is_paid": True},
            synchronize_session=False
        )
