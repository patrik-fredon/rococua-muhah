# Deployment Guide

This guide covers deployment options for the FastAPI + Next.js Dashboard System.

## 🚀 Quick Deployment

### Using the Unified Launcher

The simplest way to deploy is using our unified launcher:

```bash
# Development
python3 launcher.py --mode dev

# Production
python3 launcher.py --mode prod
```

## 🐳 Docker Deployment

### Development Environment

```bash
# Start all services with Docker Compose
make docker-up

# Or manually
docker-compose up -d

# View logs
make docker-logs
```

### Production Environment

```bash
# Build images
make docker-build

# Deploy with production profile
docker-compose --profile production up -d

# Or use the deployment command
make deploy
```

## ☁️ Cloud Deployment

### AWS Deployment

1. **Setup EC2 Instance**:

   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Deploy Application**:

   ```bash
   # Clone repository
   git clone <your-repo-url>
   cd rococua-muhah

   # Setup environment
   cp .env.example .env
   # Edit .env with production values

   # Deploy
   make deploy
   ```

3. **Setup Reverse Proxy** (Nginx):

   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Google Cloud Platform

1. **Setup Cloud Run**:

   ```bash
   # Build and push backend
   gcloud builds submit --tag gcr.io/PROJECT_ID/fastapi-backend

   # Build and push frontend
   cd dashboard
   gcloud builds submit --tag gcr.io/PROJECT_ID/nextjs-frontend
   ```

2. **Deploy Services**:

   ```bash
   # Deploy backend
   gcloud run deploy fastapi-backend \
     --image gcr.io/PROJECT_ID/fastapi-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated

   # Deploy frontend
   gcloud run deploy nextjs-frontend \
     --image gcr.io/PROJECT_ID/nextjs-frontend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### Digital Ocean App Platform

```yaml
# .do/app.yaml
name: fastapi-nextjs-dashboard
services:
  - name: backend
    source_dir: /
    dockerfile_path: Dockerfile.backend
    http_port: 8000
    instance_count: 1
    instance_size_slug: basic-xxs

  - name: frontend
    source_dir: /dashboard
    dockerfile_path: Dockerfile
    http_port: 3000
    instance_count: 1
    instance_size_slug: basic-xxs

databases:
  - name: dashboard-db
    engine: PG
    version: "14"
    size: db-s-1vcpu-1gb
```

## 🔒 Production Security

### Environment Configuration

```env
# Production .env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-production-secret-key-minimum-32-characters-long
SECURE_COOKIES=true
HTTPS_ONLY=true

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dashboard_db

# Security
BACKEND_CORS_ORIGINS=https://yourdomain.com
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=30

# Performance
WORKERS=4
LOG_LEVEL=WARNING
SWAGGER_UI_ENABLED=false
```

### SSL/TLS Setup

1. **Using Let's Encrypt**:

   ```bash
   # Install Certbot
   sudo apt install certbot python3-certbot-nginx

   # Get certificate
   sudo certbot --nginx -d yourdomain.com

   # Auto-renewal
   sudo crontab -e
   # Add: 0 12 * * * /usr/bin/certbot renew --quiet
   ```

2. **Using Cloudflare**:
   - Point your domain to Cloudflare
   - Enable SSL/TLS encryption
   - Configure origin certificates

## 📊 Monitoring & Logging

### Health Checks

```bash
# Backend health
curl https://yourdomain.com/api/v1/health

# Frontend health
curl https://yourdomain.com/

# Docker health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Logging Setup

1. **Centralized Logging**:

   ```yaml
   # docker-compose.override.yml
   version: "3.8"
   services:
     backend:
       logging:
         driver: "json-file"
         options:
           max-size: "10m"
           max-file: "3"

     frontend:
       logging:
         driver: "json-file"
         options:
           max-size: "10m"
           max-file: "3"
   ```

2. **Log Aggregation** (ELK Stack):

   ```yaml
   services:
     elasticsearch:
       image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
       environment:
         - discovery.type=single-node
         - xpack.security.enabled=false
       ports:
         - "9200:9200"

     kibana:
       image: docker.elastic.co/kibana/kibana:8.8.0
       ports:
         - "5601:5601"
       depends_on:
         - elasticsearch
   ```

## 🔄 CI/CD Pipeline

### GitHub Actions (Included)

The project includes a complete CI/CD pipeline:

1. **Automated Testing**: Backend and frontend tests
2. **Security Scanning**: Vulnerability scans
3. **Docker Builds**: Automated image building
4. **Deployment**: Staging and production deployment

### Manual Deployment

```bash
# Build and test
make test
make build

# Deploy to staging
git push origin develop

# Deploy to production
git push origin main
```

## 📈 Scaling

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: "3.8"
services:
  backend:
    deploy:
      replicas: 3

  frontend:
    deploy:
      replicas: 2
```

### Load Balancing

```nginx
upstream backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

upstream frontend {
    server 127.0.0.1:3001;
    server 127.0.0.1:3002;
}

server {
    listen 80;

    location /api {
        proxy_pass http://backend;
    }

    location / {
        proxy_pass http://frontend;
    }
}
```

## 🛠️ Maintenance

### Database Backups

```bash
# PostgreSQL backup
pg_dump dashboard_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backups
echo "0 2 * * * pg_dump dashboard_db > /backups/backup_\$(date +\%Y\%m\%d_\%H\%M\%S).sql" | crontab -
```

### Updates

```bash
# Update application
git pull origin main
make build
make deploy

# Update dependencies
make update-deps
```

### Rollback

```bash
# Docker rollback
docker-compose down
git checkout <previous-commit>
make deploy

# Database rollback
alembic downgrade -1
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Conflicts**:

   ```bash
   sudo lsof -ti:3000,8000 | xargs kill -9
   ```

2. **Database Connection**:

   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql

   # Test connection
   psql -h localhost -U postgres -d dashboard_db
   ```

3. **Docker Issues**:

   ```bash
   # Clean Docker
   make docker-clean

   # Rebuild images
   docker-compose build --no-cache
   ```

### Log Analysis

```bash
# Backend logs
docker logs fastapi-backend

# Frontend logs
docker logs nextjs-frontend

# Database logs
docker logs postgres

# System logs
journalctl -u docker
```

## 📞 Support

For deployment issues:

1. Check the [troubleshooting guide](./README.md#troubleshooting)
2. Review application logs
3. Verify environment configuration
4. Open an issue on GitHub

---

**Ready to deploy your FastAPI + Next.js Dashboard!** 🚀
