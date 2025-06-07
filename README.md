# FastAPI + Next.js Dashboard System

A modern, full-stack dashboard system built with FastAPI backend and Next.js frontend, featuring unified launching, secure authentication, real-time updates, and comprehensive CRUD operations.

## 🚀 Quick Start

### Using the Unified Launcher (Recommended)

The easiest way to get started is using our unified launcher system:

```bash
# Clone the repository
git clone <repository-url>
cd rococua-muhah

# Quick start (installs dependencies, sets up environment, and launches)
make quick-start

# Or use the launcher directly
python3 launcher.py --mode dev

# Or use platform-specific scripts
./launch.sh --mode dev     # Unix/Linux/macOS
launch.bat --mode dev      # Windows
```

### Manual Setup

If you prefer manual setup:

```bash
# 1. Setup environment
make setup-env

# 2. Install dependencies
make install

# 3. Run database migrations
make migrate

# 4. Start development servers
make dev
```

## 📋 Features

- **🔄 Unified Launcher**: Single command to start both backend and frontend
- **🛡️ Secure Authentication**: JWT-based auth with role-based access control
- **⚡ Real-time Updates**: WebSocket integration for live data
- **🔧 Generic CRUD System**: Reusable patterns for any entity
- **📱 Responsive Dashboard**: Modern Next.js frontend with Material-UI
- **🐳 Docker Support**: Complete containerization for production deployment
- **🔍 API Documentation**: Auto-generated Swagger/OpenAPI docs
- **📊 Performance Optimized**: Caching, compression, and monitoring
- **🔒 Security Headers**: Production-ready security configurations

## 🏗️ Architecture

```
┌─────────────────────┐    ┌─────────────────────┐
│   Frontend (Next.js) │    │   Backend (FastAPI) │
├─────────────────────┤    ├─────────────────────┤
│ • Generic UI Hooks  │    │ • API Routes        │
│ • CRUD Components   │◄──►│ • Service Layer     │
│ • Base API Client   │    │ • Base CRUD Classes │
│ • Type-safe APIs    │    │ • Database Models   │
└─────────────────────┘    └─────────────────────┘
           │                           │
           └─────────┬─────────────────┘
                     │
        ┌─────────────────────┐
        │   Infrastructure    │
        ├─────────────────────┤
        │ • PostgreSQL/SQLite │
        │ • Redis (WebSocket) │
        │ • Docker & Compose  │
        │ • Nginx (Production)│
        └─────────────────────┘
```

## 🛠️ Technology Stack

### Backend

- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM with Alembic migrations
- **Pydantic**: Data validation and settings
- **Redis**: Caching and WebSocket scaling
- **JWT**: Secure authentication
- **WebSockets**: Real-time communication

### Frontend

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Material-UI**: Component library
- **TanStack Query**: Data fetching and caching
- **Framer Motion**: Animations
- **Axios**: HTTP client

### Infrastructure

- **Docker & Compose**: Containerization
- **PostgreSQL**: Production database
- **Redis**: Caching and sessions
- **Nginx**: Reverse proxy (production)

## 🚀 Available Commands

### Launcher Commands

```bash
# Development mode (default)
python3 launcher.py
python3 launcher.py --mode dev

# Production mode
python3 launcher.py --mode prod

# Skip dependency installation
python3 launcher.py --no-install

# Skip database migrations
python3 launcher.py --no-migrate

# Don't open browser automatically
python3 launcher.py --no-browser
```

### Makefile Commands

```bash
# Development
make dev              # Start development servers
make dev-backend      # Start only backend
make dev-frontend     # Start only frontend

# Installation
make install          # Install all dependencies
make install-backend  # Install backend dependencies
make install-frontend # Install frontend dependencies

# Environment
make setup-env        # Setup environment files
make migrate          # Run database migrations
make seed             # Seed database with sample data

# Production
make prod             # Start production servers
make build            # Build for production
make deploy           # Deploy to production

# Docker
make docker           # Build and run with Docker
make docker-build     # Build Docker images
make docker-up        # Start Docker services
make docker-down      # Stop Docker services

# Code Quality
make test             # Run all tests
make lint             # Run linting
make format           # Format code

# Utilities
make clean            # Clean build artifacts
make health           # Check service health
make status           # Show project status
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Database
DATABASE_URL=sqlite:///./app.db

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256

# API
PROJECT_NAME=FastAPI Dashboard
API_V1_PREFIX=/api/v1

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Environment
ENVIRONMENT=development
DEBUG=true
```

### Production Configuration

For production deployment:

