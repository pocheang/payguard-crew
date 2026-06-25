# Enterprise Architecture Document - PayGuard Crew

## Executive Summary

PayGuard Crew is an enterprise-grade AI-powered payment risk control and compliance auditing system. This document outlines the production-ready architecture, security measures, and operational procedures for deploying and maintaining the system in enterprise environments.

**Document Version:** 1.0  
**Last Updated:** 2026-06-25  
**Classification:** Internal Use

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Internet (HTTPS)                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Load Balancer / WAF                           │
│              - Rate Limiting: 100 req/min                        │
│              - DDoS Protection                                   │
│              - SSL Termination                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │     Kubernetes Cluster        │
         │   (3+ worker nodes)           │
         │                               │
         │   ┌─────────────────────┐    │
         │   │  PayGuard API Pods  │    │
         │   │  (Min: 3, Max: 10)  │    │
         │   │                     │    │
         │   │  - FastAPI          │    │
         │   │  - JWT Auth         │    │
         │   │  - Risk Engine      │    │
         │   │  - AI Agents        │    │
         │   └──────────┬──────────┘    │
         │              │                │
         └──────────────┼────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌─────────────┐ ┌────────────┐
│ PostgreSQL   │ │ ChromaDB    │ │ Redis      │
│ Cluster      │ │ (Vectors)   │ │ (Cache)    │
│              │ │             │ │            │
│ - Primary    │ │ - RAG Store │ │ - Sessions │
│ - 2 Replicas │ │ - Policies  │ │ - Rate Lim │
└──────────────┘ └─────────────┘ └────────────┘
        │
        ▼
┌──────────────┐
│ S3 Storage   │
│ - Backups    │
│ - Audit Logs │
└──────────────┘

Observability Stack:
┌────────────────────────────────────────┐
│ Prometheus → Grafana (Metrics)         │
│ Loki → Grafana (Logs)                  │
│ Tempo → Grafana (Traces)               │
│ Sentry (Error Tracking)                │
└────────────────────────────────────────┘
```

---

## Technology Stack

### Application Layer
- **Framework:** FastAPI 0.111+ (Python 3.9+)
- **AI Orchestration:** CrewAI 0.80+ (optional)
- **API Documentation:** OpenAPI 3.0 (Swagger/ReDoc)

### Data Layer
- **Primary Database:** PostgreSQL 14+ with streaming replication
- **Alternative:** MySQL 8.0+ (supported)
- **Vector Store:** ChromaDB (RAG knowledge base)
- **Cache:** Redis 7+ (optional, for rate limiting)

### Security
- **Authentication:** JWT (HS256/RS256)
- **Authorization:** Role-Based Access Control (RBAC)
- **Encryption:** AES-256-GCM, bcrypt password hashing
- **API Protection:** API key authentication, rate limiting

### Observability
- **Metrics:** Prometheus + Grafana
- **Logging:** Structured JSON logs (ELK/Datadog/CloudWatch compatible)
- **Tracing:** OpenTelemetry (OTLP)
- **APM:** Sentry (error tracking)

### Infrastructure
- **Orchestration:** Kubernetes 1.24+
- **CI/CD:** GitHub Actions
- **Container Registry:** GitHub Container Registry (GHCR)
- **Cloud:** AWS/GCP/Azure agnostic

---

## Security Architecture

### Authentication & Authorization

#### JWT Token Flow

```
1. User Login
   POST /api/v1/auth/login
   { username, password }
   ↓
2. Verify Credentials
   - Check password hash (bcrypt)
   - Validate user status
   ↓
3. Issue JWT Tokens
   - Access Token (30 min)
   - Refresh Token (7 days)
   ↓
4. Client Stores Tokens
   - Access Token in memory
   - Refresh Token in HttpOnly cookie
   ↓
5. API Requests
   Authorization: Bearer <access_token>
   ↓
6. Token Validation
   - Verify signature
   - Check expiration
   - Extract user roles
   ↓
7. RBAC Check
   - Validate required permissions
   - Allow/Deny access
```

#### Role Hierarchy

| Role | Permissions | Use Case |
|------|-------------|----------|
| `super_admin` | All permissions | System administrators |
| `admin` | Manage users, view all data | Department heads |
| `compliance_officer` | KYC, AML, reporting | Compliance team |
| `aml_analyst` | AML monitoring, SAR | AML specialists |
| `kyc_reviewer` | KYC verification | KYC team |
| `transaction_approver` | Approve/reject transactions | Operations |
| `auditor` | Read-only audit logs | Internal audit |
| `analyst` | View dashboards, reports | Business analysts |
| `viewer` | Read-only access | Stakeholders |

### Data Encryption

#### At Rest
- **Database:** PostgreSQL TDE (Transparent Data Encryption)
- **Backups:** AES-256 encryption before S3 upload
- **Sensitive Fields:** Application-level encryption (AES-GCM)

#### In Transit
- **External:** TLS 1.3 (HTTPS)
- **Internal:** mTLS between services (optional)
- **Database:** SSL/TLS connections

#### Encryption Key Management
- **Master Keys:** AWS KMS / HashiCorp Vault
- **Data Keys:** Envelope encryption pattern
- **Key Rotation:** Automated 90-day rotation

### Network Security

- **Firewall Rules:** Whitelist only necessary ports (443, 5432)
- **Network Policies:** Kubernetes NetworkPolicy for pod-to-pod
- **VPC:** Private subnets for databases
- **Bastion Host:** Jump server for SSH access

---

## Data Architecture

### Database Schema

#### Core Tables

```sql
-- Users and Authentication
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    roles TEXT[] NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Transactions
CREATE TABLE transactions (
    transaction_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    merchant_id VARCHAR(255) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL,
    risk_score INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_status (status)
);

