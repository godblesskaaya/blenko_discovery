"""
Blenko Discovery System - Database Models
All 12 entities as defined in Design Doc Section 6.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DECIMAL, Enum, ForeignKey,
    Integer, String, Text, TIMESTAMP, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base

# ─────────────────────────────────────────────
# ENTITY 11: User  (defined first — others FK to it)
# ─────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(
        Enum("rep", "domain_expert", "manager", "admin", name="user_role_enum"),
        nullable=False
    )
    specialization = Column(
        Enum(
            "brand_apparel", "print_collateral", "digital_web",
            "erp_crm", "it_infrastructure", "software_custom", "general",
            name="specialization_enum"
        )
    )
    erp_user_id = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    last_login = Column(TIMESTAMP)

    # Relationships
    prospects_created = relationship("Prospect", back_populates="creator", foreign_keys="Prospect.created_by")
    interactions_conducted = relationship("Interaction", back_populates="conductor", foreign_keys="Interaction.conducted_by")


# ─────────────────────────────────────────────
# ENTITY 1: Prospect
# ─────────────────────────────────────────────

class Prospect(Base):
    __tablename__ = "prospects"

    prospect_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=False)
    contact_role = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    industry = Column(String(100))
    business_type = Column(
        Enum(
            "service", "trade", "retail", "manufacturing",
            "hospitality", "professional", "other",
            name="business_type_enum"
        )
    )
    size_tier = Column(
        Enum("micro", "small", "medium", "large", name="size_tier_enum")
    )
    headcount = Column(Integer)
    revenue_range = Column(String(50))
    growth_stage = Column(
        Enum(
            "early_growth", "active_growth", "scaling",
            "established", "consolidating",
            name="growth_stage_enum"
        )
    )
    geographic_scope = Column(
        Enum("local", "regional", "national", "multi_site", name="geo_scope_enum")
    )
    vendor_status = Column(
        Enum("none", "ad_hoc", "established", "unhappy", name="vendor_status_enum")
    )
    growth_ambition = Column(
        Enum("high", "moderate", "maintenance", name="growth_ambition_enum")
    )
    erp_lead_id = Column(String(100))
    erp_opportunity_id = Column(String(100))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))

    # Relationships
    creator = relationship("User", back_populates="prospects_created", foreign_keys=[created_by])
    interactions = relationship("Interaction", back_populates="prospect")
    business_profiles = relationship("BusinessProfile", back_populates="prospect")
    persona_detections = relationship("PersonaDetection", back_populates="prospect")
    dimension_scores = relationship("DimensionScore", back_populates="prospect")
    signal_scores = relationship("SignalScore", back_populates="prospect")
    pain_flags = relationship("PainFlag", back_populates="prospect")
    solution_flags = relationship("SolutionFlag", back_populates="prospect")
    qualification_summaries = relationship("QualificationSummary", back_populates="prospect")
    interaction_briefs = relationship("InteractionIntelligenceBrief", back_populates="prospect")
    notes = relationship("ProspectNote", back_populates="prospect")


# ─────────────────────────────────────────────
# ENTITY 2: Interaction
# ─────────────────────────────────────────────

class Interaction(Base):
    __tablename__ = "interactions"

    interaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prospect_id = Column(UUID(as_uuid=True), ForeignKey("prospects.prospect_id"), nullable=False)
    interaction_type = Column(
        Enum(
            "discovery", "follow_up_brand", "follow_up_print",
            "follow_up_digital", "follow_up_erp_crm",
            "follow_up_it_infra", "follow_up_software",
            "email", "site_visit", "proposal", "other",
            name="interaction_type_enum"
        ),
        nullable=False
    )
    interaction_date = Column(TIMESTAMP, default=datetime.utcnow)
    conducted_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    persona_detected = Column(
        Enum(
            "executive_sponsor", "champion", "gatekeeper", "end_user", "unknown",
            name="persona_type_enum"
        )
    )
    persona_notes = Column(Text)
    duration_minutes = Column(Integer)
    overall_score = Column(DECIMAL(5, 2))
    session_status = Column(
        Enum("in_progress", "complete", "abandoned", name="session_status_enum"),
        default="in_progress"
    )
    summary = Column(Text)
    key_pain_notes = Column(Text)
    next_interaction_id = Column(UUID(as_uuid=True), ForeignKey("interactions.interaction_id"))
    previous_interaction_id = Column(UUID(as_uuid=True), ForeignKey("interactions.interaction_id"))
    erp_task_id = Column(String(100))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    prospect = relationship("Prospect", back_populates="interactions")
    conductor = relationship("User", back_populates="interactions_conducted", foreign_keys=[conducted_by])
    business_profile = relationship("BusinessProfile", back_populates="interaction", uselist=False)
    persona_detection = relationship("PersonaDetection", back_populates="interaction", uselist=False)
    dimension_scores = relationship("DimensionScore", back_populates="interaction")
    signal_scores = relationship("SignalScore", back_populates="interaction")
    pain_flags = relationship("PainFlag", back_populates="interaction")
    solution_flags = relationship("SolutionFlag", back_populates="interaction")
    qualification_summary = relationship("QualificationSummary", back_populates="interaction", uselist=False)
    notes = relationship("ProspectNote", back_populates="interaction")


# ─────────────────────────────────────────────
# ENTITY 3: BusinessProfile (Layer Zero)
# ─────────────────────────────────────────────

class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prospect_id = Column(UUID(as_uuid=True), ForeignKey("prospects.prospect_id"), nullable=False)
    interaction_id = Column(UUID(as_uuid=True), ForeignKey("interactions.interaction_id"), nullable=False)
    trigger_event = Column(Text)
    trigger_category = Column(
        Enum(
            "new_contract", "rebranding", "system_failure",
            "competitor_move", "new_hire", "upcoming_event",
            "growth_pressure", "vendor_dissatisfaction",
            "referral", "other",
            name="trigger_category_enum"
        )
    )
    primary_trigger_dimension = Column(
        Enum(
            "competitive_awareness", "brand_gap",
            "is_maturity", "cost_of_status_quo",
            name="trigger_dimension_enum"
        )
    )
    current_vendors = Column(JSON)
    vendor_pain_notes = Column(Text)
    competitive_context = Column(Text)
    strategic_priorities = Column(Text)
    additional_context = Column(Text)
    captured_at = Column(TIMESTAMP, default=datetime.utcnow)
    captured_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))

    # Relationships
    prospect = relationship("Prospect", back_populates="business_profiles")
    interaction = relationship("Interaction", back_populates="business_profile")


# ─────────────────────────────────────────────
# ENTITY 4: PersonaDetection
# ─────────────────────────────────────────────

class PersonaDetection(Base):
    __tablename__ = "persona_detections"

    persona_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interaction_id = Column(UUID(as_uuid=True), ForeignKey("interactions.interaction_id"), nullable=False)
    prospect_id = Column(UUID(as_uuid=True), ForeignKey("prospects.prospect_id"), nullable=False)
    contact_name = Column(String(255))
    detected_persona = Column(
        Enum(
            "executive_sponsor", "champion", "gatekeeper", "end_user",
            name="detected_persona_enum"
        )
    )
    detection_confidence = Column(
        Enum("high", "medium", "low", name="detection_confidence_enum")
    )
    authority_level = Column(
        Enum("full", "partial", "none", name="authority_level_enum")
    )
    decision_role = Column(Text)
    primary_motivation = Column(Text)
    primary_fear = Column(Text)
    internal_allies = Column(Text)
    internal_obstacles = Column(Text)
    champion_notes = Column(Text)
    executive_path = Column(Text)
    rep_strategy_notes = Column(Text)
    multi_stakeholder = Column(Boolean, default=False)
    multi_stakeholder_notes = Column(Text)
    detected_at = Column(TIMESTAMP, default=datetime.utcnow)
    detected_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))

    # Relationships
    prospect = relationship("Prospect", back_populates="persona_detections")
    interaction = relationship("Interaction", back_populates="persona_detection")


# ─────────────────────────────────────────────
# ENTITY 5: DimensionScore
# ─────────────────────────────────────────────

class DimensionScore(Base):
    __tablename__ = "dimension_scores"

    dimension_score_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interaction_id = Column(UUID(as_uuid=True), ForeignKey("interactions.interaction_id"), nullable=False)
    prospect_id = Column(UUID(as_uuid=True), ForeignKey("prospects.prospect_id"), nullable=False)
    dimension = Column(
        Enum(
            "competitive_awareness", "brand_gap", "is_maturity",
            "cost_of_status_quo", "solution_routing",
            name="dimension_enum"
        ),
        nullable=False
    )
    dimension_version = Column(String(10), default="1.0.0")
    max_score = Column(Integer, nullable=False)
    achieved_score = Column(DECIMAL(5, 2), default=0)
    score_percentage = Column(DECIMAL(5, 2), default=0)
    score_tier = Column(
        Enum("low", "emerging", "high", name="score_tier_enum")
    )
    tier_label = Column(String(100))
    system_trigger = Column(Text)
    trigger_deployed = Column(Boolean, default=False)
    probes_used = Column(JSON)
    reframes_deployed = Column(JSON)
    dimension_notes = Column(Text)
    scored_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    prospect = relationship("Prospect", back_populates="dimension_scores")
    interaction = relationship("Interaction", back_populates="dimension_scores")
    signal_scores = relationship("SignalScore", back_populates="dimension_score")


# ─────────────────────────────────────────────
# ENTITY 6: SignalScore
# ─────────────────────────────────────────────

class SignalScore(Base):
    __tablename__ = "signal_scores"

    signal_score_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dimension_score_id = Column(UUID(as_uuid=True), ForeignKey("dimension_scores.dimension_score_id"), nullable=False)
    interaction_id = Column(UUID(as_uuid=True), ForeignKey("interactions.interaction_id"), nullable=False)
    prospect_id = Column(UUID(as_uuid=True), ForeignKey("prospects.prospect_id"), nullable=False)
    signal_name = Column(String(100), nullable=False)
    signal_description = Column(Text)
    score_given = Column(Integer, default=0)
    max_signal_score = Column(Integer, default=2)
    signal_notes = Column(Text)
    scored_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Audit trail: previous scores stored as JSON array
    score_history = Column(JSON, default=list)

    # Relationships
    dimension_score = relationship("DimensionScore", back_populates="signal_scores")
    interaction = relationship("Interaction", back_populates="signal_scores")
    prospect = relationship("Prospect", back_populates="signal_scores")


# ─────────────────────────────────────────────
# ENTITY 7: PainFlag
# ─────────────────────────────────────────────

class PainFlag(Base):
    __tablename__ = "pain_flags"

    pain_flag_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interaction_id = Column(UUID(as_uuid=True), ForeignKey("interactions.interaction_id"), nullable=False)
    prospect_id = Column(UUID(as_uuid=True), ForeignKey("prospects.prospect_id"), nullable=False)
    dimension = Column(
        Enum(
            "competitive_awareness", "brand_gap", "is_maturity",
            "cost_of_status_quo", "solution_routing",
            name="pain_dimension_enum"
        )
    )
    pain_category = Column(
        Enum(
            "brand_presentation", "apparel_quality", "print_collateral",
            "digital_presence", "web_infrastructure", "email_infrastructure",
            "business_management", "erp_crm", "network_infrastructure",
            "it_security", "software_custom", "operational_friction",
            "competitive_pressure", "vendor_failure", "cost_of_status_quo",
            "scalability", "reputation_risk", "team_consistency", "other",
            name="pain_category_enum"
        )
    )
    pain_intensity = Column(
        Enum("low", "medium", "high", "critical", name="pain_intensity_enum")
    )
    pain_description = Column(Text)
    prospect_quoted = Column(Text)
    quantified_cost = Column(DECIMAL(12, 2))
    quantified_unit = Column(
        Enum(
            "per_day", "per_week", "per_month", "per_year",
            "total", "unknown",
            name="quantified_unit_enum"
        )
    )
    quantification_notes = Column(Text)
    status = Column(
        Enum(
            "unaddressed", "in_discussion", "solution_proposed", "resolved",
            name="pain_status_enum"
        ),
        default="unaddressed"
    )
    flagged_at = Column(TIMESTAMP, default=datetime.utcnow)
    flagged_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))

    # Relationships
    prospect = relationship("Prospect", back_populates="pain_flags")
    interaction = relationship("Interaction", back_populates="pain_flags")


# ─────────────────────────────────────────────
# ENTITY 8: SolutionFlag
# ─────────────────────────────────────────────

class SolutionFlag(Base):
    __tablename__ = "solution_flags"

    solution_flag_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interaction_id = Column(UUID(as_uuid=True), ForeignKey("interactions.interaction_id"), nullable=False)
    prospect_id = Column(UUID(as_uuid=True), ForeignKey("prospects.prospect_id"), nullable=False)
    solution_area = Column(
        Enum(
            "brand_apparel", "print_collateral", "digital_web",
            "erp_crm", "it_infrastructure", "software_custom",
            "full_brand_strategy", "it_consulting",
            "network_assessment", "brand_audit",
            name="solution_area_enum"
        )
    )
    priority_rank = Column(Integer)
    pain_flags_linked = Column(JSON)
    domain_expert = Column(String(255))
    follow_up_scheduled = Column(Boolean, default=False)
    follow_up_interaction_id = Column(UUID(as_uuid=True))
    prospect_stated_priority = Column(Boolean, default=False)
    rep_confidence = Column(
        Enum("low", "medium", "high", name="rep_confidence_enum")
    )
    estimated_value = Column(DECIMAL(12, 2))
    solution_notes = Column(Text)
    status = Column(
        Enum(
            "flagged", "follow_up_scheduled", "in_discussion",
            "proposed", "won", "lost",
            name="solution_status_enum"
        ),
        default="flagged"
    )
    flagged_at = Column(TIMESTAMP, default=datetime.utcnow)
    flagged_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))

    # Relationships
    prospect = relationship("Prospect", back_populates="solution_flags")
    interaction = relationship("Interaction", back_populates="solution_flags")


# ─────────────────────────────────────────────
# ENTITY 9: QualificationSummary
# ─────────────────────────────────────────────

class QualificationSummary(Base):
    __tablename__ = "qualification_summaries"

    summary_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interaction_id = Column(UUID(as_uuid=True), ForeignKey("interactions.interaction_id"), nullable=False)
    prospect_id = Column(UUID(as_uuid=True), ForeignKey("prospects.prospect_id"), nullable=False)
    framework_version = Column(String(10), default="1.0.0")
    overall_score = Column(DECIMAL(5, 2))
    max_possible_score = Column(DECIMAL(5, 2), default=50)
    score_percentage = Column(DECIMAL(5, 2))
    qualification_grade = Column(
        Enum("unqualified", "developing", "qualified", "hot", name="qualification_grade_enum")
    )
    dimension_summary = Column(JSON)
    key_pains_summary = Column(Text)
    prospect_priority = Column(Text)
    solution_areas_count = Column(Integer)
    primary_solution = Column(String(100))
    routing_plan = Column(JSON)
    positioning_coverage = Column(JSON)
    cross_sell_potential = Column(
        Enum("low", "medium", "high", "full_portfolio", name="cross_sell_enum")
    )
    recommended_next_step = Column(Text)
    erp_pushed = Column(Boolean, default=False)
    erp_pushed_at = Column(TIMESTAMP)
    erp_opportunity_id = Column(String(100))
    pdf_generated = Column(Boolean, default=False)
    pdf_url = Column(String(500))
    champion_summary_generated = Column(Boolean, default=False)
    champion_summary_url = Column(String(500))
    generated_at = Column(TIMESTAMP, default=datetime.utcnow)
    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))

    # Relationships
    prospect = relationship("Prospect", back_populates="qualification_summaries")
    interaction = relationship("Interaction", back_populates="qualification_summary")


# ─────────────────────────────────────────────
# ENTITY 10: InteractionIntelligenceBrief
# ─────────────────────────────────────────────

class InteractionIntelligenceBrief(Base):
    __tablename__ = "interaction_intelligence_briefs"

    brief_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interaction_id = Column(UUID(as_uuid=True), ForeignKey("interactions.interaction_id"), nullable=False)
    prospect_id = Column(UUID(as_uuid=True), ForeignKey("prospects.prospect_id"), nullable=False)
    prepared_for = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    prepared_at = Column(TIMESTAMP, default=datetime.utcnow)
    previous_interactions = Column(JSON)
    persona_context = Column(Text)
    key_pains_relevant = Column(JSON)
    solution_context = Column(Text)
    open_questions = Column(Text)
    internal_dynamics = Column(Text)
    prospect_quotes = Column(JSON)
    positioning_notes = Column(Text)
    do_not_repeat = Column(Text)
    recommended_approach = Column(Text)
    cost_figures_identified = Column(JSON)
    erp_opportunity_stage = Column(String(100))
    brief_version = Column(String(10), default="1.0.0")

    # Relationships
    prospect = relationship("Prospect", back_populates="interaction_briefs")
    interaction = relationship("Interaction")


# ─────────────────────────────────────────────
# ENTITY 12: ProspectNote
# ─────────────────────────────────────────────

class ProspectNote(Base):
    __tablename__ = "prospect_notes"

    note_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prospect_id = Column(UUID(as_uuid=True), ForeignKey("prospects.prospect_id"), nullable=False)
    interaction_id = Column(UUID(as_uuid=True), ForeignKey("interactions.interaction_id"))
    note_type = Column(
        Enum(
            "observation", "quote", "objection", "opportunity",
            "risk", "relationship", "competitive_intel", "other",
            name="note_type_enum"
        )
    )
    note_content = Column(Text, nullable=False)
    is_pinned = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))

    # Relationships
    prospect = relationship("Prospect", back_populates="notes")
    interaction = relationship("Interaction", back_populates="notes")


# ─────────────────────────────────────────────
# FRAMEWORK CONTENT TABLES
# Stores all questions, probes, signals, reframes — never hardcoded in frontend
# ─────────────────────────────────────────────

class FrameworkDimension(Base):
    __tablename__ = "framework_dimensions"

    dimension_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dimension_name = Column(String(100), nullable=False, unique=True)
    dimension_label = Column(String(255))
    max_score = Column(Integer, nullable=False)
    framework_version = Column(String(10), nullable=False, default="1.0.0")
    opening_question = Column(Text)
    positioning_moment = Column(Text)
    tier_thresholds = Column(JSON)  # {"low": [0,3], "emerging": [4,6], "high": [7,10]}
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    signals = relationship("FrameworkSignal", back_populates="dimension")
    probes = relationship("FrameworkProbe", back_populates="dimension")
    reframes = relationship("FrameworkReframe", back_populates="dimension")
    triggers = relationship("FrameworkTrigger", back_populates="dimension")


class FrameworkSignal(Base):
    __tablename__ = "framework_signals"

    signal_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dimension_id = Column(UUID(as_uuid=True), ForeignKey("framework_dimensions.dimension_id"), nullable=False)
    signal_code = Column(String(20))   # e.g. "S1", "S2"
    signal_name = Column(String(100), nullable=False)
    signal_description = Column(Text)
    max_signal_score = Column(Integer, default=2)
    display_order = Column(Integer)
    framework_version = Column(String(10), default="1.0.0")

    # Relationships
    dimension = relationship("FrameworkDimension", back_populates="signals")


class FrameworkProbe(Base):
    __tablename__ = "framework_probes"

    probe_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dimension_id = Column(UUID(as_uuid=True), ForeignKey("framework_dimensions.dimension_id"), nullable=False)
    probe_label = Column(String(10))   # "A", "B", "C", etc.
    probe_text = Column(Text, nullable=False)
    follow_up_text = Column(Text)
    priority_personas = Column(JSON)  # ["executive_sponsor", "champion"]
    display_order = Column(Integer)
    framework_version = Column(String(10), default="1.0.0")

    # Relationships
    dimension = relationship("FrameworkDimension", back_populates="probes")


class FrameworkReframe(Base):
    __tablename__ = "framework_reframes"

    reframe_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dimension_id = Column(UUID(as_uuid=True), ForeignKey("framework_dimensions.dimension_id"), nullable=False)
    reframe_label = Column(String(100))
    reframe_text = Column(Text, nullable=False)
    trigger_condition = Column(Text)
    display_order = Column(Integer)
    framework_version = Column(String(10), default="1.0.0")

    # Relationships
    dimension = relationship("FrameworkDimension", back_populates="reframes")


class FrameworkTrigger(Base):
    __tablename__ = "framework_triggers"

    trigger_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dimension_id = Column(UUID(as_uuid=True), ForeignKey("framework_dimensions.dimension_id"), nullable=False)
    tier = Column(
        Enum("low", "emerging", "high", name="trigger_tier_enum"),
        nullable=False
    )
    trigger_text = Column(Text, nullable=False)
    persona_addendums = Column(JSON)  # {"executive_sponsor": "...", "champion": "..."}
    framework_version = Column(String(10), default="1.0.0")

    # Relationships
    dimension = relationship("FrameworkDimension", back_populates="triggers")
