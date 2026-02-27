"""
Scoring routes.
All signal updates flow through here — engine recalculates immediately.
Target: full round-trip (API call → DB update → response) < 100ms.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from database import get_db
from middleware.auth_middleware import get_current_user
from models.database import User
from models.schemas import SignalScoreUpdate, DimensionScoreResponse, OverallScoreResponse
from services.scoring_engine import ScoringEngine

router = APIRouter()


class LegacySignalUpdate(BaseModel):
    interaction_id: str
    dimension: str
    signal_name: str
    score: int
    notes: Optional[str] = None

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: int) -> int:
        if v not in (0, 1, 2):
            raise ValueError("Score must be 0, 1, or 2")
        return v


@router.post("/{session_id}/signal")
def update_signal(
    session_id: str,
    payload: SignalScoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Primary real-time scoring endpoint.
    Frontend calls this on every 0/1/2 radio button change.
    Returns updated dimension totals immediately.
    """
    engine = ScoringEngine(db)
    try:
        result = engine.update_signal_score(
            interaction_id=session_id,
            dimension=payload.dimension,
            signal_name=payload.signal_name,
            score=payload.score,
            notes=payload.notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": "updated",
        "session_id": session_id,
        "dimension": payload.dimension,
        "interaction_id": session_id,
        "signal": payload.signal_name,
        "signal_name": payload.signal_name,
        "score_given": payload.score,
        "score": payload.score,
        "dimension_result": result,
        "dimension_total": result,
    }


@router.get("/{session_id}/dimension/{dimension}", response_model=DimensionScoreResponse)
def get_dimension_score(
    session_id: str,
    dimension: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    engine = ScoringEngine(db)
    result = engine.get_dimension_score(session_id, dimension)
    result["score_tier"] = result.get("tier")
    return result


@router.get("/{session_id}/overall", response_model=OverallScoreResponse)
def get_overall_score(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    engine = ScoringEngine(db)
    try:
        return engine.get_overall_score(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/signal")
def update_signal_legacy(
    payload: LegacySignalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Legacy compatibility endpoint:
    POST /api/scoring/signal with interaction_id in the body.
    """
    engine = ScoringEngine(db)
    try:
        result = engine.update_signal_score(
            interaction_id=payload.interaction_id,
            dimension=payload.dimension,
            signal_name=payload.signal_name,
            score=payload.score,
            notes=payload.notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": "updated",
        "interaction_id": payload.interaction_id,
        "dimension": payload.dimension,
        "signal": payload.signal_name,
        "signal_name": payload.signal_name,
        "score": payload.score,
        "score_given": payload.score,
        "dimension_total": result,
        "dimension_result": result,
    }


@router.get("/dimension/{interaction_id}/{dimension}")
def get_dimension_score_legacy(
    interaction_id: str,
    dimension: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Legacy compatibility endpoint:
    GET /api/scoring/dimension/{interaction_id}/{dimension}
    """
    engine = ScoringEngine(db)
    result = engine.get_dimension_score(interaction_id, dimension)
    result["score_tier"] = result.get("tier")
    return result


@router.get("/overall/{interaction_id}")
def get_overall_score_legacy(
    interaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Legacy compatibility endpoint:
    GET /api/scoring/overall/{interaction_id}
    """
    engine = ScoringEngine(db)
    try:
        return engine.get_overall_score(interaction_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{session_id}/trigger/{dimension}/acknowledge")
def acknowledge_trigger(
    session_id: str,
    dimension: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rep acknowledges a system trigger — marks it deployed and advances dimension."""
    engine = ScoringEngine(db)
    success = engine.mark_trigger_deployed(session_id, dimension)
    if not success:
        raise HTTPException(status_code=404, detail="Dimension score not found")
    return {"status": "trigger_acknowledged", "dimension": dimension}


@router.get("/{session_id}/framework/{dimension}")
def get_framework_content(
    session_id: str,
    dimension: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns all framework content for a dimension (questions, probes, signals, reframes).
    Frontend renders directly from this — no hardcoded content in UI.
    """
    from models.database import FrameworkDimension
    fw = db.query(FrameworkDimension).filter(
        FrameworkDimension.dimension_name == dimension
    ).first()

    if not fw:
        raise HTTPException(status_code=404, detail=f"Framework content for '{dimension}' not found")

    return {
        "dimension_name": fw.dimension_name,
        "dimension_label": fw.dimension_label,
        "max_score": fw.max_score,
        "opening_question": fw.opening_question,
        "positioning_moment": fw.positioning_moment,
        "tier_thresholds": fw.tier_thresholds,
        "framework_version": fw.framework_version,
        "signals": [
            {
                "signal_id": str(s.signal_id),
                "signal_code": s.signal_code,
                "signal_name": s.signal_name,
                "signal_description": s.signal_description,
                "max_signal_score": s.max_signal_score,
                "display_order": s.display_order,
            }
            for s in sorted(fw.signals, key=lambda x: x.display_order or 0)
        ],
        "probes": [
            {
                "probe_id": str(p.probe_id),
                "probe_label": p.probe_label,
                "probe_text": p.probe_text,
                "follow_up_text": p.follow_up_text,
                "priority_personas": p.priority_personas,
                "display_order": p.display_order,
            }
            for p in sorted(fw.probes, key=lambda x: x.display_order or 0)
        ],
        "reframes": [
            {
                "reframe_id": str(r.reframe_id),
                "reframe_label": r.reframe_label,
                "reframe_text": r.reframe_text,
                "trigger_condition": r.trigger_condition,
                "display_order": r.display_order,
            }
            for r in sorted(fw.reframes, key=lambda x: x.display_order or 0)
        ],
    }
