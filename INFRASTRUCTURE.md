# Infrastructure Layer - Complete Implementation Guide

## Overview
The Infrastructure Layer provides all external service integrations and data access mechanisms for the Travellr backend.

---

## 1. Database Layer (`database/`)

### Models (`models.py`)
**Status:** ✅ COMPLETE

#### UserModel
```python
UserModel(
    id: str (UUID),
    email: str (unique, lowercase),
    password_hash: str (bcrypt),
    name: str,
    phone: str,
    role: str (default: "user"),
    is_active: bool (default: True),
    created_at: datetime,
    updated_at: datetime
)
```

#### BookingModel
```python
BookingModel(
    id: str (UUID),
    user_id: str (FK: UserModel),
    vendor_id: str,
    trip_date: datetime,
    status: BookingStatus (enum: pending|confirmed|completed|cancelled),
    total_price: float,
    created_at: datetime,
    updated_at: datetime
)
```

#### PaymentModel
```python
PaymentModel(
    id: str (UUID),
    booking_id: str (FK: BookingModel),
    amount: float,
    currency: str (default: "usd"),
    status: str (pending|completed|failed|refunded),
    created_at: datetime,
    updated_at: datetime
)
```

### Repositories (`repositories.py`)
**Status:** ✅ COMPLETE

#### UserRepository
```python
save(user: UserModel) -> UserModel
find_by_id(user_id: str) -> Optional[UserModel]
find_by_email(email: str) -> Optional[UserModel]
find_all(page: int, limit: int) -> Tuple[List[UserModel], int]
update(user_id: str, **kwargs) -> Optional[UserModel]
delete(user_id: str) -> bool
exists(email: str) -> bool
```

#### BookingRepository
```python
save(booking: BookingModel) -> BookingModel
find_by_id(booking_id: str) -> Optional[BookingModel]
find_by_user_id(user_id: str, page: int, limit: int) -> Tuple[List, int]
find_by_vendor_id(vendor_id: str, page: int, limit: int) -> Tuple[List, int]
find_all(page: int, limit: int) -> Tuple[List[BookingModel], int]
update(booking_id: str, **kwargs) -> Optional[BookingModel]
delete(booking_id: str) -> bool
count_by_status(status: str) -> int
```

#### PaymentRepository
```python
save(payment: PaymentModel) -> PaymentModel
find_by_id(payment_id: str) -> Optional[PaymentModel]
find_by_booking_id(booking_id: str) -> List[PaymentModel]
find_all(page: int, limit: int) -> Tuple[List[PaymentModel], int]
update(payment_id: str, **kwargs) -> Optional[PaymentModel]
delete(payment_id: str) -> bool
sum_by_status(status: str) -> float
```

---

## 2. Payment Gateway (`payment/`)

### PaymentGateway (Abstract)
**Status:** ✅ COMPLETE

Base interface for all payment processors:
```python
process_payment(amount: float, currency: str, payment_method: str, 
                metadata: Dict) -> Dict
refund_payment(transaction_id: str, amount: Optional[float]) -> Dict
get_payment_status(transaction_id: str) -> Dict
```

### StripePaymentGateway
**Status:** ✅ COMPLETE

Full Stripe integration with error handling:

**Features:**
- PaymentIntent creation with metadata
- Automatic currency conversion (amount in cents)
- Card error handling (declined, invalid, etc.)
- Full/partial refunds
- Payment status retrieval
- Rate limiting and request error handling

**Usage:**
```python
from src.infrastructure.payment.payment_gateway import StripePaymentGateway

gateway = StripePaymentGateway(api_key="sk_test_...")

# Process payment
response = gateway.process_payment(
    amount=50.00,
    currency="usd",
    payment_method="pm_card_visa",
    metadata={"booking_id": "12345", "user_id": "user123"}
)

# Refund payment
refund = gateway.refund_payment("pi_123456", amount=25.00)

# Get status
status = gateway.get_payment_status("pi_123456")
```

### MockPaymentGateway
**Status:** ✅ COMPLETE

