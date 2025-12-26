   """
Cleanup worker for maintenance and database housekeeping tasks.
Archives old data, deletes expired sessions, cleans test data.
"""
from datetime import datetime, timedelta
from typing import Dict, List
import logging
import gzip
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class CleanupWorker:
    """Worker for cleanup and maintenance tasks."""
    
    # Configuration
    ARCHIVE_BOOKING_AGE_DAYS = 365  # Archive bookings older than 1 year
    DELETE_SESSION_AGE_DAYS = 30    # Delete sessions older than 30 days
    ARCHIVE_LOG_AGE_DAYS = 90       # Archive logs older than 90 days
    
    def __init__(self, booking_repository=None, session_repository=None, 
                 archive_storage=None, log_directory=None):
        self.booking_repo = booking_repository
        self.session_repo = session_repository
        self.archive_storage = archive_storage
        self.log_directory = log_directory or "logs/"
    
    def run_maintenance(self) -> Dict:
        """
        Run all cleanup tasks.
        Scheduled to run daily at 2 AM.
        
        Returns:
            Dict with results of all cleanup tasks
        """
        try:
            logger.info("Starting daily maintenance cleanup")
            
            results = {
                "timestamp": datetime.now().isoformat(),
                "tasks": {}
            }
            
            # Run all cleanup tasks
            results["tasks"]["archive_bookings"] = self.archive_completed_bookings()
            results["tasks"]["delete_sessions"] = self.cleanup_old_sessions()
            results["tasks"]["cleanup_test_data"] = self.cleanup_test_data()
            results["tasks"]["compress_logs"] = self.compress_old_logs()
            
            logger.info(f"Maintenance cleanup completed: {results}")
            return results
        
        except Exception as e:
            logger.error(f"Error during maintenance: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            }
    
    def archive_completed_bookings(self) -> Dict:
        """
        Archive completed bookings older than 1 year.
        Moves data to archive table instead of deleting.
        
        Returns:
            Archive operation results
        """
        try:
            logger.info("Starting booking archival")
            
            cutoff_date = datetime.now() - timedelta(days=self.ARCHIVE_BOOKING_AGE_DAYS)
            archived_count = 0
            
            # TODO: Query bookings older than cutoff_date with status='completed'
            old_bookings = [
                # {"id": "book1", "completed_at": datetime(2023, 1, 1)},
            ]
            
            for booking in old_bookings:
                try:
                    # Move to archive table
                    if self.archive_storage:
                        self.archive_storage.save_archive("bookings", booking)
                    
                    # Delete from main table
                    if self.booking_repo:
                        self.booking_repo.delete(booking["id"])
                    
                    archived_count += 1
                    logger.info(f"Archived booking {booking['id']}")
                
                except Exception as e:
                    logger.error(f"Error archiving booking {booking['id']}: {str(e)}")
            
            result = {
                "status": "completed",
                "archived_count": archived_count,
                "cutoff_date": cutoff_date.isoformat()
            }
            logger.info(f"Booking archival result: {result}")
            return result
        
        except Exception as e:
            logger.error(f"Error in archival process: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def cleanup_old_sessions(self) -> Dict:
        """
        Delete user sessions older than 30 days.
        Frees up database space and improves security.
        
        Returns:
            Cleanup operation results
        """
        try:
            logger.info("Starting session cleanup")
            
            cutoff_date = datetime.now() - timedelta(days=self.DELETE_SESSION_AGE_DAYS)
            deleted_count = 0
            
            # TODO: Query old sessions
            old_sessions = [
                # {"id": "sess1", "created_at": datetime(2025, 10, 1)},
            ]
            
            for session in old_sessions:
                try:
                    if self.session_repo:
                        self.session_repo.delete(session["id"])
                    deleted_count += 1
                    logger.info(f"Deleted session {session['id']}")
                
                except Exception as e:
                    logger.error(f"Error deleting session: {str(e)}")
            
            result = {
                "status": "completed",
                "deleted_count": deleted_count,
                "cutoff_date": cutoff_date.isoformat()
            }
            logger.info(f"Session cleanup result: {result}")
            return result
        
        except Exception as e:
            logger.error(f"Error in session cleanup: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def cleanup_test_data(self) -> Dict:
        """
        Remove all test data marked with test_run_id or test_user flag.
        Keeps database clean from testing artifacts.
        
        Returns:
            Cleanup operation results
        """
        try:
            logger.info("Starting test data cleanup")
            
            deleted_counts = {
                "test_bookings": 0,
                "test_payments": 0,
                "test_users": 0
            }
            
            # TODO: Query and delete all records with test flags
            # From bookings table
            test_bookings = []
            for booking in test_bookings:
                try:
                    if self.booking_repo:
                        self.booking_repo.delete(booking["id"])
                    deleted_counts["test_bookings"] += 1
                except Exception as e:
                    logger.error(f"Error deleting test booking: {str(e)}")
            
            # From payments table (TODO)
            # From users table (TODO)
            
            result = {
                "status": "completed",
                "deleted_counts": deleted_counts,
                "total_deleted": sum(deleted_counts.values())
            }
            logger.info(f"Test data cleanup result: {result}")
            return result
        
        except Exception as e:
            logger.error(f"Error in test data cleanup: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def compress_old_logs(self, days: int = 90) -> Dict:
        """
        Compress log files older than specified days.
        Reduces disk space usage significantly (90% compression typical).
        
        Args:
            days: Days before compression (default 90)
        
        Returns:
            Compression operation results
        """
        try:
            logger.info(f"Starting log compression for logs older than {days} days")
            
            cutoff_date = datetime.now() - timedelta(days=days)
            compressed_count = 0
            total_compressed_size = 0
            
            # Check if log directory exists
            log_path = Path(self.log_directory)
            if not log_path.exists():
                logger.warning(f"Log directory not found: {self.log_directory}")
                return {"status": "skipped", "reason": "Log directory not found"}
            
            # Find old log files
            for log_file in log_path.glob("*.log"):
                try:
                    # Check file modification time
                    file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    
                    if file_mtime < cutoff_date:
                        # Compress file
                        compressed_file = f"{log_file}.gz"
                        
                        with open(log_file, 'rb') as f_in:
                            with gzip.open(compressed_file, 'wb') as f_out:
                                f_out.writelines(f_in)
                        
                        # Get size reduction
                        original_size = log_file.stat().st_size
                        compressed_size = Path(compressed_file).stat().st_size
                        total_compressed_size += (original_size - compressed_size)
                        
                        # Delete original
                        log_file.unlink()
                        
                        compressed_count += 1
                        logger.info(f"Compressed {log_file.name} "
                                  f"({original_size} → {compressed_size} bytes)")
                
                except Exception as e:
                    logger.error(f"Error compressing {log_file}: {str(e)}")
            
            result = {
                "status": "completed",
                "compressed_count": compressed_count,
                "space_saved_bytes": total_compressed_size,
                "space_saved_mb": round(total_compressed_size / (1024 * 1024), 2)
            }
            logger.info(f"Log compression result: {result}")
            return result
        
        except Exception as e:
            logger.error(f"Error in log compression: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def cleanup_expired_bookings(self, days: int = 7) -> Dict:
        """
        Delete bookings that expired (trip date passed).
        Removes no-show bookings after specified grace period.
        
        Args:
            days: Grace period after trip date
        
        Returns:
            Cleanup operation results
        """
        try:
            logger.info(f"Cleaning up expired bookings (>{days} days past trip date)")
            
            grace_date = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            # TODO: Query bookings with trip_date < grace_date and status not completed
            expired_bookings = []
            
            for booking in expired_bookings:
                try:
                    if self.booking_repo:
                        self.booking_repo.delete(booking["id"])
                    deleted_count += 1
                    logger.info(f"Deleted expired booking {booking['id']}")
                
                except Exception as e:
                    logger.error(f"Error deleting expired booking: {str(e)}")
            
            result = {
                "status": "completed",
                "deleted_count": deleted_count,
                "grace_period_days": days
            }
            logger.info(f"Expired booking cleanup result: {result}")
            return result
        
        except Exception as e:
            logger.error(f"Error in expired booking cleanup: {str(e)}")
            return {"status": "failed", "error": str(e)}
