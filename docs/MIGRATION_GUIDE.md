# Migration Guide - Legacy to Refactored Code

## Overview

PayGuard Crew has been refactored for better maintainability. This guide helps you migrate from legacy implementations to the new modular architecture.

## Deprecated Files

### 1. audit_crew.py → audit_crew_refactored.py

**Legacy** (500 lines):
```python
from app.crew.audit_crew import run_audit_crew
```

**New** (110 lines):
```python
from app.crew.audit_crew_refactored import run_audit_crew
```

**Benefits**:
- 78% code reduction
- Modular agent runners (agents/ directory)
- Modular fallbacks (fallbacks/ directory)
- Easier to test and maintain

**Breaking Changes**: None - Function signature is identical

### 2. fallbacks.py → fallbacks/ directory

**Legacy** (255 lines):
```python
from app.crew.fallbacks import (
    build_transaction_result,
    build_fraud_detection_result
)
```

**New** (Modular):
```python
# For core agents
from app.crew.fallbacks.core_fallbacks import (
    build_transaction_result,
    build_compliance_result
)

# For risk detection agents
from app.crew.fallbacks.risk_fallbacks import (
    build_fraud_detection_result,
    build_merchant_risk_result
)
```

**Benefits**:
- Organized by agent category
- Smaller files (~100 lines each)
- Easier to locate specific fallback logic

**Breaking Changes**: Import paths changed

## Migration Steps

### Step 1: Update Imports (Recommended)

```python
# Old
from app.crew.audit_crew import run_audit_crew
from app.crew.fallbacks import build_fraud_detection_result

# New
from app.crew.audit_crew_refactored import run_audit_crew
from app.crew.fallbacks.risk_fallbacks import build_fraud_detection_result
```

### Step 2: Test Thoroughly

Both versions produce identical outputs. Run your test suite to verify.

### Step 3: Remove Legacy Dependencies

Once migration is complete, you can safely ignore legacy files.

## Timeline

- **Now - v0.1.x**: Both versions coexist
- **v0.2.0**: Legacy files will be removed

## Need Help?

If you encounter issues during migration, please file an issue on GitHub.

---

Last Updated: 2026-06-25
Version: v0.1.9
