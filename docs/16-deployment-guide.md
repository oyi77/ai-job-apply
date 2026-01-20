# Deployment Guide: Production Deployment

> **Step-by-step deployment procedures**

## Environment Configurations

### Development
- **Backend**: `http://localhost:8000`
- **Frontend**: `http://localhost:5173`
- **Database**: SQLite (`app.db`)
- **Debug**: Enabled
- **Hot Reload**: Enabled

### Production
- **Backend**: `https://api.yourdomain.com`
- **Frontend**: `https://yourdomain.com`
- **Database**: PostgreSQL
- **Debug**: Disabled
- **SSL**: Required

## Docker Deployment

### Development Setup

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Setup

```bash
# Set environment variables
export POSTGRES_USER=your_user
export POSTGRES_PASSWORD=secure_password
export SECRET_KEY=your_secret_key
export GEMINI_API_KEY=your_api_key
export CORS_ORIGINS=https://yourdomain.com

# Build and start
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Check health
curl https://api.yourdomain.com/health
```

## Environment Variables

### Required Variables

```bash
# Backend (.env)
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key_min_32_chars
JWT_SECRET_KEY=your_jwt_secret_key

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# CORS
CORS_ORIGINS=["https://yourdomain.com"]

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Frontend (.env)

```bash
VITE_API_URL=https://api.yourdomain.com
VITE_APP_NAME=AI Job Assistant
```

## Database Migrations

### Development

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Production

```bash
# Backup database first
docker-compose exec postgres pg_dump -U postgres ai_job_assistant > backup.sql

# Run migrations
docker-compose exec backend alembic upgrade head

# Verify
docker-compose exec backend alembic current
```

## Health Checks

### Backend Health

```bash
curl https://api.yourdomain.com/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "ai_service": "available"
}
```

### Frontend Health

```bash
curl https://yourdomain.com

# Should return 200 OK
```

## Monitoring

### Application Logs

```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# File logs
tail -f backend/logs/app.log
```

### Database Monitoring

```bash
# PostgreSQL stats
docker-compose exec postgres psql -U postgres -d ai_job_assistant -c "
  SELECT schemaname, tablename, n_live_tup 
  FROM pg_stat_user_tables 
  ORDER BY n_live_tup DESC;
"
```

## Backup and Recovery

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres ai_job_assistant > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T postgres psql -U postgres ai_job_assistant < backup_20260120.sql
```

### File Backup

```bash
# Backup uploads
tar -czf uploads_backup.tar.gz backend/uploads/

# Restore uploads
tar -xzf uploads_backup.tar.gz -C backend/
```

## Security Hardening

### SSL/TLS Configuration

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://frontend:5173;
    }
    
    location /api {
        proxy_pass http://backend:8000;
    }
}
```

### Environment Security

```bash
# Use secrets management
docker secret create db_password password.txt
docker secret create api_key api_key.txt

# Restrict file permissions
chmod 600 .env
chmod 600 backend/.env
```

## Performance Tuning

### Database Optimization

```sql
-- Add indexes
CREATE INDEX idx_applications_user_status ON applications(user_id, status);
CREATE INDEX idx_applications_created_at ON applications(created_at);

-- Analyze tables
ANALYZE applications;
ANALYZE resumes;
```

### Application Tuning

```python
# backend/src/config.py
# Increase worker count
WORKERS = 4

# Connection pool
POOL_SIZE = 20
MAX_OVERFLOW = 10
```

## Rollback Procedures

### Application Rollback

```bash
# Rollback to previous version
docker-compose down
git checkout previous_tag
docker-compose up -d --build
```

### Database Rollback

```bash
# Rollback migration
docker-compose exec backend alembic downgrade -1

# Restore from backup
docker-compose exec -T postgres psql -U postgres ai_job_assistant < backup.sql
```

## Troubleshooting Production

### High Memory Usage

```bash
# Check container stats
docker stats

# Restart services
docker-compose restart backend
```

### Database Connection Issues

```bash
# Check connections
docker-compose exec postgres psql -U postgres -c "
  SELECT count(*) FROM pg_stat_activity;
"

# Kill idle connections
docker-compose exec postgres psql -U postgres -c "
  SELECT pg_terminate_backend(pid) 
  FROM pg_stat_activity 
  WHERE state = 'idle' AND state_change < now() - interval '1 hour';
"
```

---

**Last Updated**: 2026-01-20  
**Deployment**: Docker-based with PostgreSQL  
**For troubleshooting, see**: [10-troubleshooting.md](./10-troubleshooting.md)
