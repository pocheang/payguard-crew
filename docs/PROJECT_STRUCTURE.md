# PayGuard Crew - Project Structure

## Directory Organization

```
payguard_crew_starter/
├── app/                          # Application source code
│   ├── agents/                   # AI Agent implementations
│   │   ├── prompts/             # 9 modular Agent prompts
│   │   ├── agent_factory.py     # Agent registry and factory
│   │   └── llm_client.py        # LLM integration layer
│   ├── api/                     # REST API endpoints
│   │   ├── audit.py            # Audit endpoints
│   │   ├── audit_secure.py     # Secured audit endpoints (recommended)
│   │   ├── auth.py             # Authentication endpoints
│   │   └── metrics.py          # Metrics and monitoring
│   ├── crew/                    # Multi-Agent orchestration
│   │   ├── agents/             # Modular agent runners (5 files)
│   │   ├── fallbacks/          # Modular fallback logic (3 files)
│   │   ├── audit_crew_refactored.py  # ⭐ Recommended (110 lines)
│   │   └── audit_crew.py       # Legacy (deprecated)
│   ├── compliance/              # Regulatory compliance
│   │   ├── aml_service.py      # Anti-Money Laundering
│   │   ├── kyc_service.py      # Know Your Customer
│   │   └── regulatory_reporting.py  # Regulatory reports
│   ├── db/                      # Database layer
│   │   ├── database_optimized.py    # ⭐ Optimized with indexes
│   │   ├── async_operations.py      # Async DB operations
│   │   └── repository.py       # Data access layer
│   ├── rules/                   # Risk rules engine
│   │   └── risk_rules_optimized.py  # ⭐ Deduplicated rules
│   ├── security/                # Security modules
│   │   ├── advanced_encryption.py   # Encryption services
│   │   ├── enhanced_audit.py   # Security audit trail
│   │   └── access_control.py   # RBAC implementation
│   └── utils/                   # Utility modules
│       ├── security.py         # Security validators
│       └── validation.py       # Input validation
├── data/                        # Sample data and database
│   └── sample_transaction_advanced.json
├── docs/                        # Documentation
│   ├── MIGRATION_GUIDE.md      # Legacy to refactored migration
│   └── PROJECT_STRUCTURE.md    # This file
├── tests/                       # Test suites
├── .github/workflows/           # CI/CD pipelines
├── README.md                    # ⭐ Main documentation
├── CHANGELOG.md                 # ⭐ Complete version history
├── ARCHITECTURE_OPTIMIZATION.md # System architecture details
└── AGENT_SPECIFICATIONS.md     # Agent specifications

⭐ = Recommended / Primary files
```

## Key Files

### Documentation (Must Read)
1. **README.md** - Start here
2. **CHANGELOG.md** - Version history
3. **ARCHITECTURE_OPTIMIZATION.md** - Architecture details
4. **AGENT_SPECIFICATIONS.md** - Agent capabilities

### Code Entry Points
1. **app/main.py** - Application entry point
2. **app/crew/audit_crew_refactored.py** - Main workflow (recommended)
3. **app/api/audit_secure.py** - Secure API endpoints (recommended)

### Configuration
1. **.env** - Environment variables
2. **requirements.txt** - Python dependencies
3. **docker-compose.yml** - Docker configuration

## Module Relationships

```
User Request
    ↓
FastAPI (app/main.py)
    ↓
API Layer (app/api/audit_secure.py)
    ↓
Multi-Agent Orchestration (app/crew/audit_crew_refactored.py)
    ↓
┌─────────────┬─────────────┬─────────────┐
│ Agents      │ Rules       │ Database    │
│ (prompts/)  │ (rules/)    │ (db/)       │
└─────────────┴─────────────┴─────────────┘
    ↓
Security & Validation (utils/security.py, utils/validation.py)
    ↓
Response
```

---

Last Updated: 2026-06-25
Version: 0.1.9
