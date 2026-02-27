"""
Unit tests for the Scoring Engine.
Validates all tier boundaries from design doc Section 4.
"""
import pytest
import uuid

from models.database import Interaction, DimensionScore, SignalScore
from services.scoring_engine import (
    ScoringEngine, calculate_grade, _default_thresholds, _score_to_tier, _tier_label
)


# ─────────────────────────────────────────────────────────────────────────────
# Grade calculation (overall score → grade)
# ─────────────────────────────────────────────────────────────────────────────

class TestCalculateGrade:
    def test_unqualified_lower_bound(self):
        assert calculate_grade(0) == "unqualified"

    def test_unqualified_upper_bound(self):
        assert calculate_grade(12) == "unqualified"

    def test_developing_lower_bound(self):
        assert calculate_grade(13) == "developing"

    def test_developing_upper_bound(self):
        assert calculate_grade(25) == "developing"

    def test_qualified_lower_bound(self):
        assert calculate_grade(26) == "qualified"

    def test_qualified_upper_bound(self):
        assert calculate_grade(40) == "qualified"

    def test_hot_lower_bound(self):
        assert calculate_grade(41) == "hot"

    def test_hot_upper_bound(self):
        assert calculate_grade(50) == "hot"

    def test_perfect_score_is_hot(self):
        assert calculate_grade(50) == "hot"

    def test_zero_is_unqualified(self):
        assert calculate_grade(0) == "unqualified"


# ─────────────────────────────────────────────────────────────────────────────
# Tier thresholds per dimension
# ─────────────────────────────────────────────────────────────────────────────

class TestTierThresholds:
    """Validates tier boundaries from design doc Section 4.1."""

    def test_d1_low_max(self):
        t = _default_thresholds("competitive_awareness")
        assert _score_to_tier(3, t) == "low"

    def test_d1_emerging_min(self):
        t = _default_thresholds("competitive_awareness")
        assert _score_to_tier(4, t) == "emerging"

    def test_d1_emerging_max(self):
        t = _default_thresholds("competitive_awareness")
        assert _score_to_tier(6, t) == "emerging"

    def test_d1_high_min(self):
        t = _default_thresholds("competitive_awareness")
        assert _score_to_tier(7, t) == "high"

    def test_d1_high_max(self):
        t = _default_thresholds("competitive_awareness")
        assert _score_to_tier(10, t) == "high"

    def test_d2_low_max(self):
        t = _default_thresholds("brand_gap")
        assert _score_to_tier(4, t) == "low"

    def test_d2_emerging_min(self):
        t = _default_thresholds("brand_gap")
        assert _score_to_tier(5, t) == "emerging"

    def test_d2_high_min(self):
        t = _default_thresholds("brand_gap")
        assert _score_to_tier(9, t) == "high"

    def test_d3_low_max(self):
        t = _default_thresholds("is_maturity")
        assert _score_to_tier(4, t) == "low"

    def test_d3_emerging_max(self):
        t = _default_thresholds("is_maturity")
        assert _score_to_tier(9, t) == "emerging"

    def test_d3_high_min(self):
        t = _default_thresholds("is_maturity")
        assert _score_to_tier(10, t) == "high"

    def test_d4_low_max(self):
        t = _default_thresholds("cost_of_status_quo")
        assert _score_to_tier(4, t) == "low"

    def test_d4_emerging_max(self):
        t = _default_thresholds("cost_of_status_quo")
        assert _score_to_tier(9, t) == "emerging"

    def test_d4_high_min(self):
        t = _default_thresholds("cost_of_status_quo")
        assert _score_to_tier(10, t) == "high"


# ─────────────────────────────────────────────────────────────────────────────
# Tier labels
# ─────────────────────────────────────────────────────────────────────────────

class TestTierLabels:
    def test_d1_low_label(self):
        assert _tier_label("competitive_awareness", "low") == "Low Awareness"

    def test_d1_emerging_label(self):
        assert _tier_label("competitive_awareness", "emerging") == "Emerging Awareness"

    def test_d1_high_label(self):
        assert _tier_label("competitive_awareness", "high") == "High Awareness"

    def test_d2_low_label(self):
        assert _tier_label("brand_gap", "low") == "No Perceived Gap"

    def test_d3_high_label(self):
        assert _tier_label("is_maturity", "high") == "Active IS Pain / Readiness"

    def test_d4_high_label(self):
        assert _tier_label("cost_of_status_quo", "high") == "Genuine Urgency Established"


# ─────────────────────────────────────────────────────────────────────────────
# ScoringEngine integration tests (require DB)
# ─────────────────────────────────────────────────────────────────────────────

