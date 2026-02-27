"""
Integration tests for scoring API endpoints.
"""
import pytest


class TestSignalScoreEndpoint:
    def test_update_signal_success(self, client, auth_headers, test_interaction):
        response = client.post(
            f"/api/scoring/{test_interaction.interaction_id}/signal",
            json={
                "dimension": "competitive_awareness",
                "signal_name": "competitor_awareness",
                "score": 2,
                "notes": "Clearly named two direct competitors and their recent wins",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"
        assert data["score_given"] == 2
        assert "dimension_result" in data

    def test_invalid_score_rejected(self, client, auth_headers, test_interaction):
        response = client.post(
            f"/api/scoring/{test_interaction.interaction_id}/signal",
            json={
                "dimension": "competitive_awareness",
                "signal_name": "competitor_awareness",
                "score": 5,
            },
            headers=auth_headers,
        )
        assert response.status_code == 422  # Pydantic validation

    def test_multiple_signals_aggregate_correctly(self, client, auth_headers, test_interaction):
        session_id = str(test_interaction.interaction_id)
        signals = [
            ("competitor_awareness", 2),
            ("brand_perception_sensitivity", 2),
            ("loss_attribution", 1),
        ]
        for signal_name, score in signals:
            client.post(
                f"/api/scoring/{session_id}/signal",
                json={"dimension": "competitive_awareness", "signal_name": signal_name, "score": score},
                headers=auth_headers,
            )

        response = client.get(
            f"/api/scoring/{session_id}/dimension/competitive_awareness",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["achieved_score"] == 5
        assert data["tier"] == "emerging"
        assert data["tier_label"] == "Emerging Awareness"


class TestDimensionScoreEndpoint:
    def test_get_unstarted_dimension(self, client, auth_headers, test_interaction):
        response = client.get(
            f"/api/scoring/{test_interaction.interaction_id}/dimension/brand_gap",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["achieved_score"] == 0
        assert data["tier"] is None


class TestOverallScoreEndpoint:
    def test_overall_score_starts_at_zero(self, client, auth_headers, test_interaction):
        response = client.get(
            f"/api/scoring/{test_interaction.interaction_id}/overall",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["overall_score"] == 0.0
        assert data["qualification_grade"] == "unqualified"

    def test_overall_score_updates_after_signals(self, client, auth_headers, test_interaction):
        session_id = str(test_interaction.interaction_id)
        # Score all D1 signals at max
        for signal in [
            "competitor_awareness", "brand_perception_sensitivity",
            "loss_attribution", "is_competitive_awareness", "emotional_engagement"
        ]:
            client.post(
                f"/api/scoring/{session_id}/signal",
                json={"dimension": "competitive_awareness", "signal_name": signal, "score": 2},
                headers=auth_headers,
            )

        response = client.get(f"/api/scoring/{session_id}/overall", headers=auth_headers)
        data = response.json()
        assert data["overall_score"] == 10.0


class TestTriggerAcknowledge:
    def test_acknowledge_trigger(self, client, auth_headers, test_interaction):
        session_id = str(test_interaction.interaction_id)
        # First score enough to create a dimension score
        client.post(
            f"/api/scoring/{session_id}/signal",
            json={"dimension": "competitive_awareness", "signal_name": "competitor_awareness", "score": 1},
            headers=auth_headers,
        )
        response = client.post(
            f"/api/scoring/{session_id}/trigger/competitive_awareness/acknowledge",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "trigger_acknowledged"
