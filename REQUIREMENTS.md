# Travellr Backend - Project Requirements & Dependencies

## Project Structure Overview

```
Travellr-backend/
├── src/
│   ├── api/              # REST API endpoints
│   ├── application/      # Business logic & use cases
│   ├── domain/           # Domain models & entities
│   ├── infrastructure/   # Database, external services
│   ├── workers/          # Background jobs
│   ├── security/         # Auth & encryption
│   ├── config/           # Configuration
│   ├── tests/            # Unit & integration tests
│   ├── app.py            # Flask app factory
│   └── server.py         # Entry point
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Environment variables (local)
└── README.md             # Project documentation
```

---

## Dependencies Breakdown

### 1. **Web Framework**
- **Flask** (2.3.3) - Lightweight Python web framework
- **Flask-SQLAlchemy** (3.0.5) - Database ORM
- **SQLAlchemy** (2.0.21) - Core ORM library

**Why:** Build REST APIs with database integration

---

### 2. **Database Drivers**
- **psycopg2-binary** (2.9.7) - PostgreSQL driver (Production)
- **PyMySQL** (1.1.0) - MySQL driver (Optional)

**Why:** Connect to different databases

---

### 3. **Authentication & Security**
- **PyJWT** (2.8.1) - JWT token generation & verification
- **bcrypt** (4.0.1) - Password hashing
- **python-dotenv** (1.0.0) - Load environment variables from .env

**Why:** Secure user authentication and credential storage

---

### 4. **Data Validation**
- **marshmallow** (3.20.1) - Validate request/response data
- **marshmallow-sqlalchemy** (0.29.0) - SQLAlchemy integration for marshmallow

**Why:** Validate input, transform data, handle errors

---

### 5. **Caching**
- **redis** (5.0.0) - Redis Python client
- **Flask-Caching** (2.0.2) - Flask caching extension

**Why:** Cache frequently accessed data, improve performance

---

### 6. **Production Server**
- **gunicorn** (21.2.0) - WSGI HTTP server (production)
- **gevent** (23.9.1) - Async worker support for gunicorn

**Why:** Run Flask safely in production (not development server)

---

### 7. **API Documentation**
- **Flask-RESTX** (0.5.1) - Auto-generate Swagger/OpenAPI docs

**Why:** Document APIs automatically

---

### 8. **Email**
- **Flask-Mail** (0.9.1) - Send emails

**Why:** Send confirmation emails, notifications

---

### 9. **Background Jobs**
- **celery** (5.3.2) - Task queue for async jobs
- **celery-beat** (2.5.0) - Celery scheduler

**Why:** Send notifications, process payments asynchronously

---

### 10. **Payment Gateway**
- **stripe** (5.16.0) - Stripe payment integration

**Why:** Process payments securely

---

### 11. **Testing**
- **pytest** (7.4.2) - Testing framework
- **pytest-flask** (1.2.0) - Flask testing plugin
- **pytest-cov** (4.1.0) - Code coverage reports
- **factory-boy** (3.3.0) - Create test data

**Why:** Write unit & integration tests

---

### 12. **Code Quality**
- **black** (23.10.0) - Code formatter
- **flake8** (6.1.0) - Code linter
- **pylint** (3.0.2) - Code analyzer
- **isort** (5.12.0) - Import sorter

**Why:** Keep code clean & consistent

---

### 13. **Development Tools**
- **flask-cors** (4.0.0) - Enable CORS
- **requests** (2.31.0) - HTTP client for testing

**Why:** Handle cross-origin requests, test APIs

---

## Installation

### Step 1: Install all dependencies
```bash
cd Travellr-backend
pip install -r requirements.txt
```

### Step 2: Verify installation
```bash
pip list
```

---

## Environment Variables Required

Create `.env` file with:

```env
# Flask
FLASK_ENV=development
FLASK_APP=server.py

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/travellr
DEV_DATABASE_URL=sqlite:///travellr_dev.db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here

# Stripe
STRIPE_API_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

---

## Optional Dependencies (Add later as needed)

```bash
# API versioning
pip install flask-versioning

# Rate limiting
pip install Flask-Limiter

# Request logging
pip install Flask-Logging

# Database migrations
pip install Flask-Migrate Alembic

# GraphQL (if needed)
pip install graphene flask-graphql

# WebSockets (if needed)
pip install Flask-SocketIO python-socketio
```

---

## Running the Project

### Development
```bash
cd src
python -m server
```

### Production
```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

### Testing
```bash
pytest
pytest --cov=src  # With coverage report
```

### Code Quality
```bash
black src/          # Format code
flake8 src/         # Lint code
isort src/          # Sort imports
```

---

## Next Steps

1. ✅ Create requirements.txt (Done)
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env`
4. Fix import issues in Flask app
5. Test authentication endpoints
6. Build other API endpoints (Users, Bookings, Payments)
7. Write tests
8. Deploy to production

---

## Project Size Estimate

- **Total Packages:** 30+
- **Total Size:** ~500MB
- **Installation Time:** 2-5 minutes

