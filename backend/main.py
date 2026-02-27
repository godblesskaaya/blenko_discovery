"""
Blenko Discovery System — FastAPI Application
Sprint 1: Core Discovery Flow & Scoring Engine
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import engine, Base
from routes import auth, sessions, scoring


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables only for local SQLite dev.
    # PostgreSQL environments should use Alembic migrations.
    if settings.APP_ENV == "development" and settings.DATABASE_URL.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Blenko Discovery API",
    version="1.0.0",
    description="Sales discovery intelligence system for Blenko Stitches",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(scoring.router, prefix="/api/scoring", tags=["Scoring"])


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0", "system": "Blenko Discovery"}


@app.get("/")
def root():
    return {
        "message": "Blenko Discovery API v1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
