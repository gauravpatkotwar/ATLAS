# ATLAS - Project Summary

## Overview
ATLAS is an enterprise-grade AI-powered Recruitment Operating System built with Clean Architecture, Domain-Driven Design, and modern technology stack.

## Architecture

### Backend (FastAPI + Python 3.13)
```
backend/
├── app/
│   ├── core/                    # Core infrastructure
│   │   ├── config.py           # Pydantic settings management
│   │   ├── database.py         # SQLAlchemy 2.x async setup
│   │   ├── security.py         # JWT RS256, password hashing, MFA
│   │   ├── exceptions.py       # Custom exception hierarchy
│   │   └── logging.py          # Structured logging with structlog
│   ├── domain/                 # Domain layer (shared)
│   │   ├── base.py             # Entity, ValueObject, AggregateRoot, DomainEvent
│   │   └── repositories.py     # Repository interfaces (Ports)
│   ├── application/            # Application layer (shared)
│   │   └── base.py             # CQRS: Command, Query, Handler, MessageBus
│   ├── infrastructure/         # Infrastructure layer (shared)
│   │   ├── ai/                 # AI Provider abstraction
│   │   │   ├── providers/      # Ollama, OpenAI, NVIDIA providers
│   │   │   └── service.py      # AI service with logging/retries
│   │   └── vector_db/          # Vector database abstraction
│   │       ├── faiss_store.py  # FAISS implementation
│   │       └── chroma_store.py # ChromaDB implementation
│   └── modules/                # Business modules (14 modules)
│       ├── auth/               # Authentication & Authorization
│       ├── companies/          # Multi-tenant company management
│       ├── users/              # User management
│       ├── candidates/         # Candidate management
│       ├── jobs/               # Job & pipeline management
│       ├── matching/           # Semantic search & matching
│       ├── atlas_brain/        # Long-term memory & knowledge graph
│       ├── atlas_one/          # AI Recruiter Assistant
│       ├── communication/      # Email, chat, scheduling
│       ├── interview_intelligence/ # Interview recording & analysis
│       ├── analytics/          # Hiring analytics & reporting
│       ├── workflows/          # Workflow automation
│       ├── admin/              # Enterprise administration
│       └── api_platform/       # API platform & webhooks
├── tests/                      # Test suite
├── alembic/                    # Database migrations
└── scripts/                    # Utility scripts
```

### Frontend (React + TypeScript + Vite)
```
frontend/
├── src/
│   ├── components/            # Reusable UI components
│   │   ├── ui/               # ShadCN UI components
│   │   └── layout/           # Layout components
│   ├── pages/                # Page components
│   │   ├── auth/             # Login, Register pages
│   │   ├── dashboard/        # Dashboard page
│   │   ├── candidates/       # Candidate management
│   │   ├── jobs/             # Job management
│   │   ├── matching/         # AI matching
│   │   ├── atlas-one/        # AI Assistant
│   │   └── settings/         # Settings page
│   ├── layouts/              # Layout components
│   ├── lib/                  # Utilities & API client
│   │   ├── api.ts           # Axios instance with interceptors
│   │   ├── auth.tsx         # Auth context & provider
│   │   └── utils.ts         # Helper functions
│   └── hooks/               # Custom React hooks
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
└── Dockerfile
```

## Implemented Modules

### 1. Authentication Module (`auth/`)
- **Entities**: User, Tenant, UserSession, APIKey, Role, AuditLog
- **Features**: 
  - JWT RS256 with refresh token rotation
  - Multi-factor authentication (TOTP)
  - Role-based access control (7 roles, 50+ permissions)
  - Password policies & lockout protection
  - Email verification & password reset
  - API key management
  - Comprehensive audit logging

### 2. Companies Module (`companies/`)
- **Entities**: Tenant, Department, Integration, Webhook, APIKey, FeatureFlag
- **Features**:
  - Multi-tenant isolation
  - Custom branding (colors, logo, domain)
  - Subscription management (5 plans)
  - Feature flags with rollout percentages
  - Webhook system with retry policies
  - Integration management (LinkedIn, Indeed, etc.)

### 3. Candidates Module (`candidates/`)
- **Entities**: Candidate, Experience, Education, Project, Document, TimelineEvent
- **Features**:
  - Resume parsing (PDF, DOCX, TXT)
  - Skill embeddings for semantic search
  - AI-powered profile enrichment
  - Document management
  - Candidate timeline/activity feed

### 4. Jobs Module (`jobs/`)
- **Entities**: Job, Pipeline, PipelineStage, JobTeamMember, InterviewTemplate, ScorecardTemplate
- **Features**:
  - Customizable hiring pipelines
  - Drag-and-drop pipeline builder
  - Job team collaboration
  - Interview templates & scorecards
  - Application tracking with stages

