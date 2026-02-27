"""
Integration tests for session API endpoints.
"""
import pytest


SESSION_PAYLOAD = {
    "prospect": {
        "company_name": "Acme Workwear Pty Ltd",
        "contact_name": "David Chen",
        "contact_role": "Managing Director",
        "contact_email": "david@acmeworkwear.com",
        "contact_phone": "0412 345 678",
        "business_type": "trade",
        "size_tier": "small",
        "growth_stage": "active_growth",
        "geographic_scope": "regional",
        "vendor_status": "ad_hoc",
        "growth_ambition": "high",
    },
    "business_profile": {
        "trigger_event": "Won a large contract and need consistent branded workwear",
        "trigger_category": "new_contract",
        "primary_trigger_dimension": "brand_gap",
        "competitive_context": "Up against two larger regional competitors",
        "strategic_priorities": "Grow to multi-site in 2 years",
    },
}


class TestCreateSession:
    def test_create_session_success(self, client, auth_headers):
        response = client.post(
            "/api/sessions/create",
            json=SESSION_PAYLOAD,
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        assert "prospect_id" in data
        assert data["status"] == "in_progress"
        assert data["overall_score"] == 0.0

    def test_create_session_requires_auth(self, client):
        response = client.post("/api/sessions/create", json=SESSION_PAYLOAD)
        assert response.status_code == 401

    def test_create_session_missing_required_fields(self, client, auth_headers):
        bad_payload = {
            "prospect": {"company_name": "Missing Fields Co"},
            "business_profile": {},
        }
        response = client.post(
            "/api/sessions/create",
            json=bad_payload,
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestGetSession:
    def test_get_session_success(self, client, auth_headers, test_interaction):
        response = client.get(
            f"/api/sessions/{test_interaction.interaction_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert str(data["session_id"]) == str(test_interaction.interaction_id)
        assert "prospect" in data
        assert "dimension_scores" in data

    def test_get_nonexistent_session_returns_404(self, client, auth_headers):
        response = client.get(
            "/api/sessions/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestAutosave:
    def test_autosave_updates_session(self, client, auth_headers, test_interaction):
        response = client.patch(
            f"/api/sessions/{test_interaction.interaction_id}/autosave",
            json={
                "field": "key_pain_notes",
                "value": "Prospect mentioned losing 2 contracts last year due to presentation",
                "context": None,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "saved"

    def test_autosave_returns_timestamp(self, client, auth_headers, test_interaction):
        response = client.patch(
            f"/api/sessions/{test_interaction.interaction_id}/autosave",
            json={"field": "key_pain_notes", "value": "test"},
            headers=auth_headers,
        )
        data = response.json()
        assert "timestamp" in data


class TestCompleteSession:
    def test_complete_session(self, client, auth_headers, test_interaction):
        response = client.patch(
            f"/api/sessions/{test_interaction.interaction_id}/complete",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "complete"
        assert "qualification_grade" in data


class TestListSessions:
    def test_list_sessions_returns_own_sessions(self, client, auth_headers, test_interaction):
        response = client.get("/api/sessions/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "total" in data
        assert data["total"] >= 1


class TestPainFlags:
    def test_create_pain_flag(self, client, auth_headers, test_interaction):
        payload = {
            "dimension": "competitive_awareness",
            "pain_category": "competitive_pressure",
            "pain_intensity": "high",
            "pain_description": "Lost three tenders in past 6 months to better-presented competitor",
            "prospect_quoted": "They just look more professional than us on paper",
        }
        response = client.post(
            f"/api/sessions/{test_interaction.interaction_id}/pain-flags",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["pain_intensity"] == "high"
        assert data["status"] == "unaddressed"

    def test_list_pain_flags(self, client, auth_headers, test_interaction):
        response = client.get(
            f"/api/sessions/{test_interaction.interaction_id}/pain-flags",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
