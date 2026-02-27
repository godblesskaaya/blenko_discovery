# Blenko Discovery System — Backend

FastAPI backend for the Blenko Discovery sales intelligence tool.  
**Sprint 1**: Database foundation + Layer Zero API + D1 Scoring Engine.

---

## Quick Start

### 1. Prerequisites
- Python 3.11+
- PostgreSQL 15+ (or Docker)
- Git

### 2. Install dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your database URL and JWT secret
```

### 4. Start database (Docker option)

```bash
# From project root
docker-compose up postgres -d
```

### 5. Run migrations

```bash
cd backend
alembic upgrade head
```

### 6. Seed framework content

```bash
python -m seeds.framework_content
```

### 7. Start the API

```bash
uvicorn main:app --reload
# API available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

---

## Run with Docker (full stack)

```bash
# From project root
docker-compose up --build
```

---

## Run Tests

```bash
cd backend
pytest -v
```

Tests use SQLite in-memory — no PostgreSQL required.

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://blenko:blenko@localhost:5432/blenko_discovery` |
| `JWT_SECRET_KEY` | Secret for signing JWTs — **change in production** | `change-this...` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `APP_ENV` | `development` or `production` | `development` |

---

## API Overview

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Login, returns access + refresh tokens |
| `POST` | `/api/auth/refresh` | Exchange refresh token for new access token |
| `GET` | `/api/auth/me` | Current user info |
| `POST` | `/api/auth/register` | Admin: create new user |
| `POST` | `/api/sessions/create` | Start new discovery session (Layer Zero) |
| `GET` | `/api/sessions/{id}` | Load full session state |
| `PATCH` | `/api/sessions/{id}/autosave` | Auto-save any field change |
| `PATCH` | `/api/sessions/{id}/complete` | Mark session complete |
| `GET` | `/api/sessions/` | Dashboard: list sessions |
| `POST` | `/api/sessions/{id}/pain-flags` | Create pain flag |
| `GET` | `/api/sessions/{id}/pain-flags` | List pain flags for session |
| `POST` | `/api/sessions/{id}/notes` | Add free-form note |
| `POST` | `/api/scoring/{id}/signal` | **Core**: update signal score → instant recalculation |
| `GET` | `/api/scoring/{id}/dimension/{dim}` | Get dimension score snapshot |
| `GET` | `/api/scoring/{id}/overall` | Overall score + grade |
| `POST` | `/api/scoring/{id}/trigger/{dim}/acknowledge` | Mark trigger deployed |
| `GET` | `/api/scoring/{id}/framework/{dim}` | Get framework content (questions, probes, reframes) |

Full interactive docs: `http://localhost:8000/docs`

Compatibility aliases are also available for Sprint 1 clients:
- `POST /api/scoring/signal`
- `GET /api/scoring/dimension/{interaction_id}/{dimension}`
- `GET /api/scoring/overall/{interaction_id}`

---

## Architecture Notes

### Scoring Engine
- `services/scoring_engine.py` — core logic, no business rules in routes
- Signal updates trigger immediate dimension recalculation (target <100ms)
- Append-only audit trail: `signal_scores.score_history` JSONB preserves all previous values
- Trigger text loaded from DB — not hardcoded — supports framework versioning

### Framework Content
- All questions, probes, signals, and reframes stored in `framework_*` tables
- `framework_version` field on all content + score records ensures historical sessions
  always render with the framework version that was active when they were conducted
- Re-seed with `python -m seeds.framework_content` (idempotent — safe to re-run)

### Database
- 12 core entities (design doc Section 6) + 5 framework content tables
- All FKs enforced at DB level
- Alembic for all schema changes — no direct SQL manipulation
- ERPNext IDs stored as nullable VARCHAR for Phase 3 integration

---

## Sprint 1 Checklist

- [x] All 12 database entities + framework content tables
- [x] Alembic migration setup
- [x] Framework content seed (all 4 dimensions: probes, signals, reframes, triggers)
- [x] FastAPI project scaffolding
- [x] JWT authentication (access + refresh tokens)
- [x] Role-based access control (rep/domain_expert/manager/admin)
- [x] Layer Zero API (create, retrieve, autosave)
- [x] D1 Scoring Engine with recalculation on every signal change
- [x] All 4 dimension scoring logic (D1–D4)
- [x] Pain flag creation and retrieval
- [x] Free-form notes
- [x] Session dashboard list
- [x] Unit tests: grade calculation, all tier boundaries, audit trail
- [x] Integration tests: session flow, scoring API
- [x] Docker + docker-compose
- [x] `/health` endpoint for DevOps