```env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-production-secret-key-minimum-32-characters-long
SECURE_COOKIES=true
HTTPS_ONLY=true
DATABASE_URL=postgresql://user:password@localhost:5432/dashboard_db
BACKEND_CORS_ORIGINS=https://yourdomain.com
WORKERS=4
LOG_LEVEL=WARNING
SWAGGER_UI_ENABLED=false
```

## 🐳 Docker Deployment

### Development with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment

```bash
# Build and deploy
make docker-build
docker-compose --profile production up -d

# Or use the complete deployment command
make deploy
```

## 📚 API Documentation

When running in development mode, API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🔐 Authentication

The system uses JWT-based authentication with role-based access control:

```typescript
// Login
const response = await authApi.login({
  email: "admin@example.com",
  password: "password",
});

// Use authenticated requests
const users = await userApi.getAll();
```

### Default Users

After running `make seed`, the following users are available:

- **Admin**: admin@example.com / password
- **User**: user@example.com / password

## 🔄 Adding New Entities

The system provides a generic CRUD pattern that makes adding new entities simple:

### 1. Backend Setup

```python
# models/entity.py
class Entity(Base):
    __tablename__ = "entities"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)

# schemas/entity.py
class EntityCreate(BaseModel):
    name: str

class EntityUpdate(BaseModel):
    name: Optional[str] = None

# services/entity_service.py
class EntityService(CRUDBase[Entity, EntityCreate, EntityUpdate]):
    pass

entity_service = EntityService(Entity)
```

### 2. Frontend Setup

```typescript
// services/entitiesApi.ts
export const entityService = createCrudService<
  Entity,
  EntityCreate,
  EntityUpdate
>("/api/v1/entities");

// hooks/useEntityQuery.ts
const entityHooks = createCrudHooks("entity", entityService);
export const useEntities = entityHooks.useGetAll;
export const useCreateEntity = entityHooks.useCreate;
```

## 🧪 Testing

```bash
# Run all tests
make test

# Backend tests only
make test-backend

# Frontend tests only
make test-frontend

# With coverage
cd app && python -m pytest --cov=app tests/
```

## 📊 Monitoring & Health Checks

### Health Endpoints

- **Backend Health**: http://localhost:8000/health
- **Frontend Health**: http://localhost:3000/ (Next.js built-in)

### Monitoring

```bash
# Check service status
make status

# View logs
make logs-backend
make logs-frontend

# Docker logs
make docker-logs
```

## 🔧 Development

### Project Structure

```
├── app/                    # FastAPI backend
│   ├── api/               # API routes
│   ├── core/              # Core configuration
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── main.py           # Application entry point
├── dashboard/             # Next.js frontend
│   ├── app/              # App Router pages
│   ├── components/       # React components
│   ├── hooks/            # Custom hooks
│   ├── services/         # API services
│   └── utils/            # Utilities
├── launcher.py           # Unified launcher
├── docker-compose.yml    # Docker configuration
├── Makefile             # Development commands
└── README.md            # This file
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Type checking
cd dashboard && npm run type-check
```

## 🚀 Production Deployment

### Prerequisites

- Docker & Docker Compose
- Domain name with SSL certificate
- PostgreSQL database
- Redis instance

### Deployment Steps

1. **Configure environment**:

   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Build and deploy**:

   ```bash
   make deploy
   ```

3. **Setup SSL** (optional):
   ```bash
   # Copy SSL certificates to ./ssl/
   docker-compose --profile production up -d
   ```

## 📈 Performance

### Optimizations Included

- **Backend**:

  - FastAPI with async/await
  - SQLAlchemy connection pooling
  - Redis caching
  - Compression middleware
  - Security headers

- **Frontend**:
  - Next.js optimizations
  - React Query caching
  - Code splitting
  - Image optimization
  - Static generation

### Benchmarks

On a typical development machine:

- **Cold start**: ~5-10 seconds
- **Hot reload**: ~1-2 seconds
- **API response**: <100ms
- **Frontend render**: <200ms

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run quality checks: `make lint && make test`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

**Port already in use**:

```bash
# Kill processes on ports 3000 and 8000
sudo lsof -ti:3000,8000 | xargs kill -9
```

**Database migration issues**:

```bash
# Reset database
make reset-db
```

**Docker issues**:

```bash
# Clean Docker
make docker-clean
```

### Getting Help

- Check the [troubleshooting guide](./docs/troubleshooting.md)
- Review [API documentation](http://localhost:8000/docs)
- Open an issue on GitHub

## 🎯 Roadmap

- [ ] Rate limiting middleware
- [ ] Email notifications
- [ ] File upload system
- [ ] Advanced search & filtering
- [ ] Audit logging
- [ ] Multi-tenancy support
- [ ] API versioning
- [ ] GraphQL endpoint

---

**Built with ❤️ using FastAPI and Next.js**
