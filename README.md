# FastAPI Backend Application

A comprehensive RESTful API backend built with FastAPI, featuring user authentication, role-based authorization, real-time WebSocket updates, and a complete e-commerce order management system.

## 🚀 Features

- **Authentication & Authorization**: JWT-based authentication with role-based access control
- **User Management**: Complete user registration, login, and profile management
- **Product Management**: Full CRUD operations for products with inventory tracking
- **Order System**: Comprehensive order processing with status tracking
- **Real-time Updates**: WebSocket endpoints for live order and product updates
- **Database Migrations**: Alembic integration for schema version control
- **Admin Dashboard**: Static file serving for admin interface
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Security Best Practices**: Password hashing, JWT tokens, and input validation

## 🛠 Technology Stack

- **Framework**: FastAPI 0.104.0+
- **Database**: SQLAlchemy 2.0+ with SQLite (configurable)
- **Authentication**: python-jose with JWT tokens
- **Password Hashing**: Passlib with bcrypt
- **Real-time**: WebSockets with Redis pub/sub
- **Migrations**: Alembic 1.12.0+
- **Validation**: Pydantic 2.0+ with email validation
- **ASGI Server**: Uvicorn with standard extras

## 📋 Prerequisites

- Python 3.8+
- Redis server (optional, fallback mode available)
- Git

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rococua-muhah
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./app.db

# Security Settings (REQUIRED - Generate a secure secret key)
SECRET_KEY=your-super-secret-key-here-generate-a-secure-one
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_V1_PREFIX=/api/v1
PROJECT_NAME=FastAPI Project
PROJECT_VERSION=1.0.0

# CORS Settings
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Environment Configuration
ENVIRONMENT=development
DEBUG=true
```

**⚠️ Important**: Generate a secure `SECRET_KEY` for production:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🗃 Database Setup

### Initialize Database

The application uses Alembic for database migrations:

```bash
# Initialize the database with the latest schema
alembic upgrade head
```

### Create New Migration

When you modify models, create a new migration:

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Apply the migration
alembic upgrade head
```

### Migration Management

```bash
# Check current migration status
alembic current

# View migration history
alembic history

# Downgrade to previous migration
alembic downgrade -1

# Upgrade to specific revision
alembic upgrade <revision_id>
```

### Verify Database Setup

```bash
python verify_migration.py
```

## 🚀 Running the Application

### Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### With Custom Configuration

```bash
# Specify custom host and port
uvicorn app.main:app --host 127.0.0.1 --port 8080

# With SSL (production)
uvicorn app.main:app --host 0.0.0.0 --port 443 --ssl-keyfile=./key.pem --ssl-certfile=./cert.pem
```

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Main API Endpoints

```
# Authentication
POST   /api/v1/auth/register     - User registration
POST   /api/v1/auth/login        - User login
POST   /api/v1/auth/refresh      - Refresh JWT token

# Users
GET    /api/v1/users/me          - Get current user profile
PUT    /api/v1/users/me          - Update user profile
POST   /api/v1/users/change-password - Change password

# Products
GET    /api/v1/products          - List products
POST   /api/v1/products          - Create product (admin)
GET    /api/v1/products/{id}     - Get product details
PUT    /api/v1/products/{id}     - Update product (admin)
DELETE /api/v1/products/{id}     - Delete product (admin)

# Orders
GET    /api/v1/orders            - List user's orders
POST   /api/v1/orders            - Create new order
GET    /api/v1/orders/{id}       - Get order details
PUT    /api/v1/orders/{id}       - Update order status

# Roles (Admin only)
GET    /api/v1/roles             - List roles
POST   /api/v1/roles             - Create role
PUT    /api/v1/roles/{id}        - Update role
DELETE /api/v1/roles/{id}        - Delete role
```

## 🔌 Real-time WebSocket Integration

The application provides real-time updates via WebSocket endpoints. For detailed WebSocket documentation, see [`README_WEBSOCKETS.md`](README_WEBSOCKETS.md).

### WebSocket Endpoints

- **Order Updates**: `/api/v1/ws/orders/{order_id}`
- **Product Updates**: `/api/v1/ws/products`
- **Health Check**: `/api/v1/ws/health`

### Quick WebSocket Example

```javascript
// Connect to order updates
const token = "your_jwt_token";
const orderId = "123e4567-e89b-12d3-a456-426614174000";
const ws = new WebSocket(
  `ws://localhost:8000/api/v1/ws/orders/${orderId}?token=${token}`
);

