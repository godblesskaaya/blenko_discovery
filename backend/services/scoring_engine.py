"""
Blenko Discovery Scoring Engine.

Handles:
- Signal score updates with append-only audit trail
- Real-time dimension score recalculation (target: <100ms)
- Tier calculation against framework thresholds
- System trigger generation (from database, not hardcoded)
- Overall score and qualification grade calculation
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from models.database import (
    DimensionScore, SignalScore, Interaction,
    FrameworkDimension, FrameworkTrigger,
)


# Overall grade thresholds (design doc Section 4.2)
GRADE_THRESHOLDS = {
    "unqualified": (0, 12),
    "developing": (13, 25),
    "qualified": (26, 40),
    "hot": (41, 50),
}

ERP_STAGE_MAP = {
    "unqualified": "Lead - Awareness",
    "developing": "Opportunity - Qualification",
    "qualified": "Opportunity - Needs Analysis",
    "hot": "Opportunity - Proposal",
}

# Max scores per dimension (design doc Section 4.1)
DIMENSION_MAX_SCORES = {
    "competitive_awareness": 10,
    "brand_gap": 12,
    "is_maturity": 14,
    "cost_of_status_quo": 14,
    "solution_routing": 0,  # Not scored
}

DEFAULT_TRIGGERS = {
    "competitive_awareness": {
        "low": (
            "Deploy Reframes 1 & 2. Do not advance to deep qualification. "
            "Flag for longer sales cycle. Awareness-building is the priority."
        ),
        "emerging": (
            "Probe C and D are high priority if not yet used. "
            "Transition to D2 - brand gap will deepen urgency."
        ),
        "high": (
            "Strong foundation. Move efficiently. Flag cross-sell opportunity. "
            "Prospect is open to both branding and IS interventions."
        ),
    },
}


def calculate_grade(total_score: float) -> str:
    for grade, (low, high) in GRADE_THRESHOLDS.items():
        if low <= total_score <= high:
            return grade
    return "unqualified"


class ScoringEngine:
    def __init__(self, db: Session):
        self.db = db

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC: Update a single signal score
    # ─────────────────────────────────────────────────────────────────────────

    def update_signal_score(
        self,
        interaction_id: str,
        dimension: str,
        signal_name: str,
        score: int,
        notes: Optional[str] = None,
    ) -> dict:
        """
        Update one signal score and immediately recalculate dimension total.
        Returns updated dimension score data for immediate frontend consumption.
        Maintains append-only audit trail via score_history JSONB field.
        """
        # Validate score value
        if score not in [0, 1, 2]:
            raise ValueError("Signal score must be 0, 1, or 2")

        interaction_uuid = self._normalize_uuid(interaction_id)

        # Get or create DimensionScore record
        dim_score = self._get_or_create_dimension_score(interaction_uuid, dimension)

        # Get or create SignalScore record
        signal, signal_created = self._get_or_create_signal_score(dim_score, interaction_uuid, signal_name)

        # Append previous score to audit history before overwriting
        history = signal.score_history or []
        if not signal_created and signal.score_given is not None:
            history.append({
                "score": signal.score_given,
                "notes": signal.signal_notes,
                "changed_at": datetime.utcnow().isoformat(),
            })
        signal.score_history = history
        signal.score_given = score
        signal.signal_notes = notes
        signal.scored_at = datetime.utcnow()

        self.db.flush()

        # Recalculate dimension totals
        updated = self._recalculate_dimension(dim_score, interaction_uuid, dimension)

        # Update the overall interaction score
        self._recalculate_overall_score(interaction_uuid)

        self.db.commit()
        return updated

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC: Get dimension score snapshot
    # ─────────────────────────────────────────────────────────────────────────

    def get_dimension_score(self, interaction_id: str, dimension: str) -> dict:
        interaction_uuid = self._normalize_uuid(interaction_id)
        dim_score = self.db.query(DimensionScore).filter(
            DimensionScore.interaction_id == interaction_uuid,
            DimensionScore.dimension == dimension,
        ).first()

        if not dim_score:
            return {
                "dimension": dimension,
                "achieved_score": 0,
                "max_score": DIMENSION_MAX_SCORES.get(dimension, 0),
                "score_percentage": 0,
                "tier": None,
                "tier_label": None,
                "system_trigger": None,
                "trigger_deployed": False,
                "signals": [],
            }

        signals = self.db.query(SignalScore).filter(
            SignalScore.dimension_score_id == dim_score.dimension_score_id
        ).all()

        return {
            "dimension": dimension,
            "achieved_score": float(dim_score.achieved_score or 0),
            "max_score": dim_score.max_score,
            "score_percentage": float(dim_score.score_percentage or 0),
            "tier": dim_score.score_tier,
            "tier_label": dim_score.tier_label,
            "system_trigger": dim_score.system_trigger,
            "trigger_deployed": dim_score.trigger_deployed,
            "signals": [
                {
                    "signal_name": s.signal_name,
                    "score": s.score_given or 0,
                    "max_score": s.max_signal_score,
                    "notes": s.signal_notes,
                }
                for s in signals
            ],
        }

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC: Get overall score for a session
    # ─────────────────────────────────────────────────────────────────────────

    def get_overall_score(self, interaction_id: str) -> dict:
        interaction_uuid = self._normalize_uuid(interaction_id)
        interaction = self.db.query(Interaction).filter(
            Interaction.interaction_id == interaction_uuid
        ).first()

        if not interaction:
            raise ValueError(f"Interaction {interaction_id} not found")

        total = float(interaction.overall_score or 0)
        grade = calculate_grade(total)

        dim_scores = self.db.query(DimensionScore).filter(
            DimensionScore.interaction_id == interaction_uuid
        ).all()

        return {
            "overall_score": total,
            "max_possible_score": 50,
            "score_percentage": round((total / 50) * 100, 2),
            "qualification_grade": grade,
            "erp_stage": ERP_STAGE_MAP[grade],
            "dimension_scores": [
                self.get_dimension_score(interaction_id, ds.dimension)
                for ds in dim_scores
            ],
        }

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC: Mark trigger as deployed
    # ─────────────────────────────────────────────────────────────────────────

    def mark_trigger_deployed(self, interaction_id: str, dimension: str) -> bool:
        interaction_uuid = self._normalize_uuid(interaction_id)
        dim_score = self.db.query(DimensionScore).filter(
            DimensionScore.interaction_id == interaction_uuid,
            DimensionScore.dimension == dimension,
        ).first()

        if not dim_score:
            return False

        dim_score.trigger_deployed = True
        self.db.commit()
        return True

    # ─────────────────────────────────────────────────────────────────────────
    # PRIVATE: Get or create DimensionScore
    # ─────────────────────────────────────────────────────────────────────────

    def _get_or_create_dimension_score(self, interaction_id: uuid.UUID, dimension: str) -> DimensionScore:
        dim_score = self.db.query(DimensionScore).filter(
            DimensionScore.interaction_id == interaction_id,
            DimensionScore.dimension == dimension,
        ).first()

        if not dim_score:
            interaction = self.db.query(Interaction).filter(
                Interaction.interaction_id == interaction_id
            ).first()
            if not interaction:
                raise ValueError(f"Interaction {interaction_id} not found")

            dim_score = DimensionScore(
                dimension_score_id=uuid.uuid4(),
                interaction_id=interaction_id,
                prospect_id=interaction.prospect_id,
                dimension=dimension,
                dimension_version="1.0.0",
                max_score=DIMENSION_MAX_SCORES.get(dimension, 0),
                achieved_score=0,
                score_percentage=0,
                trigger_deployed=False,
            )
            self.db.add(dim_score)
            self.db.flush()

        return dim_score

    # ─────────────────────────────────────────────────────────────────────────
    # PRIVATE: Get or create SignalScore
    # ─────────────────────────────────────────────────────────────────────────

    def _get_or_create_signal_score(
        self,
        dim_score: DimensionScore,
        interaction_id: uuid.UUID,
        signal_name: str,
    ) -> tuple[SignalScore, bool]:
        signal = self.db.query(SignalScore).filter(
            SignalScore.dimension_score_id == dim_score.dimension_score_id,
            SignalScore.signal_name == signal_name,
        ).first()

        created = False
        if not signal:
            signal = SignalScore(
                signal_score_id=uuid.uuid4(),
                dimension_score_id=dim_score.dimension_score_id,
                interaction_id=interaction_id,
                prospect_id=dim_score.prospect_id,
                signal_name=signal_name,
                score_given=0,
                max_signal_score=2,
                score_history=[],
            )
            self.db.add(signal)
            self.db.flush()
            created = True

        return signal, created

    # ─────────────────────────────────────────────────────────────────────────
    # PRIVATE: Recalculate dimension score from all its signals
    # ─────────────────────────────────────────────────────────────────────────

    def _recalculate_dimension(
        self,
        dim_score: DimensionScore,
        interaction_id: uuid.UUID,
        dimension: str,
    ) -> dict:
        signals = self.db.query(SignalScore).filter(
            SignalScore.dimension_score_id == dim_score.dimension_score_id
        ).all()

        total = sum(s.score_given or 0 for s in signals)
        max_score = dim_score.max_score
        percentage = round((total / max_score) * 100, 2) if max_score > 0 else 0

        # Determine tier from framework database
        tier, tier_label, trigger_text = self._get_tier_and_trigger(dimension, total)

        dim_score.achieved_score = Decimal(str(total))
        dim_score.score_percentage = Decimal(str(percentage))
        dim_score.score_tier = tier
        dim_score.tier_label = tier_label
        dim_score.system_trigger = trigger_text
        dim_score.scored_at = datetime.utcnow()

        return {
            "dimension": dimension,
            "achieved_score": total,
            "max_score": max_score,
            "score_percentage": percentage,
            "tier": tier,
            "tier_label": tier_label,
            "system_trigger": trigger_text,
            "trigger_deployed": dim_score.trigger_deployed,
            "signals": [
                {
                    "signal_name": s.signal_name,
                    "score": s.score_given or 0,
                    "max_score": s.max_signal_score,
                    "notes": s.signal_notes,
                }
                for s in signals
            ],
        }

    # ─────────────────────────────────────────────────────────────────────────
    # PRIVATE: Determine tier and fetch trigger text from DB
    # ─────────────────────────────────────────────────────────────────────────

    def _get_tier_and_trigger(self, dimension: str, score: int) -> tuple:
        # Load framework dimension for tier thresholds
        fw_dim = self.db.query(FrameworkDimension).filter(
            FrameworkDimension.dimension_name == dimension
        ).first()

        if fw_dim and fw_dim.tier_thresholds:
            thresholds = fw_dim.tier_thresholds
        else:
            # Fallback thresholds if seed data not loaded
            thresholds = _default_thresholds(dimension)

        tier = _score_to_tier(score, thresholds)
        tier_label = _tier_label(dimension, tier)

        # Fetch trigger text from DB
        trigger_text = None
        fw_trigger = self.db.query(FrameworkTrigger).join(FrameworkDimension).filter(
            FrameworkDimension.dimension_name == dimension,
            FrameworkTrigger.tier == tier,
        ).first()

        if fw_trigger:
            trigger_text = fw_trigger.trigger_text
        else:
            trigger_text = DEFAULT_TRIGGERS.get(dimension, {}).get(tier)

        return tier, tier_label, trigger_text

    # ─────────────────────────────────────────────────────────────────────────
    # PRIVATE: Recalculate and persist overall interaction score
    # ─────────────────────────────────────────────────────────────────────────

    def _recalculate_overall_score(self, interaction_id: uuid.UUID):
        dim_scores = self.db.query(DimensionScore).filter(
            DimensionScore.interaction_id == interaction_id,
            DimensionScore.dimension != "solution_routing",  # D5 not scored
        ).all()

        total = sum(float(d.achieved_score or 0) for d in dim_scores)

        interaction = self.db.query(Interaction).filter(
            Interaction.interaction_id == interaction_id
        ).first()

        if interaction:
            interaction.overall_score = Decimal(str(round(total, 2)))

    @staticmethod
    def _normalize_uuid(value: str | uuid.UUID) -> uuid.UUID:
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(str(value))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid interaction_id: {value}") from exc


# ─────────────────────────────────────────────────────────────────────────────
# Module-level helpers
# ─────────────────────────────────────────────────────────────────────────────

def _default_thresholds(dimension: str) -> dict:
    """Fallback thresholds matching design doc Section 4.1."""
    defaults = {
        "competitive_awareness": {"low": [0, 3], "emerging": [4, 6], "high": [7, 10]},
        "brand_gap":             {"low": [0, 4], "emerging": [5, 8], "high": [9, 12]},
        "is_maturity":           {"low": [0, 4], "emerging": [5, 9], "high": [10, 14]},
        "cost_of_status_quo":    {"low": [0, 4], "emerging": [5, 9], "high": [10, 14]},
    }
    return defaults.get(dimension, {"low": [0, 3], "emerging": [4, 7], "high": [8, 10]})


def _score_to_tier(score: int, thresholds: dict) -> str:
    if score <= thresholds["low"][1]:
        return "low"
    elif score <= thresholds["emerging"][1]:
        return "emerging"
    return "high"


def _tier_label(dimension: str, tier: str) -> str:
    labels = {
        "competitive_awareness": {
            "low": "Low Awareness",
            "emerging": "Emerging Awareness",
            "high": "High Awareness",
        },
        "brand_gap": {
            "low": "No Perceived Gap",
            "emerging": "Emerging Gap Awareness",
            "high": "Clear Gap Recognition",
        },
        "is_maturity": {
            "low": "Low IS Maturity Awareness",
            "emerging": "Emerging IS Pain",
            "high": "Active IS Pain / Readiness",
        },
        "cost_of_status_quo": {
            "low": "Low Cost Awareness",
            "emerging": "Emerging Urgency",
            "high": "Genuine Urgency Established",
        },
    }
    return labels.get(dimension, {}).get(tier, tier.capitalize())
