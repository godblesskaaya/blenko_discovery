# Blenko Discovery System — DevOps Deployment Plan
**Sprint 1 | Version 1.0.1 | Prepared: 26 February 2026**

---

## Overview

Step-by-step execution guide to take the Blenko Discovery System from existing frontend/backend folders to a fully deployed, HTTPS-secured, CI/CD-automated production environment at `https://discovery.blenkotechnologies.co.tz`.

**Assumed starting point:**
- `frontend/` folder exists (React app)
- `backend/` folder exists (FastAPI app)
- VPS is accessible via SSH
- **Traefik is already running on the VPS as the reverse proxy**
- Domain DNS is pointed at the VPS IP

**What Traefik already handles (you do NOT need to set up):**
- SSL/TLS termination
- Let's Encrypt certificate issuance and renewal
- HTTP → HTTPS redirect
- Routing traffic to the right container

**What this plan covers:**
- Docker Compose with Traefik labels (routing + SSL via labels, not config files)
- Dockerfiles for backend and frontend
- Simple nginx config inside the frontend container (static file serving only — no proxying)
- VPS environment setup
- CI/CD pipeline (GitHub Actions)
- Database backups and health monitoring

---

## How Traefik Integration Works

Traefik discovers services automatically via Docker labels. Instead of editing nginx proxy config or running certbot, you add labels to each service in `docker-compose.yml`. Traefik reads these labels and:

1. Creates a router for the domain you specify
2. Requests a Let's Encrypt cert automatically
3. Routes incoming HTTPS traffic to the right container

Your containers **do not expose ports 80 or 443**. Traefik listens on those ports and forwards internally. The only thing your containers need is to be on the same Docker network as Traefik.

```
Internet
   │
   ▼
Traefik  (port 80 + 443, already running, manages SSL)
   │
   ├──▶  blenko_frontend  (port 80 inside container, serves React static files)
   │
   └──▶  blenko_backend   (port 8000 inside container, FastAPI)
```

---

## Phase Map

| Phase | What | When |
|-------|------|------|
| **Phase A** | Project structure + config files | Day 1 |
| **Phase B** | Dockerfiles (backend + frontend) | Day 1 |
| **Phase C** | Frontend nginx config (static files only) | Day 1 |
| **Phase D** | VPS environment setup | Day 1–2 |
| **Phase E** | First deployment (manual) | Day 2 |
| **Phase F** | CI/CD pipeline (GitHub Actions) | Day 3 |
| **Phase G** | Database backups + health monitoring | Day 3 |
| **Phase H** | Verification + handoff | Day 4 |

---

## Phase A — Project Structure & Config Files

### A1 — Create the root project structure

```
blenko-discovery/
├── frontend/               ← already exists
├── backend/                ← already exists
├── nginx/
│   └── nginx.conf          ← static file serving only (no SSL, no proxy)
├── database/
│   ├── migrations/
│   └── seeds/
├── scripts/
│   ├── backup-db.sh
│   └── health-check.sh
├── .github/
│   └── workflows/
│       └── deploy.yml
├── docker-compose.yml
├── .env.example
├── .env                    ← NOT committed to git
└── .gitignore
```

Create the missing folders:

```bash
mkdir -p nginx database/migrations database/seeds scripts .github/workflows
```

> **Note:** No `nginx/ssl/` folder needed. Traefik owns the certificates.

---

### A2 — Create `.env.example`

