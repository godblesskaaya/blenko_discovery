"""
Blenko Discovery System — API Integration Tests

Tests the full HTTP layer for session and scoring endpoints.
Uses httpx TestClient with an in-memory SQLite database for speed.

Run with: pytest tests/test_api_integration.py -v
"""
import uuid
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app
from models.database import User
from services.auth_service import hash_password, create_access_token


# ---------------------------------------------------------------------------
# Test database setup (SQLite in-memory for speed)
# ---------------------------------------------------------------------------

SQLALCHEMY_TEST_URL = "sqlite:///./test_blenko.db"

test_engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Create all tables before tests, drop after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="module")
def test_user():
    """Create and return a test rep user."""
    db = TestingSessionLocal()
    user = User(
        user_id=uuid.uuid4(),
        full_name="Test Rep",
        email="testrep@blenko.test",
        password_hash=hash_password("testpass123"),
        role="rep",
        specialization="general",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture(scope="module")
def auth_headers(test_user):
    """Return Authorization headers for the test user."""
    token = create_access_token(test_user.user_id, test_user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def created_session(auth_headers):
    """Create and return a live session for use in tests."""
    payload = {
        "prospect": {
            "company_name": "Acme Uniforms Ltd",
            "contact_name": "Sarah Chen",
            "contact_role": "Operations Manager",
            "contact_email": "sarah@acmeuniforms.test",
            "contact_phone": "0800 000 001",
            "industry": "Workwear",
            "business_type": "manufacturing",
            "size_tier": "small",
            "growth_stage": "active_growth",
            "geographic_scope": "regional",
            "vendor_status": "unhappy",
            "growth_ambition": "high",
        },
        "business_profile": {
            "trigger_event": "Lost a major contract renewal",
            "trigger_category": "vendor_dissatisfaction",
            "primary_trigger_dimension": "competitive_awareness",
            "competitive_context": "Three competitors in the regional market",
        },
    }
    response = client.post("/api/sessions/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    return response.json()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

class TestHealth:
    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

class TestAuth:
    def test_login_valid_credentials(self, test_user):
        response = client.post("/api/auth/login", json={
            "email": "testrep@blenko.test",
            "password": "testpass123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "testrep@blenko.test"

    def test_login_invalid_password(self):
        response = client.post("/api/auth/login", json={
            "email": "testrep@blenko.test",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_login_unknown_email(self):
        response = client.post("/api/auth/login", json={
            "email": "nobody@blenko.test",
            "password": "testpass123",
        })
        assert response.status_code == 401

    def test_me_returns_user(self, auth_headers):
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["email"] == "testrep@blenko.test"

    def test_protected_endpoint_requires_token(self):
        response = client.get("/api/sessions/")
        assert response.status_code == 401

    def test_refresh_token(self):
        login = client.post("/api/auth/login", json={
            "email": "testrep@blenko.test",
            "password": "testpass123",
        })
        refresh_token = login.json()["refresh_token"]
        response = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == 200
        assert "access_token" in response.json()


# ---------------------------------------------------------------------------
# Session creation (Layer Zero)
# ---------------------------------------------------------------------------

class TestSessionCreation:
    def test_create_session_returns_201(self, auth_headers):
        payload = {
            "prospect": {
                "company_name": "Test Company",
                "contact_name": "John Smith",
                "business_type": "service",
                "size_tier": "micro",
                "growth_stage": "early_growth",
                "geographic_scope": "local",
                "vendor_status": "none",
                "growth_ambition": "high",
            },
            "business_profile": {
                "trigger_event": "Just started the business",
                "trigger_category": "growth_pressure",
            },
        }
        response = client.post("/api/sessions/", json=payload, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        assert "prospect_id" in data
        assert data["status"] == "in_progress"

    def test_create_session_requires_company_name(self, auth_headers):
        payload = {
            "prospect": {
                "contact_name": "John Smith",
                "business_type": "service",
                "size_tier": "micro",
                "growth_stage": "early_growth",
                "geographic_scope": "local",
                "vendor_status": "none",
                "growth_ambition": "high",
            },
            "business_profile": {},
        }
        response = client.post("/api/sessions/", json=payload, headers=auth_headers)
        assert response.status_code == 422  # Pydantic validation error

    def test_created_session_retrievable(self, auth_headers, created_session):
        session_id = created_session["session_id"]
        response = client.get(f"/api/sessions/{session_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["prospect"]["company_name"] == "Acme Uniforms Ltd"

    def test_created_session_has_business_profile(self, auth_headers, created_session):
        session_id = created_session["session_id"]
        response = client.get(f"/api/sessions/{session_id}", headers=auth_headers)
        data = response.json()
        assert data["business_profile"] is not None
        assert data["business_profile"]["trigger_category"] == "vendor_dissatisfaction"


# ---------------------------------------------------------------------------
# Auto-save
# ---------------------------------------------------------------------------

class TestAutoSave:
    def test_autosave_returns_saved(self, auth_headers, created_session):
        session_id = created_session["session_id"]
        response = client.patch(
            f"/api/sessions/{session_id}/autosave",
            json={"key_pain_notes": "Prospect mentioned losing 2 tenders this year"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "saved"

    def test_autosave_nonexistent_session_returns_404(self, auth_headers):
        response = client.patch(
            f"/api/sessions/{uuid.uuid4()}/autosave",
            json={"key_pain_notes": "test"},
            headers=auth_headers,
        )
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Signal scoring
# ---------------------------------------------------------------------------

class TestSignalScoring:
    def test_update_signal_returns_dimension_total(self, auth_headers, created_session):
        session_id = created_session["session_id"]
        payload = {
            "interaction_id": session_id,
            "dimension": "competitive_awareness",
            "signal_name": "S1_competitor_awareness",
            "score": 2,
        }
        response = client.post("/api/scoring/signal", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["signal_name"] == "S1_competitor_awareness"
        assert data["score"] == 2
        assert "dimension_total" in data
        assert data["dimension_total"]["achieved_score"] >= 2

    def test_update_signal_invalid_score_returns_422(self, auth_headers, created_session):
        session_id = created_session["session_id"]
        payload = {
            "interaction_id": session_id,
            "dimension": "competitive_awareness",
            "signal_name": "S1_competitor_awareness",
            "score": 3,  # Invalid — must be 0, 1, or 2
        }
        response = client.post("/api/scoring/signal", json=payload, headers=auth_headers)
        assert response.status_code == 422

    def test_score_zero_valid(self, auth_headers, created_session):
        session_id = created_session["session_id"]
        payload = {
            "interaction_id": session_id,
            "dimension": "competitive_awareness",
            "signal_name": "S1_competitor_awareness",
            "score": 0,
        }
        response = client.post("/api/scoring/signal", json=payload, headers=auth_headers)
        assert response.status_code == 200

    def test_multiple_signals_accumulate(self, auth_headers, created_session):
        session_id = created_session["session_id"]

        signals = [
            ("S1_competitor_awareness", 2),
            ("S2_brand_perception_sensitivity", 2),
            ("S3_loss_attribution", 1),
        ]

        for signal_name, score in signals:
            client.post("/api/scoring/signal", json={
                "interaction_id": session_id,
                "dimension": "competitive_awareness",
                "signal_name": signal_name,
                "score": score,
            }, headers=auth_headers)

        # Check accumulated score
        response = client.get(
            f"/api/scoring/dimension/{session_id}/competitive_awareness",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["achieved_score"]) == 5.0

    def test_retroactive_update_recalculates(self, auth_headers, created_session):
        """Update a previously set signal — total should recalculate."""
        session_id = created_session["session_id"]

        # Set signal to 2
        client.post("/api/scoring/signal", json={
            "interaction_id": session_id,
            "dimension": "competitive_awareness",
            "signal_name": "S4_is_competitive_awareness",
            "score": 2,
        }, headers=auth_headers)

        # Revise to 0
        client.post("/api/scoring/signal", json={
            "interaction_id": session_id,
            "dimension": "competitive_awareness",
            "signal_name": "S4_is_competitive_awareness",
            "score": 0,
        }, headers=auth_headers)

        # Should reflect the revision
        response = client.get(
            f"/api/scoring/dimension/{session_id}/competitive_awareness",
            headers=auth_headers,
        )
        signals = response.json()["signals"]
        s4 = next(s for s in signals if s["signal_name"] == "S4_is_competitive_awareness")
        assert s4["score"] == 0


# ---------------------------------------------------------------------------
# Tier trigger tests
# ---------------------------------------------------------------------------

class TestTierTriggers:
    def test_high_tier_d1_generates_trigger(self, auth_headers, created_session):
        """Score D1 to high tier (7+) and verify trigger text is returned."""
        session_id = created_session["session_id"]

        # Score all 5 D1 signals to 2 (total = 10, tier = high)
        signals = [
            "S1_competitor_awareness",
            "S2_brand_perception_sensitivity",
            "S3_loss_attribution",
            "S4_is_competitive_awareness",
            "S5_emotional_engagement",
        ]
        for sig in signals:
            client.post("/api/scoring/signal", json={
                "interaction_id": session_id,
                "dimension": "competitive_awareness",
                "signal_name": sig,
                "score": 2,
            }, headers=auth_headers)

        response = client.get(
            f"/api/scoring/dimension/{session_id}/competitive_awareness",
            headers=auth_headers,
        )
        data = response.json()
        assert data["score_tier"] == "high"
        assert data["system_trigger"] is not None
        assert len(data["system_trigger"]) > 0
        assert "cross-sell" in data["system_trigger"]


# ---------------------------------------------------------------------------
# Overall score
# ---------------------------------------------------------------------------

class TestOverallScore:
    def test_overall_score_returns_grade(self, auth_headers, created_session):
        session_id = created_session["session_id"]
        response = client.get(f"/api/scoring/overall/{session_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "overall_score" in data
        assert "qualification_grade" in data
        assert data["qualification_grade"] in ("unqualified", "developing", "qualified", "hot")

    def test_overall_score_increases_with_signals(self, auth_headers, created_session):
        session_id = created_session["session_id"]

        before = client.get(f"/api/scoring/overall/{session_id}", headers=auth_headers).json()

        # Add D2 signals
        client.post("/api/scoring/signal", json={
            "interaction_id": session_id,
            "dimension": "brand_gap",
            "signal_name": "S1_self_awareness_of_brand_gap",
            "score": 2,
        }, headers=auth_headers)

        after = client.get(f"/api/scoring/overall/{session_id}", headers=auth_headers).json()

        assert float(after["overall_score"]) >= float(before["overall_score"])


# ---------------------------------------------------------------------------
# Session completion
# ---------------------------------------------------------------------------

class TestSessionCompletion:
    def test_complete_session(self, auth_headers, created_session):
        session_id = created_session["session_id"]
        response = client.post(f"/api/sessions/{session_id}/complete", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "complete"
        assert "qualification_grade" in data
