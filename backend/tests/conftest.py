"""
Pytest configuration and shared fixtures.
Uses an in-memory SQLite database for speed — no PostgreSQL required for unit tests.
"""
import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from database import Base, get_db
from main import app
from models.database import User, Prospect, Interaction
from services.auth_service import get_password_hash, create_access_token

# Use SQLite for tests (no Postgres required)
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Test client with DB override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """A rep user for testing."""
    user = User(
        user_id=uuid.uuid4(),
        full_name="Test Rep",
        email="rep@blenko.test",
        password_hash=get_password_hash("testpass123"),
        role="rep",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """JWT auth headers for test user."""
    token = create_access_token({"sub": str(test_user.user_id), "role": test_user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_prospect(db, test_user):
    """A prospect record."""
    prospect = Prospect(
        company_name="Test Co Pty Ltd",
        contact_name="Jane Smith",
        contact_role="Owner",
        contact_email="jane@testco.com",
        business_type="service",
        size_tier="small",
        growth_stage="active_growth",
        geographic_scope="local",
        vendor_status="ad_hoc",
        growth_ambition="high",
        created_by=test_user.user_id,
    )
    db.add(prospect)
    db.commit()
    db.refresh(prospect)
    return prospect


@pytest.fixture
def test_interaction(db, test_prospect, test_user):
    """An in-progress discovery interaction."""
    interaction = Interaction(
        prospect_id=test_prospect.prospect_id,
        interaction_type="discovery",
        conducted_by=test_user.user_id,
        session_status="in_progress",
        overall_score=0,
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction
