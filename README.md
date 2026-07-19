# ATLAS - AI-Powered Recruitment Operating System

[![CI/CD](https://github.com/your-org/atlas/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/your-org/atlas/actions)
[![Codecov](https://codecov.io/gh/your-org/atlas/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/atlas)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An enterprise-grade SaaS recruitment platform combining Applicant Tracking System (ATS), AI recruiter assistant, semantic search, interview intelligence, workflow automation, analytics, and enterprise administration.

## 🚀 Features

### Core Platform
- **Multi-tenant Architecture** - Complete tenant isolation with row-level security
- **Role-Based Access Control** - Granular permissions with 7 built-in roles
- **Authentication & Authorization** - JWT (RS256), refresh tokens, MFA (TOTP), API keys
- **Audit Logging** - Comprehensive activity tracking for compliance

### AI-Powered Recruitment
- **Atlas One** - Conversational AI recruiter assistant
- **Semantic Search** - Vector-based candidate/job matching using embeddings
- **AI Job Description Generation** - Auto-generate JDs from requirements
- **AI Interview Questions** - Tailored questions per role/candidate
- **AI Email Generation** - Personalized candidate communication
- **AI Offer Letters** - Automated offer generation
- **Candidate Summarization** - AI-powered profile summaries

### Atlas Brain (Memory System)
- **Persistent Long-term Memory** - Candidate, recruiter, company, decision, conversation memory
- **Knowledge Graph** - Semantic relationships between entities
- **Retrieval-Augmented Generation (RAG)** - Context-aware AI responses
- **Decision History** - Track and learn from hiring decisions

### Candidate Management
- Resume parsing (PDF, DOCX, TXT)
- Structured profiles (experience, education, skills, projects)
- Document management
- Timeline & activity tracking
- Skill embeddings for semantic matching

### Job & Pipeline Management
- Customizable hiring pipelines
- Drag-and-drop pipeline builder
- Job templates & approval workflows
- Team collaboration
- Interview scheduling & templates
- Scorecards & evaluation forms

### Analytics & Reporting
- Hiring funnel metrics
- Time-to-hire tracking
- Source effectiveness
- Diversity reporting
- Recruiter productivity
- Custom dashboards

### Workflow Automation
- Visual workflow builder
- Trigger-based automation
- Approval chains
- Notification engine
- SLA tracking

### Communication
- Email integration (SendGrid, SES, SMTP)
- Interview scheduling
- Calendar integration
- Template management

### Enterprise Administration
- Tenant management
- Feature flags
- Billing & subscription management
- System settings
- SSO/OAuth support (planned)

## 🏗 Architecture

### Clean Architecture Layers
```
app/
├── core/                 # Core infrastructure (config, database, security, logging)
├── domain/               # Domain layer (base entities, repositories, events)
├── application/          # Application layer (commands, queries, handlers)
├── infrastructure/       # Infrastructure implementations
├── presentation/         # API routes, schemas
└── modules/              # Business modules (bounded contexts)
    ├── auth/
    ├── companies/
    ├── users/
    ├── candidates/
    ├── jobs/
    ├── matching/
    ├── atlas_brain/
    ├── atlas_one/
    ├── communication/
    ├── interview_intelligence/
    ├── analytics/
    ├── workflows/
    ├── admin/
    └── api_platform/
```

### Key Principles
- **Domain-Driven Design** - Bounded contexts, aggregates, domain events
- **SOLID Principles** - Single responsibility, open/closed, Liskov substitution, interface segregation, dependency inversion
- **Repository Pattern** - Abstract data access behind interfaces
- **Dependency Injection** - Inversion of control via FastAPI dependencies
- **CQRS** - Separate read/write models for complex domains
- **Event-Driven** - Domain events for cross-module communication

## 🛠 Technology Stack

### Backend
| Component | Technology |
|-----------|------------|
| Language | Python 3.13 |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x (async) |
| Database | PostgreSQL 16 + pgvector |
| Cache/Queue | Redis 7 + Celery |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (RS256), Passlib (bcrypt) |
| AI | Ollama (Qwen3, Phi4), OpenAI API |
| Vector DB | FAISS, ChromaDB |
| Monitoring | Prometheus, OpenTelemetry, Sentry |
| Testing | pytest, pytest-asyncio, httpx |

### Frontend
| Component | Technology |
|-----------|------------|
| Language | TypeScript |
| Framework | React 18 |
| Build Tool | Vite |
| Styling | TailwindCSS + ShadCN UI |
| State | TanStack Query + Zustand |
| Routing | React Router v6 |
| Forms | React Hook Form + Zod |
| Charts | Recharts |

### Infrastructure
| Component | Technology |
|-----------|------------|
| Containerization | Docker, Docker Compose |
| Orchestration | Kubernetes (planned) |
| CI/CD | GitHub Actions |
| Registry | GitHub Container Registry |

## 📦 Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for frontend development)
- Python 3.13+ (for backend development)
- Git

### Quick Start with Docker

```bash
# Clone repository
git clone https://github.com/your-org/atlas.git
cd atlas

# Copy environment template
cp .env.example .env

# Generate JWT keys
./scripts/generate-keys.sh

# Start all services
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f backend
```

### Service URLs
| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |
| Flower (Celery) | http://localhost:5555 |
| ChromaDB | http://localhost:8001 |
| Ollama | http://localhost:11434 |

### Local Development

#### Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment
cp ../.env.example .env

# Generate keys
../scripts/generate-keys.sh

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest -m unit          # Unit tests
pytest -m integration   # Integration tests
pytest -m api           # API tests
pytest -m slow          # Slow tests
```

### Frontend Tests
```bash
cd frontend

# Run tests
npm run test

# Run with UI
npm run test:ui

# Run with coverage
npm run test -- --coverage
```

## 📚 API Documentation

The API follows RESTful conventions with:
- Versioned endpoints: `/api/v1/`
- Standardized error responses
- Pagination, filtering, sorting
- OpenAPI 3.0 specification

Access interactive documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Authentication
All API endpoints (except auth) require a Bearer token:
```
Authorization: Bearer <access_token>
X-Tenant-ID: <tenant_uuid>  # Optional, extracted from token
```

### Rate Limiting
Default limits:
- Auth endpoints: 5 requests/5 min
- API endpoints: 1000 requests/min
- AI endpoints: 50 requests/min
- Upload endpoints: 10 requests/hour

## 🔧 Configuration

### Environment Variables

Key configuration options (see `.env.example` for complete list):

```bash
# Application
ENVIRONMENT=development
DEBUG=true
API_PREFIX=/api/v1

# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME=atlas

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# AI Providers
AI_DEFAULT_PROVIDER=ollama
AI_OLLAMA_BASE_URL=http://localhost:11434
AI_OPENAI_API_KEY=your-key

# Auth
AUTH_SECRET_KEY=your-secret-key
AUTH_PRIVATE_KEY_PATH=./keys/private.pem
AUTH_PUBLIC_KEY_PATH=./keys/public.pem

# CORS
CORS_ALLOW_ORIGINS=["http://localhost:3000"]

# Monitoring
MONITORING_LOG_LEVEL=DEBUG
MONITORING_LOG_FORMAT=console
```

### AI Model Configuration

The system supports multiple AI providers:
- **Ollama** (local): Qwen3, Phi4-mini, nomic-embed-text
- **OpenAI**: GPT-4o, text-embedding-3-large
- **NVIDIA**: Nemotron models (planned)

Configure models in `.env`:
```bash
AI_OPENAI_MODEL=gpt-4o
AI_EMBEDDING_MODEL=text-embedding-3-large
AI_EMBEDDING_DIMENSIONS=3072
```

## 🔐 Security

### Implemented Security Measures
- **OWASP Top 10** compliance
- **JWT with RS256** asymmetric encryption
- **Password hashing** with bcrypt (configurable rounds)
- **Rate limiting** on all endpoints
- **Tenant isolation** at database level
- **Input validation** with Pydantic
- **SQL injection prevention** via SQLAlchemy ORM
- **CORS configuration** with allowlist
- **Security headers** via middleware
- **Audit logging** for all mutations

### Secrets Management
- Never commit secrets to repository
- Use `.env` for local development
- Use Kubernetes secrets / Vault in production
- Rotate keys regularly

## 🚀 Deployment

### Production Checklist
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Configure strong `AUTH_SECRET_KEY`
- [ ] Generate production RSA keys
- [ ] Configure PostgreSQL with SSL
- [ ] Configure Redis with authentication
- [ ] Set up Sentry DSN
- [ ] Configure email provider
- [ ] Set up object storage (S3/GCS)
- [ ] Configure CDN for static assets
- [ ] Set up monitoring & alerting
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

### Kubernetes Deployment (Planned)
```yaml
# Example K8s resources
- Deployment (backend, frontend, celery-worker, celery-beat)
- Service (ClusterIP)
- Ingress (NGINX)
- ConfigMap & Secrets
- HorizontalPodAutoscaler
- PodDisruptionBudget
```

## 📁 Project Structure

```
ATLAS/
├── .github/
│   └── workflows/         # CI/CD pipelines
├── backend/
│   ├── app/
│   │   ├── core/         # Config, database, security, logging
│   │   ├── domain/       # Base domain classes
│   │   ├── application/  # Base application classes
│   │   ├── infrastructure/ # Infrastructure implementations
│   │   ├── presentation/ # API routing
│   │   └── modules/      # Business modules
│   ├── tests/            # Test suite
│   ├── scripts/          # Utility scripts
│   ├── alembic/          # Database migrations
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── pytest.ini
├── frontend/
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Page components
│   │   ├── layouts/      # Layout components
│   │   ├── lib/          # Utilities, API client
│   │   └── hooks/        # Custom React hooks
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── scripts/              # Project scripts
├── docker-compose.yml    # Development environment
├── .env.example          # Environment template
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- **Backend**: Ruff (linting) + Black (formatting) + MyPy (type checking)
- **Frontend**: ESLint + Prettier + TypeScript strict mode
- **Commits**: Conventional Commits specification

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL toolkit
- [Pydantic](https://pydantic.dev/) - Data validation
- [React](https://react.dev/) - UI library
- [TailwindCSS](https://tailwindcss.com/) - Utility-first CSS
- [ShadCN UI](https://ui.shadcn.com/) - Beautiful components
- [Ollama](https://ollama.ai/) - Local AI models
- [pgvector](https://github.com/pgvector/pgvector) - Vector similarity search

## 📞 Support

- **Documentation**: [docs.atlas.example.com](https://docs.atlas.example.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/atlas/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/atlas/discussions)
- **Email**: support@atlas.example.com

---

Built with ❤️ by the ATLAS Team