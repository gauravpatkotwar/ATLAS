# ATLAS Enterprise AI Recruiting Platform

ATLAS is a production-grade, AI-powered Applicant Tracking System (ATS) designed around Clean Architecture principles. It handles resume uploads, extracts structured candidate details using LLMs, index embeddings into a FAISS vector database, calculates candidate recommendations matching job specs, and provides a Recruiter Copilot conversational assistant.

---

## Technical Stack & Architecture

### Clean Architecture Layers
```
[FastAPI Router API]  --> Thin controllers, request/response validation Pydantic schemas.
        ↓
[Services Layer]       --> Business logic orchestration, validation, transaction pipelines.
        ↓
[Repositories Layer]   --> Encapsulates database queries (SQLAlchemy, PostgreSQL/SQLite).
        ↓
[Database Model Base]  --> Persisted database tables (User, Candidate, Job, AuditLog).
```

### isolated Infrastructure Plugins
- **AI Provider**: routed Ollama models (`phi4-mini` for parsing/summary, `qwen3:8b` for chat/explanations, `nomic-embed-text` for vector indexing).
- **FAISS Vector Search**: L2-normalized cosine similarity matching.
- **Workflow Engine**: Transactional sequential steps, exponential retry backoff, and reverse-order rollback.
- **Security**: JWT-based bearer authentication, password hashing, and role-based access rules.

---

## Directory Structure

```
├── src/
│   ├── atlas/
│   │   ├── main.py             # FastAPI entrypoint, lifespan startup database check.
│   │   ├── api/                # Route controllers & dependencies.
│   │   ├── services/           # Authentication, candidate pipeline, job, copilot.
│   │   ├── repositories/       # SQLAlchemy queries (Base, Candidate, Job, AuditLog).
│   │   ├── database/           # Models definitions and Session creator.
│   │   ├── ai/                 # Providers interface, Ollama implementation.
│   │   ├── vector/             # FAISS store index.
│   │   ├── parser/             # PDF, DOCX, TXT parser.
│   │   ├── workflow/           # State context and sequential transaction engine.
│   │   └── config/             # Pydantic Settings.
│   └── tests/                  # Pytest unit & integration tests.
├── frontend/                   # React + TypeScript + Vite client.
├── docker/                     # Nginx configurations and Dockerfiles.
├── docker-compose.yml          # Postgres, Redis, Ollama, Frontend, Backend orchestration.
└── requirements.txt            # Python dependencies.
```

---

## Run and Verification

### 1. Build and Run via Docker Compose
Ensure Docker is installed and running, then execute:
```bash
docker compose up --build -d
```

Once started, download the required Ollama models inside the container:
```bash
docker exec -it atlas_ollama ollama pull phi4-mini
docker exec -it atlas_ollama ollama pull qwen3:8b
docker exec -it atlas_ollama ollama pull nomic-embed-text
```

Access the application:
- Frontend Client Dashboard: `http://localhost`
- Swagger API Docs: `http://localhost:8000/docs`

### 2. Verify with Local Test Suite
To execute the automated Python test suite, setup a local virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest --cov=src/atlas tests/
```

To verify code quality and formatting:
```bash
black --check src/
ruff check src/
mypy src/
```