Testing gateway that simulates Stripe:
- Generates mock transaction IDs (UUIDs)
- Returns realistic responses without API calls
- Useful for development and testing

---

## 3. Cache Service (`cache/`)

### CacheService (Abstract)
**Status:** ✅ COMPLETE

Base cache interface:
```python
get(key: str) -> Optional[Any]
set(key: str, value: Any, ttl: int = 3600) -> bool
delete(key: str) -> bool
clear() -> bool
exists(key: str) -> bool
increment(key: str, amount: int = 1) -> int
```

### RedisCacheService
**Status:** ✅ COMPLETE

Production Redis implementation with:

**Features:**
- Automatic JSON serialization/deserialization
- TTL support with timedelta
- Connection pooling and error handling
- Pipeline operations for atomic batch updates
- Pattern-based key deletion
- Increment counter operations

**Usage:**
```python
from src.infrastructure.cache.cache_service import RedisCacheService

cache = RedisCacheService(
    host="localhost",
    port=6379,
    db=0,
    password=None
)

# Simple operations
cache.set("user:123", {"name": "John", "email": "john@example.com"}, ttl=3600)
user = cache.get("user:123")  # Automatic JSON deserialization

# Batch operations
cache.set_many({
    "cache:1": {"data": "value1"},
    "cache:2": {"data": "value2"}
}, ttl=7200)

# Pattern deletion
cache.delete_pattern("cache:*")

# Counters
counter = cache.increment("page_views:homepage", 1)
```

### InMemoryCacheService
**Status:** ✅ COMPLETE

Development/testing cache with TTL support:

**Features:**
- No external dependencies
- In-memory storage with expiration tracking
- Automatic cleanup of expired entries
- Full CacheService interface compatibility

**Usage:**
```python
from src.infrastructure.cache.cache_service import InMemoryCacheService

cache = InMemoryCacheService()

cache.set("temp_key", {"data": "value"}, ttl=60)
value = cache.get("temp_key")

cache.clear()  # Clear all entries
```

---

## 4. Event Bus / Messaging (`messaging/`)

### EventBus
**Status:** ✅ COMPLETE

Domain event publishing system:
```python
publish(event: DomainEvent) -> None
subscribe(event_name: str, handler: Callable) -> None
unsubscribe(event_name: str, handler: Callable) -> None
```

### DomainEvent (Base)
**Status:** ✅ COMPLETE

Base class for all domain events:
```python
class DomainEvent:
    event_name: str
    aggregate_id: str
    timestamp: datetime
    payload: Dict
```

### Supported Events
- **BookingCreatedEvent** - When booking is created
- **BookingCancelledEvent** - When booking is cancelled
- **BookingCompletedEvent** - When booking is completed
- **PaymentProcessedEvent** - When payment succeeds
- **VendorPayoutEvent** - When vendor payout is triggered

---

## Integration Usage

### Complete Example: Booking Creation Flow

```python
from src.infrastructure.database.repositories import BookingRepository
from src.infrastructure.payment.payment_gateway import StripePaymentGateway
from src.infrastructure.cache.cache_service import RedisCacheService
from src.infrastructure.messaging.event_bus import EventBus, BookingCreatedEvent
from src.infrastructure.database.models import BookingModel
import uuid
from datetime import datetime

# Initialize components
booking_repo = BookingRepository(db.session)
payment_gateway = StripePaymentGateway(api_key="sk_test_...")
cache = RedisCacheService()
event_bus = EventBus()

# Create booking
booking = BookingModel(
    id=str(uuid.uuid4()),
    user_id="user123",
    vendor_id="vendor456",
    trip_date=datetime(2025, 12, 25, 10, 0),
    status="pending",
    total_price=150.00
)

# Save to database
booking_repo.save(booking)

# Process payment
payment = payment_gateway.process_payment(
    amount=150.00,
    currency="usd",
    payment_method="pm_card_visa",
    metadata={"booking_id": booking.id}
)

if payment["success"]:
    # Cache booking for quick access
    cache.set(f"booking:{booking.id}", {
        "id": booking.id,
        "user_id": booking.user_id,
        "status": booking.status,
        "total_price": booking.total_price
    }, ttl=3600)
    
    # Publish event
    event = BookingCreatedEvent(
        aggregate_id=booking.id,
        user_id=booking.user_id,
        vendor_id=booking.vendor_id,
        total_price=booking.total_price
    )
    event_bus.publish(event)
```