```bash
# .env.example

# ─── Database ───────────────────────────────────────────
POSTGRES_DB=blenko_discovery
POSTGRES_USER=blenko_admin
POSTGRES_PASSWORD=CHANGE_THIS_TO_A_SECURE_PASSWORD

# ─── Backend ────────────────────────────────────────────
JWT_SECRET_KEY=CHANGE_THIS_TO_A_LONG_RANDOM_STRING
ENVIRONMENT=production

# ─── Frontend build ─────────────────────────────────────
REACT_APP_API_URL=https://discovery.blenkotechnologies.co.tz/api

# ─── Domain (used in Traefik labels) ────────────────────
DOMAIN=discovery.blenkotechnologies.co.tz

# ─── Traefik ────────────────────────────────────────────
# The name of the cert resolver configured in your Traefik instance.
# Check your Traefik config — common names: letsencrypt, le, myresolver
TRAEFIK_CERT_RESOLVER=letsencrypt

# ─── ERPNext Integration ────────────────────────────────
ERPNEXT_BASE_URL=https://your-erpnext-instance.com
ERPNEXT_API_KEY=CHANGE_THIS
ERPNEXT_API_SECRET=CHANGE_THIS
```

> **Important:** Check your Traefik config for the `certificatesResolvers` name. It's in your Traefik `traefik.yml` or `docker-compose.yml`. Common names are `letsencrypt`, `le`, or `myresolver`. The value you put in `TRAEFIK_CERT_RESOLVER` must match exactly.

---

### A3 — Create `.gitignore`

```gitignore
# .gitignore

# Secrets — NEVER commit
.env
.env.local
.env.production

# Node
node_modules/
frontend/build/

# Python
__pycache__/
*.pyc
.venv/
backend/.venv/

# Database backups
backups/

# Logs
*.log

# IDE
.vscode/
.idea/
```

---

### A4 — Create `docker-compose.yml`

This is the core change from the original plan. Notice:

- **Traefik labels** on `frontend` and `backend` services — this is how routing and SSL are configured
- **No ports 80/443** exposed on frontend — Traefik handles those
- **`traefik_network` external network** — must match the network your Traefik instance is using
- **Backend port 8000 not exposed externally** — Traefik routes to it internally

```yaml
# docker-compose.yml
version: '3.8'

services:

  # ── PostgreSQL ─────────────────────────────────────────
  postgres:
    image: postgres:16-alpine
    container_name: blenko_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-blenko_discovery}
      POSTGRES_USER: ${POSTGRES_USER:-blenko_admin}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    networks:
      - blenko_internal
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-blenko_admin}"]
      interval: 10s
      timeout: 5s
      retries: 5
    # No ports exposed — only accessible by other containers on blenko_internal

  # ── Backend (FastAPI) ──────────────────────────────────
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: blenko_backend
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-blenko_admin}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-blenko_discovery}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      ENVIRONMENT: ${ENVIRONMENT:-production}
      ERPNEXT_BASE_URL: ${ERPNEXT_BASE_URL}
      ERPNEXT_API_KEY: ${ERPNEXT_API_KEY}
      ERPNEXT_API_SECRET: ${ERPNEXT_API_SECRET}
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - blenko_internal
      - traefik_network     # Must be on Traefik's network to receive traffic
    labels:
      - "traefik.enable=true"
      # Router: routes /api/ requests to this container
      - "traefik.http.routers.blenko-api.rule=Host(`${DOMAIN}`) && PathPrefix(`/api`)"
      - "traefik.http.routers.blenko-api.entrypoints=websecure"
      - "traefik.http.routers.blenko-api.tls.certresolver=${TRAEFIK_CERT_RESOLVER}"
      # Service: tell Traefik which port the backend listens on
      - "traefik.http.services.blenko-api.loadbalancer.server.port=8000"
      # Priority: backend router wins over frontend for /api paths
      - "traefik.http.routers.blenko-api.priority=10"
      # OPTIONAL: strip /api prefix before forwarding to FastAPI
      # Uncomment if your FastAPI routes do NOT include /api prefix
      # - "traefik.http.middlewares.blenko-api-strip.stripprefix.prefixes=/api"
      # - "traefik.http.routers.blenko-api.middlewares=blenko-api-strip"

  # ── Frontend (React + nginx static server) ─────────────
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        REACT_APP_API_URL: ${REACT_APP_API_URL:-https://${DOMAIN}/api}
    container_name: blenko_frontend
    restart: unless-stopped
    networks:
      - traefik_network     # Must be on Traefik's network to receive traffic
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    labels:
      - "traefik.enable=true"
      # Router: routes all other requests to the React app
      - "traefik.http.routers.blenko-frontend.rule=Host(`${DOMAIN}`)"
      - "traefik.http.routers.blenko-frontend.entrypoints=websecure"
      - "traefik.http.routers.blenko-frontend.tls.certresolver=${TRAEFIK_CERT_RESOLVER}"
      # Service: tell Traefik which port nginx listens on inside the container
      - "traefik.http.services.blenko-frontend.loadbalancer.server.port=80"
      # Priority: frontend is catch-all, lower priority than backend
      - "traefik.http.routers.blenko-frontend.priority=1"

networks:
  blenko_internal:
    driver: bridge          # Private network for postgres <-> backend only

  traefik_network:
    external: true          # Already exists — created by your Traefik setup
    name: traefik_network   # ← REPLACE with your actual Traefik network name

volumes:
  postgres_data:
    driver: local
```

