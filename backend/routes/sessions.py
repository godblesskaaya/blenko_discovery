"""
Discovery session routes.
Handles: create session, retrieve session, autosave, complete session,
         dashboard session list, pain flags, notes.
"""
import uuid
from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from middleware.auth_middleware import get_current_user
from models.database import (
    Prospect, Interaction, BusinessProfile,
    DimensionScore, PainFlag, ProspectNote, User,
)
from models.schemas import (
    SessionCreate, SessionResponse, SessionDetail,
    AutoSavePayload, PainFlagCreate, PainFlagResponse,
    NoteCreate, NoteResponse,
)
from services.scoring_engine import ScoringEngine, calculate_grade

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# POST /sessions/create  — Start a new discovery session
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
@router.post("/create", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreate | dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates Prospect + Interaction + BusinessProfile in one atomic transaction.
    Returns session_id and prospect_id for all subsequent calls.
    """
    normalized_payload = _normalize_session_create_payload(payload)

    # 1. Create Prospect
    prospect = Prospect(
        **normalized_payload.prospect.model_dump(),
        created_by=current_user.user_id,
    )
    db.add(prospect)
    db.flush()  # Get prospect_id without committing

    # 2. Create Interaction (the session)
    interaction = Interaction(
        prospect_id=prospect.prospect_id,
        interaction_type="discovery",
        interaction_date=datetime.utcnow(),
        conducted_by=current_user.user_id,
        session_status="in_progress",
        overall_score=0,
    )
    db.add(interaction)
    db.flush()

    # 3. Create BusinessProfile (Layer Zero)
    profile_data = normalized_payload.business_profile.model_dump(exclude_none=True)
    business_profile = BusinessProfile(
        prospect_id=prospect.prospect_id,
        interaction_id=interaction.interaction_id,
        captured_by=current_user.user_id,
        **profile_data,
    )
    db.add(business_profile)

    db.commit()
    db.refresh(interaction)

    return SessionResponse(
        session_id=interaction.interaction_id,
        prospect_id=prospect.prospect_id,
        status=interaction.session_status,
        overall_score=float(interaction.overall_score or 0),
        created_at=interaction.created_at,
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /sessions/{session_id}  — Load a full session
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/{session_id}", response_model=SessionDetail)
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    interaction = _get_interaction_or_404(session_id, db)
    _check_session_access(interaction, current_user)

    prospect = db.query(Prospect).filter(
        Prospect.prospect_id == interaction.prospect_id
    ).first()

    business_profile = db.query(BusinessProfile).filter(
        BusinessProfile.interaction_id == interaction.interaction_id
    ).first()

    dim_scores = db.query(DimensionScore).filter(
        DimensionScore.interaction_id == interaction.interaction_id
    ).all()

    engine = ScoringEngine(db)
    dimension_score_data = [
        engine.get_dimension_score(session_id, ds.dimension)
        for ds in dim_scores
    ]

    return SessionDetail(
        session_id=interaction.interaction_id,
        prospect=prospect,
        business_profile=business_profile,
        overall_score=float(interaction.overall_score or 0),
        session_status=interaction.session_status,
        dimension_scores=dimension_score_data,
        created_at=interaction.created_at,
    )


# ─────────────────────────────────────────────────────────────────────────────
# PATCH /sessions/{session_id}/autosave  — Field-level autosave
# ─────────────────────────────────────────────────────────────────────────────

@router.patch("/{session_id}/autosave")
def autosave_session(
    session_id: str,
    payload: AutoSavePayload | dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Called by frontend on every meaningful field change.
    Updates session timestamp to confirm data is persisted.
    Actual field updates go through their specific endpoints
    (scoring, pain flags, etc.) — this handles free-text fields.
    """
    interaction = _get_interaction_or_404(session_id, db)
    _check_session_access(interaction, current_user)

    normalized = _normalize_autosave_payload(payload)

    # Route autosave to the right record based on context
    if normalized.context == "business_profile":
        bp = db.query(BusinessProfile).filter(
            BusinessProfile.interaction_id == interaction.interaction_id
        ).first()
        if bp and hasattr(bp, normalized.field):
            setattr(bp, normalized.field, normalized.value)

    elif normalized.context and normalized.context.startswith("dimension:"):
        dimension = normalized.context.split(":")[1]
        ds = db.query(DimensionScore).filter(
            DimensionScore.interaction_id == interaction.interaction_id,
            DimensionScore.dimension == dimension,
        ).first()
        if ds and normalized.field == "dimension_notes":
            ds.dimension_notes = normalized.value

    elif normalized.field in ("key_pain_notes", "persona_notes", "summary"):
        setattr(interaction, normalized.field, normalized.value)

    interaction.updated_at = datetime.utcnow()
    db.commit()

    return {"status": "saved", "timestamp": interaction.updated_at.isoformat()}


# ─────────────────────────────────────────────────────────────────────────────
# PATCH /sessions/{session_id}/complete  — Mark session complete
# ─────────────────────────────────────────────────────────────────────────────

@router.patch("/{session_id}/complete")
@router.post("/{session_id}/complete")
def complete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    interaction = _get_interaction_or_404(session_id, db)
    _check_session_access(interaction, current_user)

    interaction.session_status = "complete"
    interaction.updated_at = datetime.utcnow()
    db.commit()

    grade = calculate_grade(float(interaction.overall_score or 0))
    return {
        "status": "complete",
        "session_id": str(interaction.interaction_id),
        "overall_score": float(interaction.overall_score or 0),
        "qualification_grade": grade,
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /sessions  — Dashboard: all sessions for current user
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/")
def list_sessions(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(25, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Interaction)

    # Reps only see their own sessions; managers/admins see all
    if current_user.role == "rep":
        query = query.filter(Interaction.conducted_by == current_user.user_id)

    if status_filter:
        query = query.filter(Interaction.session_status == status_filter)

    query = query.filter(Interaction.interaction_type == "discovery")
    total = query.count()
    interactions = query.order_by(Interaction.created_at.desc()).offset(offset).limit(limit).all()

    results = []
    for i in interactions:
        prospect = db.query(Prospect).filter(Prospect.prospect_id == i.prospect_id).first()
        grade = calculate_grade(float(i.overall_score or 0))
        results.append({
            "session_id": str(i.interaction_id),
            "company_name": prospect.company_name if prospect else "Unknown",
            "contact_name": prospect.contact_name if prospect else "Unknown",
            "overall_score": float(i.overall_score or 0),
            "qualification_grade": grade,
            "session_status": i.session_status,
            "persona_detected": i.persona_detected,
            "created_at": i.created_at.isoformat(),
            "updated_at": i.updated_at.isoformat() if i.updated_at else None,
        })

    return {"total": total, "offset": offset, "limit": limit, "sessions": results}


# ─────────────────────────────────────────────────────────────────────────────
# POST /sessions/{session_id}/pain-flags
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/{session_id}/pain-flags", response_model=PainFlagResponse, status_code=201)
def create_pain_flag(
    session_id: str,
    payload: PainFlagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    interaction = _get_interaction_or_404(session_id, db)

    flag = PainFlag(
        interaction_id=interaction.interaction_id,
        prospect_id=interaction.prospect_id,
        flagged_by=current_user.user_id,
        **payload.model_dump(),
    )
    db.add(flag)
    db.commit()
    db.refresh(flag)
    return flag


@router.get("/{session_id}/pain-flags", response_model=List[PainFlagResponse])
def list_pain_flags(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    interaction = _get_interaction_or_404(session_id, db)
    flags = db.query(PainFlag).filter(PainFlag.interaction_id == interaction.interaction_id).all()
    return flags


# ─────────────────────────────────────────────────────────────────────────────
# Notes
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/{session_id}/notes", response_model=NoteResponse, status_code=201)
def create_note(
    session_id: str,
    payload: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    interaction = _get_interaction_or_404(session_id, db)
    note = ProspectNote(
        prospect_id=interaction.prospect_id,
        interaction_id=interaction.interaction_id,
        note_type=payload.note_type,
        note_content=payload.note_content,
        is_pinned=payload.is_pinned,
        created_by=current_user.user_id,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_interaction_or_404(session_id: str, db: Session) -> Interaction:
    session_uuid = _parse_uuid(session_id, field_name="session_id")
    interaction = db.query(Interaction).filter(
        Interaction.interaction_id == session_uuid
    ).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Session not found")
    return interaction


def _check_session_access(interaction: Interaction, user: User):
    """Reps can only access their own sessions."""
    if user.role == "rep" and str(interaction.conducted_by) != str(user.user_id):
        raise HTTPException(status_code=403, detail="Access denied")


def _normalize_autosave_payload(payload: AutoSavePayload | dict[str, Any]) -> AutoSavePayload:
    """
    Supports:
    1) Structured payload: {"field": "...", "value": "...", "context": "..."}
    2) Legacy payload: {"key_pain_notes": "..."} (single top-level field)
    """
    if isinstance(payload, AutoSavePayload):
        return payload

    if "field" in payload and "value" in payload:
        return AutoSavePayload(
            field=payload["field"],
            value=payload["value"],
            context=payload.get("context"),
        )

    if len(payload) == 1:
        field, value = next(iter(payload.items()))
        return AutoSavePayload(field=field, value=value, context=None)

    raise HTTPException(
        status_code=422,
        detail="Invalid autosave payload. Use {'field','value'} or a single key-value pair.",
    )


def _normalize_session_create_payload(payload: SessionCreate | dict[str, Any]) -> SessionCreate:
    if isinstance(payload, SessionCreate):
        return payload

    raw_prospect = payload.get("prospect") or payload.get("prospect_data")
    raw_profile = payload.get("business_profile") or payload.get("profile_data") or {}

    if not raw_prospect:
        raise HTTPException(status_code=422, detail="Missing prospect data")

    prospect_key_map = {
        "companyName": "company_name",
        "contactName": "contact_name",
        "contactRole": "contact_role",
        "contactEmail": "contact_email",
        "contactPhone": "contact_phone",
        "businessType": "business_type",
        "sizeTier": "size_tier",
        "growthStage": "growth_stage",
        "geographicScope": "geographic_scope",
        "vendorStatus": "vendor_status",
        "growthAmbition": "growth_ambition",
    }
    profile_key_map = {
        "triggerEvent": "trigger_event",
        "triggerCategory": "trigger_category",
        "currentVendors": "current_vendors",
        "competitiveContext": "competitive_context",
        "additionalContext": "additional_context",
        "vendorPainNotes": "vendor_pain_notes",
        "strategicPriorities": "strategic_priorities",
        "primaryTriggerDimension": "primary_trigger_dimension",
    }

    normalized_prospect: dict[str, Any] = {}
    normalized_profile: dict[str, Any] = {}

    for key, value in raw_prospect.items():
        normalized_prospect[prospect_key_map.get(key, key)] = value

    for key, value in raw_profile.items():
        normalized_profile[profile_key_map.get(key, key)] = value

    try:
        return SessionCreate(
            prospect=normalized_prospect,
            business_profile=normalized_profile,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Invalid session payload: {exc}") from exc


def _parse_uuid(value: str, field_name: str = "id") -> uuid.UUID:
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=f"Invalid {field_name}") from exc
