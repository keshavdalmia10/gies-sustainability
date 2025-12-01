"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


# ============================================================================
# Faculty Schemas
# ============================================================================

class FacultyBase(BaseModel):
    name: str
    email: Optional[str] = None
    department: Optional[str] = None
    active: bool = True
    profile_url: Optional[str] = None
    photo_url: Optional[str] = None
    research_interests: Optional[List[str]] = []
    current_work: Optional[str] = None


class FacultyCreate(FacultyBase):
    pass


class FacultyUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    active: Optional[bool] = None
    profile_url: Optional[str] = None
    photo_url: Optional[str] = None
    research_interests: Optional[List[str]] = None
    current_work: Optional[str] = None


class Faculty(FacultyBase):
    person_uuid: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FacultyWithStats(Faculty):
    publication_count: int = 0
    sustainable_pub_count: int = 0
    total_grant_funding: Decimal = Decimal(0)
    patent_count: int = 0


# ============================================================================
# Publication Schemas
# ============================================================================

class PublicationBase(BaseModel):
    title: str
    abstract: Optional[str] = None
    publication_year: Optional[int] = None
    doi: Optional[str] = None
    journal_title: Optional[str] = None
    journal_issn: Optional[str] = None
    keywords: Optional[List[str]] = []
    is_sustain: bool = False
    sdg_top1: Optional[int] = Field(None, ge=1, le=17)
    sdg_top2: Optional[int] = Field(None, ge=1, le=17)
    sdg_top3: Optional[int] = Field(None, ge=1, le=17)
    sdg_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    citation_count: int = 0
    source: Optional[str] = None


class PublicationCreate(PublicationBase):
    person_uuid: UUID


class Publication(PublicationBase):
    article_uuid: UUID
    person_uuid: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Impact Schemas
# ============================================================================

class ImpactBase(BaseModel):
    impact_type: str
    title: str
    description: Optional[str] = None
    sdg_primary: Optional[int] = Field(None, ge=1, le=17)
    sdg_secondary: Optional[List[int]] = []
    geography: Optional[str] = None
    beneficiaries_count: Optional[int] = None
    funding_amount: Optional[Decimal] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    outcomes: Optional[Dict[str, Any]] = {}


class ImpactCreate(ImpactBase):
    pass


class Impact(ImpactBase):
    impact_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GrantCreate(ImpactCreate):
    external_id: Optional[str] = None
    funder: str
    funder_division: Optional[str] = None
    program: Optional[str] = None
    pi_uuid: Optional[UUID] = None
    co_investigators: Optional[List[UUID]] = []
    keywords: Optional[List[str]] = []
    abstract: Optional[str] = None
    award_notice_date: Optional[date] = None


class Grant(Impact):
    grant_id: UUID
    external_id: Optional[str]
    funder: str
    program: Optional[str]
    
    class Config:
        from_attributes = True


class PatentCreate(ImpactCreate):
    patent_number: str
    inventors: Optional[List[UUID]] = []
    assignee: Optional[str] = None
    classification_codes: Optional[List[str]] = []
    citations_count: int = 0
    grant_date: Optional[date] = None
    filing_date: Optional[date] = None


class Patent(Impact):
    patent_id: UUID
    patent_number: str
    inventors: Optional[List[UUID]]
    assignee: Optional[str]
    
    class Config:
        from_attributes = True


# ============================================================================
# Impact Card Schemas
# ============================================================================

class ImpactCardBase(BaseModel):
    sdg: int = Field(..., ge=1, le=17)
    title: str
    summary: str
    narrative: Optional[str] = None
    publications: Optional[List[UUID]] = []
    impacts: Optional[List[UUID]] = []
    key_outcomes: Optional[List[str]] = []
    geography: Optional[str] = None
    total_funding: Optional[Decimal] = None
    communities_reached: Optional[int] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    funding_gap: Optional[Decimal] = None
    next_milestones: Optional[List[str]] = []


class ImpactCardCreate(ImpactCardBase):
    person_uuid: UUID


class ImpactCardUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    narrative: Optional[str] = None
    key_outcomes: Optional[List[str]] = None
    geography: Optional[str] = None
    total_funding: Optional[Decimal] = None
    communities_reached: Optional[int] = None
    funding_gap: Optional[Decimal] = None
    next_milestones: Optional[List[str]] = None
    status: Optional[str] = None


class ImpactCard(ImpactCardBase):
    card_id: UUID
    person_uuid: UUID
    status: str
    validated_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ImpactCardDetailed(ImpactCard):
    """Impact card with full nested data"""
    faculty_name: str
    faculty_department: str
    sdg_title: str
    sdg_color: str
    publication_details: List[Publication] = []
    impact_details: List[Impact] = []


# ============================================================================
# Link Schemas
# ============================================================================

class PublicationImpactLinkCreate(BaseModel):
    publication_uuid: UUID
    impact_id: UUID
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    method: str
    validated_by: Optional[str] = None
    is_validated: bool = False


class PublicationImpactLink(PublicationImpactLinkCreate):
    link_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Evaluation Schemas
# ============================================================================

class ModelEvaluationCreate(BaseModel):
    model_version: str
    model_type: str
    sdg: Optional[int] = Field(None, ge=1, le=17)
    precision_at_k: float
    recall_at_k: Optional[float] = None
    f1_at_k: Optional[float] = None
    k: int
    test_set_size: int
    parameters: Optional[Dict[str, Any]] = {}
    notes: Optional[str] = None


class ModelEvaluation(ModelEvaluationCreate):
    eval_id: UUID
    evaluation_date: datetime
    
    class Config:
        from_attributes = True


class GroundTruthCreate(BaseModel):
    publication_uuid: UUID
    impact_id: UUID
    is_true_link: bool
    sdg: int = Field(..., ge=1, le=17)
    validated_by: str
    validation_method: Optional[str] = None
    notes: Optional[str] = None


# ============================================================================
# Feedback Schemas
# ============================================================================

class FacultyFeedbackCreate(BaseModel):
    person_uuid: UUID
    feedback_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    original_value: Optional[str] = None
    suggested_value: Optional[str] = None
    comments: Optional[str] = None


class FacultyFeedback(FacultyFeedbackCreate):
    feedback_id: UUID
    status: str
    reviewed_by: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============================================================================
# SDG Schemas
# ============================================================================

class SDGGoal(BaseModel):
    sdg_number: int
    title: str
    description: Optional[str]
    color_hex: Optional[str]
    icon_url: Optional[str]
    keywords: Optional[List[str]]
    
    class Config:
        from_attributes = True


# ============================================================================
# Query/Filter Schemas
# ============================================================================

class ImpactCardFilter(BaseModel):
    sdg: Optional[int] = Field(None, ge=1, le=17)
    department: Optional[str] = None
    status: Optional[str] = None
    min_funding: Optional[Decimal] = None
    geography: Optional[str] = None


class PublicationFilter(BaseModel):
    sdg: Optional[int] = Field(None, ge=1, le=17)
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    is_sustain: Optional[bool] = None
    department: Optional[str] = None


# ============================================================================
# Response Schemas
# ============================================================================

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class DashboardStats(BaseModel):
    total_faculty: int
    total_publications: int
    sustainable_publications: int
    total_funding: Decimal
    total_patents: int
    total_impact_cards: int
    by_sdg: Dict[int, Dict[str, Any]]


class DecisionSupportData(BaseModel):
    """Data for dean/provost decision dashboard"""
    sdg_matrix: List[Dict[str, Any]]
    momentum_indicators: List[Dict[str, Any]]
    gap_analysis: List[Dict[str, Any]]
    flagship_projects: List[ImpactCard]


class DonorViewData(BaseModel):
    """Data for donor view"""
    impact_cards: List[ImpactCardDetailed]
    total_funding_opportunities: Decimal
    communities_reached: int
    sdg_breakdown: Dict[int, int]


class ImpactValidationCreate(BaseModel):
    visitor_id: str
    status: str = Field(..., pattern="^(approved|rejected)$")


class ImpactValidationResponse(BaseModel):
    validation_id: UUID
    card_id: UUID
    status: str
    timestamp: datetime
    
    class Config:
        from_attributes = True
