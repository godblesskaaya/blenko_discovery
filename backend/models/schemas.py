"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


# ─── Enums ───────────────────────────────────────────────────────────────────

class BusinessTypeEnum(str, Enum):
    service = "service"
    trade = "trade"
    retail = "retail"
    manufacturing = "manufacturing"
    hospitality = "hospitality"
    professional = "professional"
    other = "other"


class SizeTierEnum(str, Enum):
    micro = "micro"
    small = "small"
    medium = "medium"
    large = "large"


class GrowthStageEnum(str, Enum):
    early_growth = "early_growth"
    active_growth = "active_growth"
    scaling = "scaling"
    established = "established"
    consolidating = "consolidating"


class GeoScopeEnum(str, Enum):
    local = "local"
    regional = "regional"
    national = "national"
    multi_site = "multi_site"


class VendorStatusEnum(str, Enum):
    none = "none"
    ad_hoc = "ad_hoc"
    established = "established"
    unhappy = "unhappy"


class GrowthAmbitionEnum(str, Enum):
    high = "high"
    moderate = "moderate"
    maintenance = "maintenance"


class TriggerCategoryEnum(str, Enum):
    new_contract = "new_contract"
    rebranding = "rebranding"
    system_failure = "system_failure"
    competitor_move = "competitor_move"
    new_hire = "new_hire"
    upcoming_event = "upcoming_event"
    growth_pressure = "growth_pressure"
    vendor_dissatisfaction = "vendor_dissatisfaction"
    referral = "referral"
    other = "other"


class DimensionEnum(str, Enum):
    competitive_awareness = "competitive_awareness"
    brand_gap = "brand_gap"
    is_maturity = "is_maturity"
    cost_of_status_quo = "cost_of_status_quo"
    solution_routing = "solution_routing"


class UserRoleEnum(str, Enum):
    rep = "rep"
    domain_expert = "domain_expert"
    manager = "manager"
    admin = "admin"


class PainIntensityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class PainCategoryEnum(str, Enum):
    brand_presentation = "brand_presentation"
    apparel_quality = "apparel_quality"
    print_collateral = "print_collateral"
    digital_presence = "digital_presence"
    web_infrastructure = "web_infrastructure"
    email_infrastructure = "email_infrastructure"
    business_management = "business_management"
    erp_crm = "erp_crm"
    network_infrastructure = "network_infrastructure"
    it_security = "it_security"
    software_custom = "software_custom"
    operational_friction = "operational_friction"
    competitive_pressure = "competitive_pressure"
    vendor_failure = "vendor_failure"
    cost_of_status_quo = "cost_of_status_quo"
    scalability = "scalability"
    reputation_risk = "reputation_risk"
    team_consistency = "team_consistency"
    other = "other"


# ─── Auth Schemas ─────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─── User Schemas ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    role: UserRoleEnum
    specialization: Optional[str] = None


class UserResponse(BaseModel):
    user_id: UUID
    full_name: str
    email: str
    role: str
    specialization: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


# ─── Prospect Schemas ─────────────────────────────────────────────────────────

class ProspectCreate(BaseModel):
    company_name: str
    contact_name: str
    contact_role: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    industry: Optional[str] = None
    business_type: BusinessTypeEnum
    size_tier: SizeTierEnum
    growth_stage: GrowthStageEnum
    geographic_scope: GeoScopeEnum
    vendor_status: VendorStatusEnum
    growth_ambition: GrowthAmbitionEnum
    headcount: Optional[int] = None
    revenue_range: Optional[str] = None


class ProspectResponse(BaseModel):
    prospect_id: UUID
    company_name: str
    contact_name: str
    contact_role: Optional[str]
    contact_email: Optional[str]
    business_type: Optional[str]
    size_tier: Optional[str]
    growth_stage: Optional[str]
    erp_lead_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Business Profile Schemas ─────────────────────────────────────────────────

class BusinessProfileCreate(BaseModel):
    trigger_event: Optional[str] = None
    trigger_category: Optional[TriggerCategoryEnum] = None
    primary_trigger_dimension: Optional[DimensionEnum] = None
    current_vendors: Optional[Dict[str, Any]] = None
    vendor_pain_notes: Optional[str] = None
    competitive_context: Optional[str] = None
    strategic_priorities: Optional[str] = None
    additional_context: Optional[str] = None


