"""
Example: Integrating Workers with Flask App
Shows how to wire workers into your Travellr Flask application.
"""

# ============================================================================
# OPTION 1: SIMPLE INTEGRATION (Development)
# ============================================================================

from flask import Flask
from src.workers.worker_orchestration import WorkerManager
from src.infrastructure.event_bus import EventBus

def create_app():
    """Create Flask app with workers integrated."""
    app = Flask(__name__)
    
    # Create event bus
    event_bus = EventBus()
    app.event_bus = event_bus
    
    # Create and start worker manager
    worker_manager = WorkerManager(event_bus=event_bus)
    worker_manager.start()
    app.worker_manager = worker_manager
    
    # Register error handler
    @app.teardown_appcontext
    def cleanup(error):
        if error:
            print(f\"App error: {error}\")
    
    return app

# Usage in views:
# ============================================================================
# from flask import current_app
#
# @app.route('/bookings', methods=['POST'])
# def create_booking():
#     # Create booking
#     booking = Booking.create(request.json)
#     db.session.add(booking)
#     db.session.commit()
#     
#     # Publish event (NotificationWorker automatically sends confirmation)
#     current_app.event_bus.publish('booking.created', {
#         'booking_id': booking.id,
#         'user_id': booking.user_id,
#         'user_email': booking.user.email,
#         'user_phone': booking.user.phone,
#         'trip_date': booking.trip_date.isoformat(),
#         'total_price': booking.total_price
#     })
#     
#     return jsonify({'id': booking.id}), 201


# ============================================================================
# OPTION 2: PRODUCTION INTEGRATION (With APScheduler)
# ============================================================================

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

def create_app_production():
    \"\"\"Create Flask app with APScheduler for worker jobs.\"\"\"
    app = Flask(__name__)
    
    # Create event bus
    event_bus = EventBus()
    app.event_bus = event_bus
    
    # Setup APScheduler for jobs
    scheduler = BackgroundScheduler()
    
    # Schedule payroll jobs
    scheduler.add_job(
        func=app.worker_manager.scheduler._handle_weekly_payroll,
        trigger='cron',
        day_of_week='mon',
        hour=8,
        minute=0,
        id='weekly_payroll'
    )
    
    scheduler.add_job(
        func=app.worker_manager.scheduler._check_monthly_payroll,
        trigger='cron',
        hour=0,
        minute=0,
        id='monthly_payroll_check'
    )
    
    scheduler.add_job(
        func=app.worker_manager.scheduler._handle_maintenance,
        trigger='cron',
        hour=2,
        minute=0,
        id='daily_maintenance'
    )
    
    # Schedule payment reminders every hour
    scheduler.add_job(
        func=app.worker_manager.scheduler._handle_payment_reminders,
        trigger='interval',
        hours=1,
        id='hourly_payment_reminders'
    )
    
    scheduler.start()
    app.scheduler = scheduler
    
    # Graceful shutdown
    import atexit
    atexit.register(lambda: scheduler.shutdown())
    
    return app


# ============================================================================
# OPTION 3: ENTERPRISE INTEGRATION (With Celery)
# ============================================================================

from celery import Celery
from celery.schedules import crontab

def create_celery_app(app):
    \"\"\"Configure Celery for async tasks.\"\"\"
    celery = Celery(
        app.import_name,
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

# In separate file: celery_tasks.py
# ============================================================================
# from celery_app import celery
# from src.workers.notification_worker import NotificationWorker
# from src.workers.payroll_worker import PayrollWorker
# from src.workers.cleanup_worker import CleanupWorker
#
# @celery.task
# def send_notification_async(notification_type, user_id, booking_id, data):
#     \"\"\"Async notification task.\"\"\"
#     worker = NotificationWorker()
#     
#     if notification_type == 'confirmation':
#         return worker.send_booking_confirmation(user_id, booking_id, data)
#     elif notification_type == 'cancelled':
#         return worker.send_booking_cancelled(user_id, booking_id, data)
#     elif notification_type == 'reminder':
#         return worker.send_payment_reminder(user_id, booking_id, data)
#
# @celery.task
# def process_weekly_payroll():
#     \"\"\"Weekly payroll async task.\"\"\"
#     worker = PayrollWorker()
#     return worker.process_weekly_payroll()
#
# @celery.task
# def process_monthly_payroll():
#     \"\"\"Monthly payroll async task.\"\"\"
#     worker = PayrollWorker()
#     return worker.process_monthly_payroll()
#
# @celery.task
# def run_cleanup():
#     \"\"\"Daily cleanup async task.\"\"\"
#     worker = CleanupWorker()
#     return worker.run_maintenance()
#
# # Configure periodic tasks
# celery.conf.beat_schedule = {
#     'weekly-payroll': {
#         'task': 'celery_tasks.process_weekly_payroll',
#         'schedule': crontab(day_of_week=0, hour=8, minute=0),  # Monday 8 AM
#     },
#     'monthly-payroll': {
#         'task': 'celery_tasks.process_monthly_payroll',
#         'schedule': crontab(day_of_month=1, hour=0, minute=0),  # 1st of month
#     },
#     'daily-cleanup': {
#         'task': 'celery_tasks.run_cleanup',
#         'schedule': crontab(hour=2, minute=0),  # 2 AM daily
#     },
# }
#
# # Usage in views:
# # from celery_tasks import send_notification_async
# # 
# # @app.route('/bookings', methods=['POST'])
# # def create_booking():
# #     booking = create_booking_in_db(request.json)
# #     
# #     # Send notification asynchronously
# #     send_notification_async.delay(
# #         'confirmation',
# #         booking.user_id,
# #         booking.id,
# #         {...}
# #     )
# #     
# #     return jsonify({'id': booking.id}), 201


# ============================================================================
# EXAMPLE: Using Workers in Use Cases
# ============================================================================

# In src/application/use_cases/booking_use_case.py

class CreateBookingUseCase:
    \"\"\"Create booking and trigger notifications.\"\"\"
    
    def __init__(self, booking_repo, user_repo, event_bus):
        self.booking_repo = booking_repo
        self.user_repo = user_repo
        self.event_bus = event_bus
    
    def execute(self, request_data):
        \"\"\"Create booking and publish event.\"\"\"
        # Validate
        if not request_data.get('user_id'):
            raise ValueError('user_id required')
        
        # Create booking
        booking = Booking(
            user_id=request_data['user_id'],
            trip_date=request_data['trip_date'],
            total_price=request_data['total_price']
        )
        
        # Get user details for notification
        user = self.user_repo.get(request_data['user_id'])
        
        # Save
        self.booking_repo.save(booking)
        
        # PUBLISH EVENT - NotificationWorker listens and sends confirmation
        self.event_bus.publish('booking.created', {
            'booking_id': booking.id,
            'user_id': user.id,
            'user_email': user.email,
            'user_phone': user.phone,
            'trip_date': booking.trip_date.isoformat(),
            'total_price': booking.total_price
        })
        
        return booking


class CancelBookingUseCase:
    \"\"\"Cancel booking and trigger notifications.\"\"\"
    
    def __init__(self, booking_repo, event_bus):
        self.booking_repo = booking_repo
        self.event_bus = event_bus
    
    def execute(self, booking_id, reason):
        \"\"\"Cancel booking and publish event.\"\"\"
        booking = self.booking_repo.get(booking_id)
        booking.status = 'cancelled'
        self.booking_repo.save(booking)
        
        # PUBLISH EVENT - NotificationWorker listens and sends cancellation
        self.event_bus.publish('booking.cancelled', {
            'booking_id': booking.id,
            'user_id': booking.user_id,
            'user_email': booking.user.email,
            'user_phone': booking.user.phone,
            'total_price': booking.total_price,
            'reason': reason
        })
        
        return booking


# ============================================================================
# EXAMPLE: Testing Workers
# ============================================================================

# tests/test_workers.py

import pytest
from unittest.mock import Mock, MagicMock
from src.workers.notification_worker import NotificationWorker
from src.workers.payroll_worker import PayrollWorker

class TestNotificationWorker:
    
    def test_send_booking_confirmation(self):
        # Setup
        mock_email = Mock()
        mock_sms = Mock()
        mock_push = Mock()
        
        worker = NotificationWorker(
            email_service=mock_email,
            sms_service=mock_sms,
            push_service=mock_push
        )
        
        # Execute
        result = worker.send_booking_confirmation(
            user_id='user123',
            booking_id='book456',
            booking_data={
                'user_email': 'john@example.com',
                'user_phone': '+1234567890',
                'trip_date': '2025-06-15',
                'total_price': 500.00
            }
        )
        
        # Assert
        assert result is True
        assert mock_email.send.called
        assert mock_sms.send.called
        assert mock_push.send.called
    
    def test_send_booking_cancelled(self):
        mock_email = Mock()
        worker = NotificationWorker(email_service=mock_email)
        
        result = worker.send_booking_cancelled(
            'user123',
            'book456',
            {
                'user_email': 'john@example.com',
                'user_phone': '+1234567890',
                'total_price': 500.00
            }
        )
        
        assert result is True
        assert mock_email.send.called


class TestPayrollWorker:
    
    def test_calculate_vendor_earnings(self):
        # 80/20 split: vendor gets 80%
        worker = PayrollWorker()
        
        # Mock repository
        mock_repo = Mock()
        worker.booking_repo = mock_repo
        mock_repo.get_by_vendor_and_period.return_value = [
            {'id': 'b1', 'total_price': 1000},
            {'id': 'b2', 'total_price': 500}
        ]
        
        # This would be the real test with mocked data
        # earnings = worker.calculate_vendor_earnings(
        #     'vendor123',
        #     datetime(2025, 6, 2),
        #     datetime(2025, 6, 9)
        # )
        
        # assert earnings['amount'] == 1200  # 1500 * 0.80


if __name__ == '__main__':
    # Simple example
    app = create_app()
    
    # Simulate booking creation
    with app.app_context():
        app.event_bus.publish('booking.created', {
            'booking_id': 'book123',
            'user_id': 'user456',
            'user_email': 'customer@example.com',
            'user_phone': '+1-555-0123',
            'trip_date': '2025-06-15',
            'total_price': 500.00
        })
    
    print(\"Event published - NotificationWorker should have sent confirmation!\")
