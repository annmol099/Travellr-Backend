"""
Worker orchestration and scheduling.
Manages worker tasks, scheduling, and event subscriptions.
"""
from datetime import datetime
from typing import Dict, Any, Callable
import logging
import schedule
import time
from threading import Thread

from notification_worker import NotificationWorker
from payroll_worker import PayrollWorker
from cleanup_worker import CleanupWorker

logger = logging.getLogger(__name__)


class WorkerScheduler:
    """Schedules and manages background workers."""
    
    def __init__(self):
        self.notification_worker = NotificationWorker()
        self.payroll_worker = PayrollWorker()
        self.cleanup_worker = CleanupWorker()
        self.scheduler_thread = None
        self.running = False
    
    def schedule_jobs(self):
        """Schedule all worker jobs."""
        # Notification jobs
        schedule.every().hour.do(self._handle_payment_reminders)
        
        # Payroll jobs
        schedule.every().monday.at("08:00").do(self._handle_weekly_payroll)
        schedule.every().day.at("00:00").do(self._check_monthly_payroll)
        
        # Cleanup jobs
        schedule.every().day.at("02:00").do(self._handle_maintenance)
        
        logger.info("All worker jobs scheduled")
    
    def start(self):
        """Start the scheduler."""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.schedule_jobs()
        self.running = True
        
        # Run scheduler in background thread
        self.scheduler_thread = Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Worker scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        logger.info("Worker scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop."""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                time.sleep(60)
    
    def _handle_payment_reminders(self):
        """Handle payment reminders (hourly)."""
        try:
            logger.info("Processing payment reminders...")
            # TODO: Query bookings with payment due soon
            # Send reminders via notification_worker
        except Exception as e:
            logger.error(f"Error handling payment reminders: {str(e)}")
    
    def _handle_weekly_payroll(self):
        """Handle weekly payroll (Monday 8 AM)."""
        try:
            logger.info("Processing weekly payroll...")
            result = self.payroll_worker.process_weekly_payroll()
            logger.info(f"Weekly payroll result: {result}")
        except Exception as e:
            logger.error(f"Error processing weekly payroll: {str(e)}")
    
    def _check_monthly_payroll(self):
        """Check if monthly payroll should run (1st of month at midnight)."""
        if datetime.now().day == 1:
            self._handle_monthly_payroll()
    
    def _handle_monthly_payroll(self):
        """Handle monthly payroll (1st of month)."""
        try:
            logger.info("Processing monthly payroll...")
            result = self.payroll_worker.process_monthly_payroll()
            logger.info(f"Monthly payroll result: {result}")
        except Exception as e:
            logger.error(f"Error processing monthly payroll: {str(e)}")
    
    def _handle_maintenance(self):
        """Handle daily maintenance (2 AM)."""
        try:
            logger.info("Running daily maintenance...")
            result = self.cleanup_worker.run_maintenance()
            logger.info(f"Maintenance result: {result}")
        except Exception as e:
            logger.error(f"Error running maintenance: {str(e)}")


class EventSubscriber:
    """Subscribes to domain events and triggers workers."""
    
    def __init__(self, notification_worker: NotificationWorker):
        self.notification_worker = notification_worker
    
    def on_booking_created(self, event: Dict[str, Any]) -> bool:
        """Handle booking created event."""
        try:
            logger.info(f"Booking created event: {event['booking_id']}")
            
            # Send confirmation notification
            self.notification_worker.send_booking_confirmation(
                user_id=event.get('user_id'),
                booking_id=event.get('booking_id'),
                booking_data={
                    'user_email': event.get('user_email'),
                    'user_phone': event.get('user_phone'),
                    'trip_date': event.get('trip_date'),
                    'total_price': event.get('total_price')
                }
            )
            
            return True
        except Exception as e:
            logger.error(f"Error handling booking created event: {str(e)}")
            return False
    
    def on_booking_cancelled(self, event: Dict[str, Any]) -> bool:
        """Handle booking cancelled event."""
        try:
            logger.info(f"Booking cancelled event: {event['booking_id']}")
            
            # Send cancellation notification
            self.notification_worker.send_booking_cancelled(
                user_id=event.get('user_id'),
                booking_id=event.get('booking_id'),
                booking_data={
                    'user_email': event.get('user_email'),
                    'user_phone': event.get('user_phone'),
                    'total_price': event.get('total_price')
                },
                reason=event.get('reason', '')
            )
            
            return True
        except Exception as e:
            logger.error(f"Error handling booking cancelled event: {str(e)}")
            return False
    
    def on_payment_processed(self, event: Dict[str, Any]) -> bool:
        """Handle payment processed event."""
        try:
            logger.info(f"Payment processed event: {event['payment_id']}")
            
            # TODO: Send payment confirmation to customer
            # TODO: Send vendor earnings notification
            
            return True
        except Exception as e:
            logger.error(f"Error handling payment processed event: {str(e)}")
            return False
    
    def on_vendor_earnings_available(self, event: Dict[str, Any]) -> bool:
        """Handle vendor earnings available event."""
        try:
            logger.info(f"Vendor earnings event: {event['vendor_id']}")
            
            # TODO: Trigger automatic payout if threshold met
            
            return True
        except Exception as e:
            logger.error(f"Error handling vendor earnings event: {str(e)}")
            return False


class WorkerManager:
    """Central manager for all workers."""
    
    def __init__(self, event_bus=None):
        self.event_bus = event_bus
        self.scheduler = WorkerScheduler()
        self.event_subscriber = EventSubscriber(
            notification_worker=self.scheduler.notification_worker
        )
        self._register_events()
    
    def _register_events(self):
        """Register event handlers."""
        if not self.event_bus:
            logger.warning("No event bus provided, event subscriptions skipped")
            return
        
        # Register event listeners
        self.event_bus.subscribe('booking.created', self.event_subscriber.on_booking_created)
        self.event_bus.subscribe('booking.cancelled', self.event_subscriber.on_booking_cancelled)
        self.event_bus.subscribe('payment.processed', self.event_subscriber.on_payment_processed)
        self.event_bus.subscribe('vendor.earnings_available', self.event_subscriber.on_vendor_earnings_available)
        
        logger.info("Event subscriptions registered")
    
    def start(self):
        """Start all workers."""
        self.scheduler.start()
        logger.info("Worker manager started")
    
    def stop(self):
        """Stop all workers."""
        self.scheduler.stop()
        logger.info("Worker manager stopped")


# Celery integration (if using Celery for async tasks)
"""
from celery import Celery, Task

celery_app = Celery(__name__)
celery_app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0'
)

@celery_app.task
def send_notification_async(worker_type: str, method: str, **kwargs):
    '''Async notification task for Celery.'''
    scheduler = WorkerScheduler()
    
    if worker_type == 'notification':
        worker = scheduler.notification_worker
        getattr(worker, method)(**kwargs)

@celery_app.task
def process_payroll_weekly():
    '''Weekly payroll task for Celery.'''
    scheduler = WorkerScheduler()
    return scheduler.payroll_worker.process_weekly_payroll()

@celery_app.task
def process_payroll_monthly():
    '''Monthly payroll task for Celery.'''
    scheduler = WorkerScheduler()
    return scheduler.payroll_worker.process_monthly_payroll()

@celery_app.task
def run_maintenance():
    '''Maintenance task for Celery.'''
    scheduler = WorkerScheduler()
    return scheduler.cleanup_worker.run_maintenance()

@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    '''Setup periodic tasks.'''
    # Weekly payroll - Monday at 8 AM
    sender.add_periodic_task(crontab(hour=8, minute=0, day_of_week=0), process_payroll_weekly.s())
    
    # Monthly payroll - 1st of month at midnight
    sender.add_periodic_task(crontab(hour=0, minute=0, day_of_month=1), process_payroll_monthly.s())
    
    # Daily maintenance - 2 AM
    sender.add_periodic_task(crontab(hour=2, minute=0), run_maintenance.s())
"""