class TestScoringEngineIntegration:
    def test_update_signal_creates_records(self, db, test_interaction):
        engine = ScoringEngine(db)
        result = engine.update_signal_score(
            str(test_interaction.interaction_id),
            "competitive_awareness",
            "competitor_awareness",
            2,
        )
        assert result["achieved_score"] == 2
        assert result["dimension"] == "competitive_awareness"

    def test_update_signal_recalculates_total(self, db, test_interaction):
        engine = ScoringEngine(db)
        engine.update_signal_score(
            str(test_interaction.interaction_id),
            "competitive_awareness", "competitor_awareness", 2,
        )
        engine.update_signal_score(
            str(test_interaction.interaction_id),
            "competitive_awareness", "brand_perception_sensitivity", 2,
        )
        result = engine.update_signal_score(
            str(test_interaction.interaction_id),
            "competitive_awareness", "loss_attribution", 1,
        )
        assert result["achieved_score"] == 5
        assert result["tier"] == "emerging"

    def test_score_update_is_idempotent(self, db, test_interaction):
        """Updating the same signal twice uses the latest score."""
        engine = ScoringEngine(db)
        engine.update_signal_score(
            str(test_interaction.interaction_id),
            "competitive_awareness", "competitor_awareness", 1,
        )
        result = engine.update_signal_score(
            str(test_interaction.interaction_id),
            "competitive_awareness", "competitor_awareness", 2,
        )
        assert result["achieved_score"] == 2

    def test_score_history_preserved(self, db, test_interaction):
        """Audit trail: previous score is saved before overwrite."""
        engine = ScoringEngine(db)
        engine.update_signal_score(
            str(test_interaction.interaction_id),
            "competitive_awareness", "competitor_awareness", 1,
        )
        engine.update_signal_score(
            str(test_interaction.interaction_id),
            "competitive_awareness", "competitor_awareness", 2,
        )
        signal = db.query(SignalScore).filter(
            SignalScore.signal_name == "competitor_awareness"
        ).first()
        assert signal.score_given == 2
        assert len(signal.score_history) >= 1
        assert signal.score_history[0]["score"] == 1

    def test_invalid_score_raises_error(self, db, test_interaction):
        engine = ScoringEngine(db)
        with pytest.raises(ValueError, match="0, 1, or 2"):
            engine.update_signal_score(
                str(test_interaction.interaction_id),
                "competitive_awareness", "competitor_awareness", 3,
            )

    def test_overall_score_aggregates_dimensions(self, db, test_interaction):
        engine = ScoringEngine(db)
        # Score D1 fully (all 5 signals × 2 = 10 points)
        for signal in [
            "competitor_awareness", "brand_perception_sensitivity",
            "loss_attribution", "is_competitive_awareness", "emotional_engagement"
        ]:
            engine.update_signal_score(
                str(test_interaction.interaction_id),
                "competitive_awareness", signal, 2,
            )

        overall = engine.get_overall_score(str(test_interaction.interaction_id))
        assert overall["overall_score"] == 10.0
        assert overall["qualification_grade"] == "unqualified"  # 10 < 13

    def test_hot_grade_requires_41_plus(self, db, test_interaction):
        engine = ScoringEngine(db)
        # Max out D1 (10) + D3 (14) + D4 (14) = 38 → qualified
        # Add D2 signals to push over 41
        dimensions_and_signals = {
            "competitive_awareness": [
                "competitor_awareness", "brand_perception_sensitivity",
                "loss_attribution", "is_competitive_awareness", "emotional_engagement"
            ],
            "brand_gap": [
                "self_awareness_of_brand_gap", "physical_presentation_concern",
                "digital_presence_dissatisfaction", "cross_touchpoint_consistency",
                "customer_feedback_awareness", "emotional_response_to_gap"
            ],
            "is_maturity": [
                "operational_friction", "business_management_maturity",
                "web_and_digital_health", "network_and_security_confidence",
                "scalability_concern", "support_and_reliability_pain", "openness_to_is_investment"
            ],
            "cost_of_status_quo": [
                "revenue_impact_awareness", "productivity_cost_awareness",
                "competitive_erosion_concern", "trust_and_reputation_risk",
                "opportunity_cost_of_delay", "quantification_willingness", "urgency_expression"
            ],
        }

        for dimension, signals in dimensions_and_signals.items():
            for signal in signals:
                engine.update_signal_score(
                    str(test_interaction.interaction_id), dimension, signal, 2
                )

        overall = engine.get_overall_score(str(test_interaction.interaction_id))
        assert overall["overall_score"] == 50.0
        assert overall["qualification_grade"] == "hot"

    def test_get_dimension_score_returns_empty_for_unstarted(self, db, test_interaction):
        engine = ScoringEngine(db)
        result = engine.get_dimension_score(
            str(test_interaction.interaction_id), "brand_gap"
        )
        assert result["achieved_score"] == 0
        assert result["tier"] is None


# ─────────────────────────────────────────────────────────────────────────────
# Score validation
# ─────────────────────────────────────────────────────────────────────────────

class TestScoreValidation:
    @pytest.mark.parametrize("score", [0, 1, 2])
    def test_valid_scores_accepted(self, db, test_interaction, score):
        engine = ScoringEngine(db)
        result = engine.update_signal_score(
            str(test_interaction.interaction_id),
            "competitive_awareness", "competitor_awareness", score,
        )
        assert result["achieved_score"] == score

    @pytest.mark.parametrize("score", [-1, 3, 10, 100])
    def test_invalid_scores_rejected(self, db, test_interaction, score):
        engine = ScoringEngine(db)
        with pytest.raises(ValueError):
            engine.update_signal_score(
                str(test_interaction.interaction_id),
                "competitive_awareness", "competitor_awareness", score,
            )