### 5. Matching Module (`matching/`)
- **Entities**: CandidateMatch, JobSearchIndex, CandidateSearchIndex, SavedSearch
- **Features**:
  - Semantic search with embeddings
  - Hybrid matching (semantic + keyword + skill + experience + education + location)
  - AI-powered reranking
  - Match reasoning & explanations
  - Real-time match scoring

### 6. Atlas Brain Module (`atlas_brain/`)
- **Entities**: Memory, MemoryRelation, KnowledgeGraphEntity, KnowledgeGraphRelation, ConversationMemory, RecruiterMemory, DecisionMemory
- **Features**:
  - Persistent long-term memory
  - Knowledge graph with semantic relationships
  - Retrieval-Augmented Generation (RAG)
  - Multi-type memory (candidate, recruiter, company, decision, conversation)
  - Memory ingestion & entity extraction

### 7. Atlas One Module (`atlas_one/`)
- **Features**:
  - Conversational AI recruiter assistant
  - Job description generation
  - Interview question generation
  - Email & offer letter generation
  - Candidate summaries & explanations
  - Context-aware recommendations

### 8. Infrastructure Modules
- **AI Providers**: Ollama (local), OpenAI, NVIDIA with factory pattern
- **Vector Databases**: FAISS (local), ChromaDB, pgvector
- **Security**: Rate limiting, CORS, JWT, MFA, audit logging
- **Monitoring**: Prometheus metrics, structured logging, health checks

## Key Technical Decisions

### Clean Architecture
- Strict layer separation: Domain → Application → Infrastructure → Presentation
- Dependency inversion via repository interfaces (Ports)
- No framework code in domain layer

### Domain-Driven Design
- Aggregates with invariants
- Domain events for cross-module communication
- Value objects for immutable concepts
- Repository pattern for data access

### Multi-Tenancy
- Tenant ID on all entities
- Row-level security via repository filters
- Shared database, shared schema approach
- Complete data isolation

### AI-First Design
- Provider abstraction for LLM/embedding/reranking
- Structured output with Pydantic models
- Streaming support
- Request logging & cost tracking
- Retry logic with exponential backoff

### Security
- RS256 JWT with key rotation support
- bcrypt password hashing (12 rounds)
- TOTP MFA with backup codes
- Rate limiting (login, API, AI)
- Input validation with Pydantic
- SQL injection prevention via ORM

## Development Workflow

### Quick Start
```bash
# 1. Clone & configure
git clone <repo>
cd ATLAS
cp .env.example .env

# 2. Generate JWT keys
./scripts/generate-keys.sh

# 3. Start with Docker
docker-compose up -d

# 4. Access services
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# Docs:     http://localhost:8000/docs
```

### Local Development
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Testing
```bash
# Backend
cd backend
pytest                    # All tests
pytest -m unit           # Unit tests
pytest -m integration    # Integration tests
pytest --cov=app         # With coverage

# Frontend
cd frontend
npm run test             # Vitest
npm run test:ui          # With UI
```

### Code Quality
```bash
# Backend
ruff check .             # Linting
ruff format .            # Formatting
mypy app/                # Type checking
bandit -r app/           # Security scan

# Frontend
npm run lint             # ESLint
npx tsc --noEmit        # Type checking
npx prettier --check .  # Formatting check
```

## Deployment

### Docker Production Build
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Environment Variables (Production)
```env
ENVIRONMENT=production
DEBUG=false
DATABASE_HOST=prod-db
DATABASE_PASSWORD=secure-password
AUTH_SECRET_KEY=generated-32-char-key
AUTH_PRIVATE_KEY_PATH=/secrets/private.pem
AUTH_PUBLIC_KEY_PATH=/secrets/public.pem
MONITORING_SENTRY_DSN=https://...
MONITORING_LOG_LEVEL=INFO
```

### Kubernetes (Planned)
- Helm charts for all services
- Horizontal pod autoscaling
- PostgreSQL operator
- Redis operator
- Ingress with TLS
- Cert-manager for certificates

## API Documentation
- OpenAPI 3.0 specification at `/openapi.json`
- Swagger UI at `/docs`
- ReDoc at `/redoc`
- Versioned API: `/api/v1/`

## Monitoring & Observability
- **Metrics**: Prometheus at `/metrics`
- **Logging**: Structured JSON logs
- **Tracing**: OpenTelemetry (planned)
- **Health**: `/health` and `/health/ready`
- **Alerting**: Sentry integration

## Roadmap
- [ ] Communication module (email, SMS, chat)
- [ ] Interview Intelligence (recording, transcription, analysis)
- [ ] Analytics dashboard (charts, reports)
- [ ] Workflow automation builder
- [ ] Enterprise SSO (SAML, OIDC)
- [ ] Mobile app (React Native)
- [ ] Marketplace integrations
- [ ] Advanced AI features (voice, video)

## License
MIT License - see LICENSE file for details.

## Contributing
1. Fork the repository
2. Create feature branch
3. Write tests
4. Ensure CI passes
5. Submit PR with description

---

Built with ❤️ for modern recruitment teams