> **⚠️ Before running:** You must know the exact name of the Docker network your Traefik instance uses. Run `docker network ls` on the VPS to find it. Update the `name:` field under `traefik_network` to match. Common names: `traefik_network`, `traefik`, `traefik_web`, `proxy`.

---

### A4a — API prefix decision (read before proceeding)

The backend label configuration depends on how your FastAPI app is structured. Pick one:

**Option 1 — FastAPI routes include the `/api` prefix**
Your routes look like: `@app.get("/api/sessions/...")`
→ Leave the strip middleware commented out. No changes needed.

**Option 2 — FastAPI routes do NOT include the `/api` prefix**
Your routes look like: `@app.get("/sessions/...")`
→ Uncomment the strip middleware lines so Traefik strips `/api` before forwarding:
```yaml
- "traefik.http.middlewares.blenko-api-strip.stripprefix.prefixes=/api"
- "traefik.http.routers.blenko-api.middlewares=blenko-api-strip"
```

Check your FastAPI `main.py` to determine which applies.

---

## Phase B — Dockerfiles

### B1 — `backend/Dockerfile`

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies (separate layer — only rebuilds if requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Run migrations then start server
CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000

EXPOSE 8000
```

Confirm your `requirements.txt` includes:
```
fastapi
uvicorn[standard]
sqlalchemy
alembic
psycopg2-binary
python-jose[cryptography]
passlib[bcrypt]
python-multipart
httpx
```

---

### B2 — `frontend/Dockerfile`

Two-stage build. Stage 1 compiles the React app with Node. Stage 2 serves it with nginx on port 80. Traefik talks to nginx on port 80 — nginx does not need to handle SSL or API proxying.

```dockerfile
# frontend/Dockerfile

# ── Stage 1: Build React app ─────────────────────────────
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

# API URL baked into the build at compile time
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

COPY . .
RUN npm run build

# ── Stage 2: Serve with nginx ────────────────────────────
FROM nginx:alpine

# Copy built React app
COPY --from=builder /app/build /usr/share/nginx/html

# nginx config is mounted via docker-compose volume (allows updates without rebuild)

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

---

## Phase C — Frontend Nginx Config (Static Files Only)

This nginx config serves React static files. It does **not** handle SSL, certificates, or API proxying — Traefik owns all of that. This is purely an internal static file server.

### C1 — `nginx/nginx.conf`

```nginx
# nginx/nginx.conf
# Purpose: Serve React static files inside the frontend container.
# Traefik sits in front of this and handles SSL, HTTPS redirect, and routing.

events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    server {
        listen 80;

        root  /usr/share/nginx/html;
        index index.html;

        # React Router support: all unknown paths return index.html
        # so client-side routing works correctly
        location / {
            try_files $uri $uri/ /index.html;
        }

        # Health check endpoint (used by health-check.sh script)
        location /health {
            access_log off;
            return 200 "OK\n";
            add_header Content-Type text/plain;
        }

        # Gzip compression
        gzip on;
        gzip_types text/plain text/css application/json application/javascript
                   text/xml application/xml text/javascript;
    }
}
```

---

## Phase D — VPS Environment Setup

### D1 — SSH into the VPS

```bash
ssh root@<YOUR_VPS_IP>
```

---

### D2 — Find Your Traefik Network Name

**This is the most important step. Do this before anything else.**

```bash
# List all Docker networks
docker network ls

# Example output:
# NETWORK ID     NAME               DRIVER    SCOPE
# a1b2c3d4e5f6   traefik_network    bridge    local
# b2c3d4e5f6a1   bridge             bridge    local
# ...

# Confirm Traefik is connected to the network you found
docker inspect traefik | grep -A 5 '"Networks"'
```

Note the exact name. Update `docker-compose.yml`:

```yaml
traefik_network:
  external: true
  name: <YOUR_ACTUAL_TRAEFIK_NETWORK_NAME>
```

---

### D3 — Find Your Traefik Cert Resolver Name

```bash
# Option 1: Check the Traefik config file
cat /path/to/traefik/traefik.yml | grep -A 5 "certificatesResolvers"

# Option 2: Check Traefik's docker-compose.yml
cat /path/to/traefik/docker-compose.yml | grep "certresolver\|certificatesResolvers"
```

You're looking for something like:
```yaml
certificatesResolvers:
  letsencrypt:          ← this name is what goes in TRAEFIK_CERT_RESOLVER
    acme:
      email: admin@blenkotechnologies.co.tz
```

---

### D4 — Check Docker is Installed

```bash
# Docker should already be installed since Traefik is running
docker --version
docker-compose --version

# If not installed:
apt update && apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose -y
```

---

### D5 — Confirm Firewall

```bash
ufw status verbose

# Must show ALLOW for:
# 22/tcp   (SSH)
# 80/tcp   (HTTP — Traefik receives and redirects)
# 443/tcp  (HTTPS — Traefik handles)
```

If any are missing:
```bash
ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp && ufw enable
```

---

### D6 — Clone the Repository

```bash
mkdir -p /opt/blenko-discovery
cd /opt/blenko-discovery
git clone https://github.com/YOUR_ORG/blenko-discovery.git .
```

If using SSH deploy keys for GitHub:
```bash
# Generate deploy key on VPS
ssh-keygen -t ed25519 -C "blenko-vps-deploy" -f ~/.ssh/github_deploy

# Print public key — add this to: GitHub Repo → Settings → Deploy Keys
cat ~/.ssh/github_deploy.pub

# Configure SSH to use it
cat >> ~/.ssh/config << 'EOF'
Host github.com
  IdentityFile ~/.ssh/github_deploy
  StrictHostKeyChecking no
EOF
```

---

### D7 — Create Production `.env`

```bash
cd /opt/blenko-discovery
cp .env.example .env
nano .env
```

Generate secure values on the spot:
```bash
openssl rand -base64 32   # use for POSTGRES_PASSWORD
openssl rand -base64 64   # use for JWT_SECRET_KEY
```

Fill in all values:
```bash
POSTGRES_DB=blenko_discovery
POSTGRES_USER=blenko_admin
POSTGRES_PASSWORD=<generated above>
JWT_SECRET_KEY=<generated above>
ENVIRONMENT=production
REACT_APP_API_URL=https://discovery.blenkotechnologies.co.tz/api
DOMAIN=discovery.blenkotechnologies.co.tz
TRAEFIK_CERT_RESOLVER=<name from D3>
ERPNEXT_BASE_URL=https://your-erpnext-instance.com
ERPNEXT_API_KEY=<from ERPNext>
ERPNEXT_API_SECRET=<from ERPNext>
```

---

## Phase E — First Deployment (Manual)

Bring services up one at a time and verify each before proceeding.

### E1 — Start PostgreSQL

```bash
cd /opt/blenko-discovery

docker-compose up -d postgres

# Wait ~15 seconds, then check status
docker-compose ps
# Expected: blenko_postgres   Up (healthy)

# Confirm connections accepted
docker-compose exec postgres pg_isready -U blenko_admin
# Expected: localhost:5432 - accepting connections
```

---

### E2 — Start Backend (Runs Migrations on Startup)

```bash
docker-compose up -d backend

# Watch logs — confirm migrations run and server starts
docker-compose logs -f backend
```

Look for:
```
INFO  [alembic.runtime.migration] Running upgrade ...
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

If migrations fail, stop here and fix the error before continuing.

---

### E3 — Verify Backend Directly

```bash
# Direct test from within the VPS (bypasses Traefik)
curl http://localhost:8000/health
# Expected: {"status":"ok"} or similar 200 response
```

---

### E4 — Start Frontend

```bash
docker-compose up -d frontend

# Check all three containers
docker-compose ps
```

Expected — note no public ports listed on frontend or backend:
```
NAME                 STATUS           PORTS
blenko_postgres      Up (healthy)
blenko_backend       Up
blenko_frontend      Up
```

---

### E5 — Verify Full Stack Through Traefik

```bash
# HTTPS test
curl -I https://discovery.blenkotechnologies.co.tz
# Expected: HTTP/2 200

# HTTP → HTTPS redirect test
curl -I http://discovery.blenkotechnologies.co.tz
# Expected: 301 or 308 redirect to https://

# API test through Traefik
curl https://discovery.blenkotechnologies.co.tz/api/health
# Expected: 200 response from FastAPI

# SSL cert check
curl -vI https://discovery.blenkotechnologies.co.tz 2>&1 | grep "issuer\|subject"
# Expected: Let's Encrypt issuer
```

Open `https://discovery.blenkotechnologies.co.tz` in a browser. The React app should load with a valid padlock.

---

### E6 — Traefik Troubleshooting

If the site isn't loading, diagnose in this order:

```bash
# 1. Are all containers running?
docker-compose ps

# 2. Are the containers on the Traefik network?
docker network inspect <traefik_network_name> | grep blenko
# blenko_frontend and blenko_backend must appear here

# 3. Did Traefik register the routers?
docker logs traefik 2>&1 | grep blenko
# Look for: blenko-frontend and blenko-api router entries

# 4. Is the cert resolver name correct?
docker logs traefik 2>&1 | grep -i "acme\|certificate\|blenko"

# 5. Is DNS resolving to the VPS?
dig discovery.blenkotechnologies.co.tz
# Must return your VPS IP
```

---

## Phase F — CI/CD Pipeline (GitHub Actions)

### F1 — Create `.github/workflows/deploy.yml`

```yaml
name: Test & Deploy — Blenko Discovery

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:

  # ── Backend Tests ────────────────────────────────────
  test-backend:
    name: Backend Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests
        run: |
          cd backend
          pytest --tb=short

  # ── Frontend Tests + Build ────────────────────────────
  test-frontend:
    name: Frontend Tests + Build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node 18
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run tests
        run: |
          cd frontend
          npm test -- --watchAll=false --passWithNoTests

      - name: Build check
        run: |
          cd frontend
          npm run build

  # ── Deploy (main branch only) ─────────────────────────
  deploy:
    name: Deploy to VPS
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to VPS via SSH
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /opt/blenko-discovery
            git pull origin main
            docker-compose up -d --build
            docker-compose exec -T backend alembic upgrade head
            docker-compose ps
            echo "Deployment complete at $(date)"
```

---

### F2 — Add GitHub Secrets

**GitHub → Repository → Settings → Secrets and variables → Actions → New repository secret**

| Secret Name | Value |
|---|---|
| `VPS_HOST` | VPS IP address |
| `VPS_USER` | SSH username (e.g. `root`) |
| `VPS_SSH_KEY` | Full contents of SSH private key |

```bash
# Get the private key content
cat ~/.ssh/id_rsa
# Copy entire output including -----BEGIN ... ----- and -----END ... -----
```

---

### F3 — Test the Pipeline

```bash
git commit --allow-empty -m "ci: verify pipeline"
git push origin main
```

Go to **GitHub → Actions**. All three jobs should go green.

---

## Phase G — Backups & Health Monitoring

### G1 — Create the Backup Script

```bash
cat > /opt/blenko-discovery/scripts/backup-db.sh << 'EOF'
#!/bin/bash
set -e

BACKUP_DIR="/opt/blenko-discovery/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/blenko_db_$TIMESTAMP.sql.gz"

mkdir -p $BACKUP_DIR

docker-compose -f /opt/blenko-discovery/docker-compose.yml exec -T postgres \
  pg_dump -U blenko_admin blenko_discovery | gzip > $BACKUP_FILE

# Keep only last 7 days
find $BACKUP_DIR -name "blenko_db_*.sql.gz" -mtime +7 -delete

echo "$(date) — Backup: $BACKUP_FILE"
EOF

chmod +x /opt/blenko-discovery/scripts/backup-db.sh
```

Test it immediately:
```bash
/opt/blenko-discovery/scripts/backup-db.sh
ls -lh /opt/blenko-discovery/backups/
```

---

### G2 — Create the Health Check Script

The health check goes through Traefik (external HTTPS URL) — this is the true end-to-end test.

```bash
cat > /opt/blenko-discovery/scripts/health-check.sh << 'EOF'
#!/bin/bash

COMPOSE_FILE="/opt/blenko-discovery/docker-compose.yml"
DOMAIN="discovery.blenkotechnologies.co.tz"
ALERT_EMAIL="admin@blenkotechnologies.co.tz"

# 1. Check all 3 containers are running
RUNNING=$(docker-compose -f $COMPOSE_FILE ps -q | wc -l)
if [ "$RUNNING" -lt 3 ]; then
  echo "$(date) ERROR: Only $RUNNING/3 containers running" | \
    mail -s "Blenko Discovery — Container Alert" $ALERT_EMAIL
  exit 1
fi

# 2. Check backend responds (direct, bypasses Traefik)
BACKEND=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$BACKEND" != "200" ]; then
  echo "$(date) ERROR: Backend health HTTP $BACKEND" | \
    mail -s "Blenko Discovery — Backend Alert" $ALERT_EMAIL
  exit 1
fi

# 3. Check site through Traefik (true end-to-end)
FRONTEND=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/health)
if [ "$FRONTEND" != "200" ]; then
  echo "$(date) ERROR: Frontend/Traefik health HTTP $FRONTEND" | \
    mail -s "Blenko Discovery — Frontend Alert" $ALERT_EMAIL
  exit 1
fi

# 4. Check database
docker-compose -f $COMPOSE_FILE exec -T postgres pg_isready -U blenko_admin > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "$(date) ERROR: Database not ready" | \
    mail -s "Blenko Discovery — Database Alert" $ALERT_EMAIL
  exit 1
fi

echo "$(date) — All services healthy"
EOF

chmod +x /opt/blenko-discovery/scripts/health-check.sh
```

---

### G3 — Schedule Cron Jobs

```bash
crontab -e

# Add:

# Daily database backup at 2:00 AM
0 2 * * * /opt/blenko-discovery/scripts/backup-db.sh >> /var/log/blenko-backup.log 2>&1

# Health check every 5 minutes
*/5 * * * * /opt/blenko-discovery/scripts/health-check.sh >> /var/log/blenko-health.log 2>&1
```

> **Note:** No SSL renewal cron needed. Traefik handles Let's Encrypt renewal automatically.

---

### G4 — Test Backup Restore

```bash
# Create test database
docker-compose exec postgres createdb -U blenko_admin blenko_test_restore

# Restore
gunzip -c /opt/blenko-discovery/backups/blenko_db_<TIMESTAMP>.sql.gz | \
  docker-compose exec -T postgres psql -U blenko_admin blenko_test_restore

# Verify tables exist
docker-compose exec postgres psql -U blenko_admin blenko_test_restore -c "\dt"

# Clean up
docker-compose exec postgres dropdb -U blenko_admin blenko_test_restore
```

---

## Phase H — Final Verification Checklist

### Infrastructure
- [ ] `docker network ls` shows Traefik network — name matches `docker-compose.yml`
- [ ] `docker-compose up -d` starts all three containers without errors
- [ ] `docker-compose ps` shows all three as `Up` or `Up (healthy)`
- [ ] No public ports shown on frontend or backend (`docker-compose ps`)
- [ ] `curl http://localhost:8000/health` returns 200 (backend direct)
- [ ] `curl -I http://discovery.blenkotechnologies.co.tz` returns 301/308 redirect to HTTPS
- [ ] `curl -I https://discovery.blenkotechnologies.co.tz` returns 200
- [ ] `curl https://discovery.blenkotechnologies.co.tz/api/health` returns 200
- [ ] Browser loads the React app with a valid SSL padlock

### Traefik Integration
- [ ] `docker logs traefik` shows `blenko-frontend` and `blenko-api` routers registered
- [ ] Both containers appear in the Traefik network: `docker network inspect <name> | grep blenko`
- [ ] SSL cert issued by Let's Encrypt — check padlock details in browser

### CI/CD
- [ ] Push to `main` triggers all three GitHub Actions jobs
- [ ] Tests run before deployment
- [ ] Deploy job runs only on `main` push, not on PRs

### Database
- [ ] All 12 schema entities present: `docker-compose exec postgres psql -U blenko_admin blenko_discovery -c "\dt"`
- [ ] Backup script creates `.sql.gz` file
- [ ] Restore test succeeds

### Security
- [ ] `.env` is NOT in git (`git status` confirms untracked)
- [ ] PostgreSQL not exposed publicly — only on `blenko_internal` network
- [ ] GitHub secrets are set (VPS_HOST, VPS_USER, VPS_SSH_KEY)

### Monitoring
- [ ] `health-check.sh` runs manually with no errors
- [ ] Cron jobs scheduled (`crontab -l` shows backup + health)
- [ ] Log files exist: `/var/log/blenko-backup.log`, `/var/log/blenko-health.log`

---

## Quick Reference: Day-to-Day Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f
docker-compose logs -f backend

# Restart a service
docker-compose restart frontend

# Rebuild and restart after code change
docker-compose up -d --build backend

# Run migrations manually
docker-compose exec backend alembic upgrade head

# Open a database shell
docker-compose exec postgres psql -U blenko_admin blenko_discovery

# Manual backup
/opt/blenko-discovery/scripts/backup-db.sh

# Manual health check
/opt/blenko-discovery/scripts/health-check.sh

# Pull latest and redeploy (same as CI/CD)
cd /opt/blenko-discovery && git pull && docker-compose up -d --build
```

---

## What Changed From Standard Nginx Plan

| Item | Without Traefik | With Traefik |
|---|---|---|
| SSL certificates | certbot + cron renewal | Traefik automatic via labels |
| HTTP → HTTPS redirect | nginx `return 301` | Traefik entrypoint (already configured) |
| API proxy | nginx `proxy_pass` | Traefik `PathPrefix` label on backend |
| Port exposure | Frontend exposes 80 + 443 | No public ports — Traefik routes internally |
| nginx role | Reverse proxy + static server | Static file server only (port 80 inside container) |
| SSL renewal cron | Required | Not required |
| Adding a new domain | Regenerate cert + reload nginx | Add labels, redeploy — done |

---

*Blenko Discovery System — DevOps Deployment Plan — Sprint 1 — v1.0.1 (Traefik Edition)*
