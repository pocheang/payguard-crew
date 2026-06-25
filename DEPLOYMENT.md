# 🏢 PayGuard Crew - Enterprise Production Deployment Guide

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Database Setup](#database-setup)
- [Environment Configuration](#environment-configuration)
- [Deployment Options](#deployment-options)
- [Monitoring & Observability](#monitoring--observability)
- [Security Checklist](#security-checklist)
- [Backup & Disaster Recovery](#backup--disaster-recovery)
- [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers deploying PayGuard Crew to production environments. The system is designed for enterprise-grade payment risk control and compliance auditing.

**Key Production Features:**
- ✅ Multi-database support (PostgreSQL/MySQL)
- ✅ Connection pooling and auto-scaling
- ✅ JWT authentication with RBAC
- ✅ Structured logging with correlation IDs
- ✅ Distributed tracing (OpenTelemetry)
- ✅ Kubernetes-ready with health checks
- ✅ CI/CD pipeline with security scanning
- ✅ Rate limiting and API protection

---

## Architecture

### Production Infrastructure

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer (Nginx)                 │
│                    payguard.example.com                  │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ PayGuard    │  │ PayGuard    │  │ PayGuard    │
│ API Pod 1   │  │ API Pod 2   │  │ API Pod 3   │
│ (FastAPI)   │  │ (FastAPI)   │  │ (FastAPI)   │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ PostgreSQL  │  │ ChromaDB    │  │ Redis       │
│ (Primary)   │  │ (Vectors)   │  │ (Cache)     │
└─────────────┘  └─────────────┘  └─────────────┘
        │
        ▼
┌─────────────┐
│ PostgreSQL  │
│ (Replica)   │
└─────────────┘

Monitoring Stack:
- Prometheus (metrics)
- Grafana (dashboards)
- Tempo (traces)
- Loki (logs)
```

---

## Prerequisites

### Required
- **Kubernetes cluster** (1.24+) or **Docker Swarm** / **standalone servers**
- **PostgreSQL** 14+ or **MySQL** 8.0+
- **Python** 3.9+
- **SSL/TLS certificates** (Let's Encrypt recommended)

### Recommended
- **Redis** for caching and rate limiting
- **Prometheus** + **Grafana** for monitoring
- **S3-compatible storage** for backups
- **Sentry** or similar for error tracking

---

## Database Setup

### PostgreSQL (Recommended)

#### 1. Create Database and User

```sql
-- Connect as superuser
CREATE DATABASE payguard;
CREATE USER payguard WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE payguard TO payguard;

-- Connect to payguard database
\c payguard

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO payguard;
```

#### 2. Configure Connection Pooling (PgBouncer)

```ini
# pgbouncer.ini
[databases]
payguard = host=localhost port=5432 dbname=payguard

[pgbouncer]
pool_mode = transaction
max_client_conn = 100
default_pool_size = 20
```

#### 3. Setup Replication (Optional)

```sql
-- On primary
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'repl_password';

-- Configure postgresql.conf
wal_level = replica
max_wal_senders = 3
```

### MySQL Alternative

```sql
CREATE DATABASE payguard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'payguard'@'%' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON payguard.* TO 'payguard'@'%';
FLUSH PRIVILEGES;
```

---

## Environment Configuration

### 1. Copy Production Template

```bash
cp .env.production.template .env.production
```

### 2. Critical Settings

**Database:**
```env
DATABASE_TYPE=postgresql
POSTGRES_HOST=postgres-primary.internal
POSTGRES_PASSWORD=<STRONG_PASSWORD>
DB_POOL_SIZE=20
```

**Security:**
```env
JWT_SECRET_KEY=<GENERATE_WITH_openssl_rand_hex_32>
API_KEYS=<COMMA_SEPARATED_KEYS>
```

**Generate secure keys:**
```bash
# Generate JWT secret
openssl rand -hex 32

# Generate API keys
openssl rand -base64 32
```

---

## Deployment Options

### Option 1: Kubernetes (Recommended)

#### 1. Create Namespace and Secrets

```bash
kubectl create namespace payguard-production

# Create secrets
kubectl create secret generic payguard-secrets \
  --from-literal=POSTGRES_PASSWORD='your_password' \
  --from-literal=JWT_SECRET_KEY='your_jwt_secret' \
  --from-literal=API_KEYS='key1,key2' \
  -n payguard-production
```

#### 2. Deploy Application

```bash
kubectl apply -f k8s/production/deployment.yaml
```

#### 3. Verify Deployment

```bash
kubectl get pods -n payguard-production
kubectl logs -f deployment/payguard-api -n payguard-production
```

### Option 2: Docker Compose

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  payguard-api:
    image: ghcr.io/pocheang/payguard-crew:latest
    deploy:
      replicas: 3
    env_file:
      - .env.production
    depends_on:
      - postgres
      - redis
    
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: payguard
      POSTGRES_USER: payguard
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

---

## Monitoring & Observability

### 1. Prometheus Metrics

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'payguard'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - payguard-production
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

**Key metrics:**
- `http_requests_total` - Request count
- `http_request_duration_seconds` - Request latency
- `risk_engine_evaluation_duration` - Rule engine performance
- `database_pool_connections` - Connection pool usage

### 2. Distributed Tracing

```env
OTEL_ENABLED=true
OTEL_EXPORTER_TYPE=otlp
OTEL_EXPORTER_OTLP_ENDPOINT=http://tempo:4317
```

### 3. Log Aggregation

Logs are output in JSON format for easy parsing:

```json
{
  "timestamp": "2026-06-25T10:30:00Z",
  "level": "INFO",
  "message": "Transaction audit completed",
  "request_id": "req_123",
  "user_id": "user_456",
  "duration_ms": 125
}
```

Ship to ELK, Datadog, or CloudWatch.

---

## Security Checklist

### Pre-Deployment

- [ ] Changed `JWT_SECRET_KEY` from default
- [ ] Generated strong `API_KEYS`
- [ ] Updated `POSTGRES_PASSWORD`
- [ ] Enabled HTTPS/TLS
- [ ] Configured firewall rules
- [ ] Set up WAF (Web Application Firewall)
- [ ] Enabled rate limiting
- [ ] Reviewed CORS settings
- [ ] Disabled debug mode (`APP_ENV=production`)
- [ ] Scanned container for vulnerabilities

### Post-Deployment

- [ ] Verified JWT authentication works
- [ ] Tested API key validation
- [ ] Confirmed database encryption at rest
- [ ] Enabled audit logging
- [ ] Set up security alerts
- [ ] Configured backup encryption
- [ ] Performed penetration testing
- [ ] Reviewed access controls

---

## Backup & Disaster Recovery

### Automated Database Backup

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/payguard"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="payguard_backup_${DATE}.sql.gz"

# Backup PostgreSQL
PGPASSWORD=${POSTGRES_PASSWORD} pg_dump \
  -h ${POSTGRES_HOST} \
  -U payguard \
  -d payguard \
  | gzip > ${BACKUP_DIR}/${FILENAME}

# Upload to S3
aws s3 cp ${BACKUP_DIR}/${FILENAME} \
  s3://payguard-backups/database/${FILENAME}

# Retain last 30 days
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +30 -delete
```

**Schedule with cron:**
```cron
0 2 * * * /opt/payguard/backup.sh
```

### Disaster Recovery Plan

**RTO (Recovery Time Objective):** 1 hour  
**RPO (Recovery Point Objective):** 24 hours

**Recovery Steps:**
1. Provision new infrastructure (Kubernetes cluster, database)
2. Restore database from latest backup
3. Deploy application from container registry
4. Update DNS records
5. Verify health checks
6. Resume traffic

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

```bash
# Check connection from pod
kubectl exec -it payguard-api-xxx -- \
  python -c "from app.db.database_engine import get_engine; get_engine()"
```

**Solutions:**
- Verify `POSTGRES_HOST` and credentials
- Check network policies
- Ensure database is accessible

#### 2. High Memory Usage

**Check metrics:**
```bash
kubectl top pods -n payguard-production
```

**Solutions:**
- Reduce `DB_POOL_SIZE`
- Increase pod memory limits
- Enable connection pooling

#### 3. Slow API Response

**Check traces in Grafana/Jaeger:**
- Identify bottleneck (database, LLM, rule engine)
- Review slow query log
- Optimize database indexes

#### 4. Authentication Failures

**Verify JWT configuration:**
```python
# Test JWT generation
from app.core.auth import User, create_access_token

user = User(
    user_id="test",
    username="test",
    email="test@example.com",
    roles=["admin"]
)
token = create_access_token(user)
print(token)
```

---

## Performance Tuning

### Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX idx_audit_reports_risk_level ON audit_reports(risk_level);

-- Analyze tables
ANALYZE transactions;
ANALYZE audit_reports;
```

### Application Settings

```env
# Connection pool tuning
DB_POOL_SIZE=20           # Increase for high traffic
DB_MAX_OVERFLOW=40        # 2x pool size
DB_POOL_RECYCLE=3600      # Recycle connections hourly

# Rate limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
```

---

## Compliance & Auditing

### Regulatory Requirements

- **PCI DSS:** Payment card data security
- **GDPR:** Data protection and privacy
- **SOC 2:** Security controls
- **ISO 27001:** Information security management

### Audit Trail

All sensitive operations are logged:
- User authentication attempts
- API access with correlation IDs
- Data modifications
- Security events

**Access audit logs:**
```bash
kubectl logs -l app=payguard --since=1h | grep "security_event"
```

---

## Support & Maintenance

### Health Monitoring

```bash
# Check health endpoint
curl https://payguard.example.com/health

# Expected response
{
  "status": "ok",
  "service": "payguard-crew",
  "version": "0.1.1",
  "database": "connected",
  "timestamp": "2026-06-25T10:30:00Z"
}
```

### Maintenance Windows

- **Database maintenance:** Sundays 02:00-04:00 UTC
- **Application updates:** Rolling deployments (zero downtime)
- **Security patches:** As needed (coordinated with team)

---

## Contact

- **Technical Support:** ops@example.com
- **Security Issues:** security@example.com
- **On-Call:** Refer to PagerDuty schedule

---

**Last Updated:** 2026-06-25  
**Version:** 0.1.1
