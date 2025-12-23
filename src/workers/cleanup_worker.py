"""
Cleanup worker for maintenance tasks.
"""

from datetime import datetime, timezone
from infrastructure.database.models import BookingModel, BookingStatus


class CleanupWorker:
    """Worker for cleanup and maintenance tasks."""

    def __init__(self, database_session):
        self.db = database_session

    def cleanup_expired_bookings(self):
        """
        Delete expired bookings:
        - status = PENDING
        - trip_date already passed
        """
        now = datetime.now(timezone.utc)

        deleted_count = (
            self.db.query(BookingModel)
            .filter(
                BookingModel.status == BookingStatus.PENDING,
                BookingModel.trip_date < now
            )
            .delete(synchronize_session=False)
        )

        self.db.commit()

        return {
            "expired_bookings_deleted": deleted_count
        }

    def cleanup_old_logs(self, days: int = 30):
        """
        Placeholder:
        No log table exists yet.
        """
        return {
            "logs_deleted": 0,
            "message": "Log model not implemented yet"
        }

    def archive_completed_bookings(self):
        """
        Soft-archive completed bookings:
        - mark them as archived instead of moving to another table
        """
        archived_count = (
            self.db.query(BookingModel)
            .filter(
                BookingModel.status == BookingStatus.COMPLETED,
                BookingModel.is_archived == False
            )
            .update(
                {"is_archived": True},
                synchronize_session=False
            )
        )

        self.db.commit()

        return {
            "bookings_archived": archived_count
        }