ws.onmessage = function (event) {
  const data = JSON.parse(event.data);
  console.log("Order update:", data);
};
```

### Redis Setup for WebSocket Scaling

For production WebSocket scaling, set up Redis:

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or install locally
redis-server
```

## 🏗 Admin Dashboard

The application serves static files for an admin dashboard:

- **Dashboard URL**: http://localhost:8000/dashboard/
- **Health Check**: http://localhost:8000/dashboard/health

Dashboard files should be placed in the `app/dashboard/` directory.

## 🔐 Security Features

### Authentication

- JWT tokens with configurable expiration
- Secure password hashing using bcrypt
- Token refresh mechanism

### Authorization

- Role-based access control (RBAC)
- Resource ownership validation
- Permission decorators for endpoints

### Security Best Practices

- Input validation with Pydantic
- SQL injection protection via SQLAlchemy ORM
- CORS configuration
- Environment-based configuration
- Secure headers and middleware

### Security Configuration

```python
# Recommended production settings
SECRET_KEY=<strong-randomly-generated-key>
ACCESS_TOKEN_EXPIRE_MINUTES=15
ENVIRONMENT=production
DEBUG=false
```

## 🧪 Testing

### Running WebSocket Tests

```bash
# Make sure server is running on localhost:8000
python test_websockets.py
```

Update the `TEST_TOKEN` in the test file with a valid JWT token.

### Manual API Testing

```bash
# Test authentication
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "testpass"}'

# Test protected endpoint
curl -X GET "http://localhost:8000/api/v1/users/me" \
     -H "Authorization: Bearer <your_jwt_token>"
```

## 🚀 Deployment

### Environment Preparation

1. **Set Production Environment Variables**:

   ```bash
   ENVIRONMENT=production
   DEBUG=false
   SECRET_KEY=<secure-production-key>
   DATABASE_URL=postgresql://user:pass@localhost/dbname
   ```

2. **Install Production Dependencies**:
   ```bash
   pip install uvicorn[standard] gunicorn
   ```

### Production Deployment

#### Using Gunicorn + Uvicorn Workers

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket support
    location /api/v1/ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### CI/CD Pipeline Example

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run migrations
        run: alembic upgrade head
      - name: Deploy to production
        run: # Your deployment script
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `python -m pytest`
5. Commit changes: `git commit -am 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Add comments for complex logic

### Database Changes

- Always create migrations for model changes
- Test migrations both up and down
- Include migration in your pull request

### API Changes

- Update OpenAPI documentation
- Maintain backward compatibility when possible
- Version breaking changes appropriately

## 📝 Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── role.py
│   │   └── ws.py              # WebSocket endpoints
│   ├── auth/                   # Authentication & authorization
│   │   ├── __init__.py
│   │   ├── jwt.py
│   │   ├── oauth2.py
│   │   ├── password.py
│   │   ├── permissions.py
│   │   ├── services.py
│   │   └── schemas.py
│   ├── core/                   # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── order_item.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   └── order.py
│   ├── dashboard/              # Static admin dashboard files
│   ├── services/               # Business logic services
│   ├── tests/                  # Test files
│   └── utils/                  # Utility functions
├── migrations/                 # Alembic migration files
├── alembic.ini                # Alembic configuration
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── README.md                 # This file
├── README_WEBSOCKETS.md      # WebSocket documentation
└── test_websockets.py        # WebSocket testing script
```

## 📞 Support & Documentation

- **API Documentation**: http://localhost:8000/docs
- **WebSocket Guide**: [`README_WEBSOCKETS.md`](README_WEBSOCKETS.md)
- **Issues**: Create an issue for bug reports or feature requests
Want to collaborate, chat tech, or just share a meme? Hit me up!

- **Email**: patrik-fredon@fredonbytes.cloud
- **Twitter**: [@PatrikFredon](https://twitter.com/freedompatrik)
- **LinkedIn**: [Patrik Fredon](https://linkedin.com/in/patrikfredon)
- **GitHub**: [patrikfredon](https://github.com/patrik-fredon)
- **Portfolio**: [About-me](https://me.fredonbytes.cloud)
- **FredonBytes**: [FredonBytes Home](https://fredonbytes.cloud)



---
<!-- Footer Section -->
<div align="center">
  
### 💭 Final Thoughts

Thanks for stopping by! If you liked this README, give it a ⭐ and follow me for more tech adventures. 

![Follow Me](https://img.shields.io/github/followers/patrik-fredon?label=Follow%20Me&style=social)

> "True mastery in code quiets the chaos and unlocks innovation."

<sub>© 2025 Fredon • Code Crafted for Tomorrow's Digital Frontier</sub>

</div>