---

## Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite:///travellr_dev.db

# Payment Gateway
STRIPE_API_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...

# Cache
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Email (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_password
```

### Development Setup
```python
from src.infrastructure.cache.cache_service import InMemoryCacheService
from src.infrastructure.payment.payment_gateway import MockPaymentGateway

# Use mock services for development
cache = InMemoryCacheService()
payment_gateway = MockPaymentGateway()
```

### Production Setup
```python
from src.infrastructure.cache.cache_service import RedisCacheService
from src.infrastructure.payment.payment_gateway import StripePaymentGateway
import os

# Use production services
cache = RedisCacheService(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD")
)
payment_gateway = StripePaymentGateway(
    api_key=os.getenv("STRIPE_API_KEY")
)
```

---

## Testing

### Unit Testing Repositories
```python
import pytest
from src.infrastructure.database.repositories import UserRepository
from src.infrastructure.database.models import UserModel

def test_save_user(db_session):
    repo = UserRepository(db_session)
    user = UserModel(
        id="123",
        email="test@example.com",
        password_hash="hashed",
        name="Test User"
    )
    saved = repo.save(user)
    assert saved.id == "123"
    assert saved.email == "test@example.com"

def test_find_by_email(db_session):
    repo = UserRepository(db_session)
    user = repo.find_by_email("test@example.com")
    assert user is not None
```

### Mock Payment Testing
```python
def test_booking_payment_flow():
    gateway = MockPaymentGateway()
    payment = gateway.process_payment(100.00, "usd")
    
    assert payment["success"] is True
    assert payment["status"] == "succeeded"
    assert payment["amount"] == 100.00
```

---

## Performance Optimization

### Cache Strategy
- User profiles: Cache for 1 hour
- Booking details: Cache for 30 minutes
- Analytics: Cache for 15 minutes
- Payment status: Cache for 5 minutes

### Database Indexing (PostgreSQL)
```sql
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_booking_user_id ON bookings(user_id);
CREATE INDEX idx_booking_vendor_id ON bookings(vendor_id);
CREATE INDEX idx_payment_booking_id ON payments(booking_id);
CREATE INDEX idx_booking_status ON bookings(status);
```

### Query Pagination
All repository queries support pagination:
```python
users, total = user_repo.find_all(page=1, limit=10)
# Returns: (List[UserModel], int total_count)
```

---

## Error Handling

All repository methods catch `SQLAlchemyError` and re-raise as `ValueError`:
```python
try:
    user = repo.save(user)
except ValueError as e:
    # Handle database error
    logger.error(f"Save failed: {str(e)}")
```

Payment gateway catches and returns error responses:
```python
response = payment_gateway.process_payment(...)
if not response["success"]:
    error = response["error"]  # "Card declined", "Rate limited", etc.
```

---

## Next Steps

1. **Database Migrations** - Setup Alembic for PostgreSQL migrations
2. **Connection Pooling** - Configure SQLAlchemy connection pool sizes
3. **Cache Warming** - Implement cache pre-loading for frequently accessed data
4. **Monitoring** - Add metrics for payment failures, cache hits, etc.
5. **Backup Strategy** - Setup database backup schedules

---

## Summary

✅ **Database** - 3 models, 3 fully-featured repositories with CRUD + advanced queries
✅ **Payment** - Abstract gateway + Stripe + Mock implementations
✅ **Cache** - Abstract service + Redis + In-Memory implementations
✅ **Events** - Pub/Sub event bus for domain events

**Infrastructure Layer Completion:** 100%