-- Audit Reports
CREATE TABLE audit_reports (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    risk_level VARCHAR(50) NOT NULL,
    risk_score INTEGER NOT NULL,
    decision VARCHAR(50) NOT NULL,
    summary TEXT,
    suggestion TEXT,
    requires_manual_review BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_transaction_id (transaction_id),
    INDEX idx_risk_level (risk_level),
    INDEX idx_decision (decision)
);

-- Agent Execution Logs
CREATE TABLE agent_logs (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(255) NOT NULL,
    agent_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    latency_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_transaction_id (transaction_id),
    INDEX idx_agent_name (agent_name)
);

-- KYC Verification
CREATE TABLE kyc_verifications (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    kyc_level VARCHAR(50) NOT NULL,
    verification_status VARCHAR(50) NOT NULL,
    risk_score INTEGER,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id)
);

-- AML Alerts
CREATE TABLE aml_alerts (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    alert_type VARCHAR(100) NOT NULL,
    risk_level VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);
```

### Connection Pooling

```python
# Production settings
DB_POOL_SIZE=20          # Base connections
DB_MAX_OVERFLOW=40       # Additional connections under load
DB_POOL_TIMEOUT=30       # Max wait for connection (seconds)
DB_POOL_RECYCLE=3600     # Recycle connections every hour
```

**Capacity Calculation:**
- 3 pods × (20 base + 40 overflow) = 180 max connections
- PostgreSQL `max_connections` should be >= 200

---

## API Architecture

### Versioning Strategy

**URL-based versioning:**
```
/api/v1/audit/transaction
/api/v2/audit/transaction
```

**Deprecation Policy:**
- New versions announced 90 days in advance
- Old versions supported for 6 months
- Breaking changes require major version bump

### Endpoints

#### Health & Monitoring

```
GET /health
GET /metrics (Prometheus format)
GET /api/v1/health/ready
GET /api/v1/health/live
```

#### Authentication

```
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
```

#### Transaction Auditing

```
POST /api/v1/audit/transaction
GET /api/v1/audit/report/{transaction_id}
GET /api/v1/audit/logs/{transaction_id}
```

#### Compliance

```
POST /api/v1/kyc/verify
GET /api/v1/kyc/status/{user_id}
POST /api/v1/aml/check
GET /api/v1/aml/alerts
GET /api/v1/compliance/reports
```

### Rate Limiting

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1719312000
```

**Tiers:**
- **Anonymous:** 10 req/min
- **Authenticated:** 100 req/min
- **Premium:** 1000 req/min

---

## Disaster Recovery

### Backup Strategy

#### Database Backups

**Full Backup:**
- **Frequency:** Daily at 2 AM UTC
- **Retention:** 30 days
- **Storage:** S3 with encryption
- **Verification:** Weekly restore test

**Incremental Backup:**
- **Frequency:** Every 6 hours
- **Retention:** 7 days

**Point-in-Time Recovery (PITR):**
- **WAL archiving:** Continuous
- **Recovery window:** 7 days

#### Application Backups

- **Configuration:** Git repository
- **Docker images:** GHCR with tags
- **Knowledge base:** Daily snapshot to S3

### Recovery Procedures

#### Database Failure

**RTO:** 30 minutes  
**RPO:** 15 minutes (PITR)

```bash
# 1. Promote replica to primary
pg_ctl promote -D /var/lib/postgresql/data

# 2. Update application config
kubectl set env deployment/payguard-api \
  POSTGRES_HOST=new-primary-host

# 3. Rebuild replica
pg_basebackup -h new-primary -D /var/lib/postgresql/data -P -Xs
```

#### Complete System Failure

**RTO:** 2 hours  
**RPO:** 24 hours

```bash
# 1. Provision infrastructure (Terraform)
terraform apply -var="environment=production"

# 2. Restore database
aws s3 cp s3://backups/latest.sql.gz - | \
  gunzip | psql -h new-host -U payguard

# 3. Deploy application
kubectl apply -f k8s/production/

# 4. Verify and cutover DNS
```

---

## Compliance

### Regulatory Standards

- ✅ **PCI DSS 3.2.1** - Payment card data security
- ✅ **GDPR** - European data protection
- ✅ **SOC 2 Type II** - Security controls
- ✅ **ISO 27001** - Information security
- ✅ **CCPA** - California consumer privacy

### Audit Requirements

**Data Retention:**
- Transaction data: 7 years
- Audit logs: 5 years
- KYC documents: 5 years after account closure
- AML records: 5 years

**Audit Trail:**
- All API requests logged with correlation IDs
- User actions tracked with timestamps
- Data modifications recorded with before/after
- Security events escalated automatically

---

## Operational Procedures

### Deployment Process

1. **Code Review:** Minimum 2 approvals
2. **CI Pipeline:** Automated tests + security scans
3. **Staging Deployment:** Full validation
4. **Production Deployment:** Rolling update (zero downtime)
5. **Smoke Tests:** Automated health checks
6. **Monitoring:** Watch dashboards for 1 hour

### Incident Response

**Severity Levels:**
- **P0 (Critical):** System down, data breach
  - Response: Immediate, 24/7 on-call
- **P1 (High):** Degraded performance, partial outage
  - Response: Within 1 hour
- **P2 (Medium):** Non-critical bug
  - Response: Within 4 hours
- **P3 (Low):** Feature request, minor bug
  - Response: Next business day

---

## Contact & Support

**Technical Leads:**
- Architecture: architecture@example.com
- Security: security@example.com
- Operations: ops@example.com

**On-Call:**
- PagerDuty: payguard-oncall
- Escalation: CTO

---

**Document Owner:** Engineering Team  
**Review Cycle:** Quarterly  
**Next Review:** 2026-09-25
