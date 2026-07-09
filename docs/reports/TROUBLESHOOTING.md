# 🔧 Quick Fix Guide - Common Issues

## Import Errors

### Issue: `ModuleNotFoundError: No module named 'app.core'`

**Solution:**
```bash
# Make sure you're in the project directory
cd payguard_crew_starter

# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-prod.txt  # For production features
```

### Issue: `ImportError: cannot import name 'get_logger'`

**Solution:**
The new structured logging module is at `app.core.logging`. Update imports:
```python
from app.core.logging import get_logger, setup_logging
```

---

## Database Errors

### Issue: `ValueError: SQLite is not suitable for production`

**Solution:**
Set `DATABASE_TYPE` in your `.env` file:
```env
# For development
DATABASE_TYPE=sqlite

# For production
DATABASE_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PASSWORD=your_password
```

### Issue: `ModuleNotFoundError: No module named 'psycopg2'`

**Solution:**
```bash
pip install psycopg2-binary
```

---

## Authentication Errors

### Issue: `ModuleNotFoundError: No module named 'jwt'`

**Solution:**
```bash
pip install PyJWT passlib[bcrypt]
```

### Issue: `JWT_SECRET_KEY must be changed in production`

**Solution:**
Generate a secure secret key:
```bash
# Linux/Mac
openssl rand -hex 32

# Windows (PowerShell)
python -c "import secrets; print(secrets.token_hex(32))"
```

Then add to `.env.production`:
```env
JWT_SECRET_KEY=your_generated_key_here
```

---

## Tracing/Monitoring Errors

### Issue: `ModuleNotFoundError: No module named 'opentelemetry'`

**Solution:**
```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi
```

**OR** disable tracing:
```env
OTEL_ENABLED=false
```

### Issue: `ModuleNotFoundError: No module named 'sentry_sdk'`

**Solution:**
```bash
pip install sentry-sdk[fastapi]
```

**OR** skip Sentry (it's optional):
```env
# Don't set SENTRY_DSN
```

---

## Startup Errors

### Issue: Application won't start

**Quick Fix:**
```bash
# 1. Check Python version
python --version  # Should be 3.9+

# 2. Reinstall all dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Set minimal environment
export APP_ENV=dev
export DATABASE_TYPE=sqlite
export LLM_PROVIDER=disabled

# 4. Try starting
uvicorn app.main:app --reload
```

### Issue: `lifespan` errors

**Solution:**
Update FastAPI to the latest version:
```bash
pip install --upgrade fastapi uvicorn
```

---

## Testing the Application

### Quick Health Check
```bash
# Start the server
uvicorn app.main:app --reload

# In another terminal, test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/

# Expected output:
# {"status": "ok", "service": "payguard-crew", "version": "0.2.0"}
```

### Test Authentication
```bash
# Login (default users: admin/admin123, demo/demo123)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# You'll get an access_token, use it:
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Minimal Working Configuration

Create `.env` with these minimal settings:

```env
# Minimal configuration for testing
APP_NAME=payguard-crew
APP_ENV=dev

# Use SQLite for quick testing
DATABASE_TYPE=sqlite
SQLITE_DB_PATH=./payguard_crew.db

# Disable optional features
LLM_PROVIDER=disabled
ENABLE_CREWAI=false
OTEL_ENABLED=false
# Don't set SENTRY_DSN

# Simple JWT config (dev only!)
JWT_SECRET_KEY=dev-secret-key-change-in-production
```

Then start:
```bash
uvicorn app.main:app --reload
```

---

## Step-by-Step Fresh Setup

```bash
# 1. Clean install
rm -rf venv/
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Create minimal .env
cat > .env << EOF
APP_ENV=dev
DATABASE_TYPE=sqlite
LLM_PROVIDER=disabled
ENABLE_CREWAI=false
OTEL_ENABLED=false
JWT_SECRET_KEY=dev-secret-change-in-prod
EOF

# 4. Start application
uvicorn app.main:app --reload

# 5. Test in browser
# Open: http://localhost:8000/docs
```

---

## Production Checklist

Before deploying to production:

- [ ] Change `JWT_SECRET_KEY` to a secure random value
- [ ] Set `DATABASE_TYPE=postgresql` (not sqlite)
- [ ] Configure `POSTGRES_PASSWORD` securely
- [ ] Set `APP_ENV=production`
- [ ] Configure `API_KEYS` for API authentication
- [ ] Enable HTTPS/TLS
- [ ] Review all environment variables in `.env.production.template`
- [ ] Run security scan: `bandit -r app/`
- [ ] Test authentication flow
- [ ] Verify database connections
- [ ] Check logs are structured JSON

---

## Getting Help

If issues persist:

1. Check the full error traceback
2. Verify Python version: `python --version` (need 3.9+)
3. Check installed packages: `pip list`
4. Review logs in console output
5. Check documentation:
   - [DEPLOYMENT.md](DEPLOYMENT.md)
   - [ENTERPRISE_ARCHITECTURE.md](ENTERPRISE_ARCHITECTURE.md)
   - [SECURITY_SECTION.md](SECURITY_SECTION.md)

---

## Common Commands Reference

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Run tests
pytest tests/ -v

# Check code
ruff check app/
mypy app/

# Database
alembic upgrade head  # Run migrations

# Docker
docker build -t payguard-crew .
docker run -p 8000:8000 --env-file .env payguard-crew
```