class BusinessProfileUpdate(BaseModel):
    trigger_event: Optional[str] = None
    trigger_category: Optional[TriggerCategoryEnum] = None
    primary_trigger_dimension: Optional[DimensionEnum] = None
    current_vendors: Optional[Dict[str, Any]] = None
    vendor_pain_notes: Optional[str] = None
    competitive_context: Optional[str] = None
    strategic_priorities: Optional[str] = None
    additional_context: Optional[str] = None


class BusinessProfileResponse(BaseModel):
    profile_id: UUID
    trigger_event: Optional[str]
    trigger_category: Optional[str]
    primary_trigger_dimension: Optional[str]
    current_vendors: Optional[Dict]
    competitive_context: Optional[str]
    captured_at: datetime

    class Config:
        from_attributes = True


# ─── Session Schemas ──────────────────────────────────────────────────────────

class SessionCreate(BaseModel):
    prospect: ProspectCreate
    business_profile: BusinessProfileCreate


class SessionResponse(BaseModel):
    session_id: UUID
    prospect_id: UUID
    status: str
    overall_score: Optional[float] = 0
    created_at: datetime


class SessionDetail(BaseModel):
    session_id: UUID
    prospect: ProspectResponse
    business_profile: Optional[BusinessProfileResponse]
    overall_score: Optional[float]
    session_status: str
    dimension_scores: List[Dict[str, Any]] = []
    created_at: datetime

    class Config:
        from_attributes = True


class AutoSavePayload(BaseModel):
    field: str
    value: Any
    context: Optional[str] = None  # e.g. "dimension:competitive_awareness"


# ─── Scoring Schemas ──────────────────────────────────────────────────────────

class SignalScoreUpdate(BaseModel):
    dimension: DimensionEnum
    signal_name: str
    score: int
    notes: Optional[str] = None

    @field_validator("score")
    @classmethod
    def score_must_be_valid(cls, v):
        if v not in [0, 1, 2]:
            raise ValueError("Score must be 0, 1, or 2")
        return v


class SignalScoreResponse(BaseModel):
    signal_name: str
    score: int
    max_score: int = 2
    notes: Optional[str]


class DimensionScoreResponse(BaseModel):
    dimension: str
    achieved_score: float
    max_score: int
    score_percentage: float
    tier: Optional[str]
    tier_label: Optional[str]
    system_trigger: Optional[str]
    trigger_deployed: bool
    signals: List[SignalScoreResponse] = []


class OverallScoreResponse(BaseModel):
    overall_score: float
    max_possible_score: int = 50
    score_percentage: float
    qualification_grade: str
    dimension_scores: List[DimensionScoreResponse] = []


# ─── Pain Flag Schemas ────────────────────────────────────────────────────────

class PainFlagCreate(BaseModel):
    dimension: DimensionEnum
    pain_category: PainCategoryEnum
    pain_intensity: PainIntensityEnum
    pain_description: str
    prospect_quoted: Optional[str] = None
    quantified_cost: Optional[float] = None
    quantified_unit: Optional[str] = None
    quantification_notes: Optional[str] = None


class PainFlagResponse(BaseModel):
    pain_flag_id: UUID
    dimension: str
    pain_category: str
    pain_intensity: str
    pain_description: str
    prospect_quoted: Optional[str]
    quantified_cost: Optional[float]
    status: str
    flagged_at: datetime

    class Config:
        from_attributes = True


# ─── Note Schemas ─────────────────────────────────────────────────────────────

class NoteCreate(BaseModel):
    note_type: str
    note_content: str
    is_pinned: bool = False
    interaction_id: Optional[UUID] = None


class NoteResponse(BaseModel):
    note_id: UUID
    note_type: str
    note_content: str
    is_pinned: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Framework Content Schemas ────────────────────────────────────────────────

class FrameworkDimensionResponse(BaseModel):
    dimension_id: UUID
    dimension_name: str
    dimension_label: str
    max_score: int
    opening_question: Optional[str]
    positioning_moment: Optional[str]
    tier_thresholds: Optional[Dict]
    signals: List[Dict] = []
    probes: List[Dict] = []
    reframes: List[Dict] = []
    framework_version: str

    class Config:
        from_attributes = True
