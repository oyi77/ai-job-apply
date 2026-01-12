# Production Deployment Guide

This guide details how to deploy the AI Job Application Assistant to a production environment.

## Prerequisites

*   **Docker & Docker Compose**: Installed on the target server.
*   **Domain Name**: Pointed to the server's IP.
*   **SSL Certificates**: Generated via Let's Encrypt or self-signed (for testing).

## Architecture

The production stack uses Docker Compose and consists of:
*   **Nginx**: Reverse proxy and SSL termination.
*   **Frontend**: Nginx serving React static build.
*   **Backend**: FastAPI application (Gunicorn/Uvicorn).
*   **Postgres**: Production database.
*   **Redis**: Caching and session storage.
*   **Prometheus**: Metrics collection.
*   **Grafana**: Monitoring dashboard.

## Initial Setup

1.  **Clone Repository**:
    ```bash
    git clone https://github.com/yourusername/ai-job-apply.git
    cd ai-job-apply
    ```

2.  **Environment Variables**:
    Copy `.env.example` to `.env` and set production values:
    ```bash
    cp .env.example .env
    # Edit .env:
    # Set ENVIRONMENT=production
    # Set POSTGRES_PASSWORD, SECRET_KEY, JWT_SECRET_KEY, GEMINI_API_KEY
    ```

3.  **SSL Certificates**:
    For testing, generate self-signed certs:
    ```bash
    ./scripts/generate-ssl.sh localhost
    ```
    For production, use Certbot:
    ```bash
    certbot certonly --standalone -d yourdomain.com
    # Copy certs to ./nginx/ssl/
    ```

4.  **Required Environment Variables**:
    Ensure `.env` contains:
    *   `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
    *   `SECRET_KEY`, `JWT_SECRET_KEY`
    *   `GEMINI_API_KEY` (or other AI keys)
    *   `CORS_ORIGINS` (comma-separated, e.g., `https://yourdomain.com`)
    *   `ENVIRONMENT=production`


## Deployment

The project includes a helper script for zero-downtime-ish deployment (replaces containers).

Run the deployment script:
```bash
./scripts/deploy.sh
```

Or manually:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head
```

## Monitoring

*   **Prometheus**: `http://localhost:9090`
*   **Grafana**: `http://localhost:3001` (Default login: admin/admin)

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/deploy.yml`) handles:
1.  Running tests.
2.  Building Docker images.
3.  Pushing to Docker Hub.
4.  Deploying to the production server via SSH.

Make sure to configure the following GitHub Secrets:
*   `DOCKER_USERNAME`, `DOCKER_PASSWORD`
*   `PROD_HOST`, `PROD_USERNAME`, `PROD_SSH_KEY`
