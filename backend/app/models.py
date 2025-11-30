"""
SQLAlchemy ORM Models
"""
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, Date, DateTime, 
    ForeignKey, ARRAY, CheckConstraint, DECIMAL, JSON
)
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Faculty(Base):
    __tablename__ = "faculty"
    
    person_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    department = Column(String(255))
    active = Column(Boolean, default=True)
    profile_url = Column(Text)
    photo_url = Column(Text)
    research_interests = Column(ARRAY(Text))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    publications = relationship("Publication", back_populates="faculty", cascade="all, delete-orphan")
    impact_cards = relationship("ImpactCard", back_populates="faculty", cascade="all, delete-orphan")
    feedback = relationship("FacultyFeedback", back_populates="faculty")
    
    # Extended relationships
    courses = relationship("CourseCurriculum", back_populates="instructor")
    advised_projects = relationship("StudentProject", back_populates="advisor")
    partnerships = relationship("CorporatePartnership", back_populates="faculty_lead")


class Publication(Base):
    __tablename__ = "publications"
    
    article_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_uuid = Column(UUID(as_uuid=True), ForeignKey("faculty.person_uuid", ondelete="CASCADE"))
    title = Column(Text, nullable=False)
    abstract = Column(Text)
    publication_year = Column(Integer)
    doi = Column(String(255))
    journal_title = Column(String(255))
    journal_issn = Column(String(50))
    keywords = Column(ARRAY(Text))
    is_sustain = Column(Boolean, default=False)
    sdg_top1 = Column(Integer, CheckConstraint('sdg_top1 BETWEEN 1 AND 17'))
    sdg_top2 = Column(Integer, CheckConstraint('sdg_top2 BETWEEN 1 AND 17'))
    sdg_top3 = Column(Integer, CheckConstraint('sdg_top3 BETWEEN 1 AND 17'))
    sdg_confidence = Column(Float, CheckConstraint('sdg_confidence BETWEEN 0 AND 1'))
    citation_count = Column(Integer, default=0)
    source = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    faculty = relationship("Faculty", back_populates="publications")
    impact_links = relationship("PublicationImpactLink", back_populates="publication", cascade="all, delete-orphan")


class Impact(Base):
    __tablename__ = "impacts"
    
    impact_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    impact_type = Column(String(50), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    sdg_primary = Column(Integer, CheckConstraint('sdg_primary BETWEEN 1 AND 17'))
    sdg_secondary = Column(ARRAY(Integer))
    geography = Column(String(255))
    beneficiaries_count = Column(Integer)
    funding_amount = Column(DECIMAL(15, 2))
    status = Column(String(50))
    start_date = Column(Date)
    end_date = Column(Date)
    outcomes = Column(JSONB)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    publication_links = relationship("PublicationImpactLink", back_populates="impact", cascade="all, delete-orphan")


class Grant(Base):
    __tablename__ = "grants"
    
    grant_id = Column(UUID(as_uuid=True), ForeignKey("impacts.impact_id", ondelete="CASCADE"), primary_key=True)
    external_id = Column(String(255))
    funder = Column(String(255), nullable=False)
    funder_division = Column(String(255))
    program = Column(String(255))
    pi_uuid = Column(UUID(as_uuid=True), ForeignKey("faculty.person_uuid"))
    co_investigators = Column(ARRAY(UUID))
    keywords = Column(ARRAY(Text))
    abstract = Column(Text)
    award_notice_date = Column(Date)


class Patent(Base):
    __tablename__ = "patents"
    
    patent_id = Column(UUID(as_uuid=True), ForeignKey("impacts.impact_id", ondelete="CASCADE"), primary_key=True)
    patent_number = Column(String(50), unique=True, nullable=False)
    inventors = Column(ARRAY(UUID))
    assignee = Column(String(255))
    classification_codes = Column(ARRAY(String(50)))
    citations_count = Column(Integer, default=0)
    grant_date = Column(Date)
    filing_date = Column(Date)
    patent_office = Column(String(50), default='USPTO')


class Policy(Base):
    __tablename__ = "policies"
    
    policy_id = Column(UUID(as_uuid=True), ForeignKey("impacts.impact_id", ondelete="CASCADE"), primary_key=True)
    agency = Column(String(255), nullable=False)
    document_type = Column(String(100))
    document_url = Column(Text)
    mention_type = Column(String(50))
    mentioned_faculty = Column(ARRAY(UUID))
    publication_date = Column(Date)
    effective_date = Column(Date)


class PublicationImpactLink(Base):
    __tablename__ = "publication_impact_links"
    
    link_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    publication_uuid = Column(UUID(as_uuid=True), ForeignKey("publications.article_uuid", ondelete="CASCADE"))
    impact_id = Column(UUID(as_uuid=True), ForeignKey("impacts.impact_id", ondelete="CASCADE"))
    confidence_score = Column(Float, CheckConstraint('confidence_score BETWEEN 0 AND 1'))
    method = Column(String(100))
    validated_by = Column(String(255))
    is_validated = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    publication = relationship("Publication", back_populates="impact_links")
    impact = relationship("Impact", back_populates="publication_links")


class FacultyImpactLink(Base):
    __tablename__ = "faculty_impact_links"
    
    link_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_uuid = Column(UUID(as_uuid=True), ForeignKey("faculty.person_uuid", ondelete="CASCADE"))
    impact_id = Column(UUID(as_uuid=True), ForeignKey("impacts.impact_id", ondelete="CASCADE"))
    role = Column(String(100))
    contribution_percentage = Column(Integer, CheckConstraint('contribution_percentage BETWEEN 0 AND 100'))
    created_at = Column(DateTime, server_default=func.now())


class GroundTruthSet(Base):
    __tablename__ = "ground_truth_set"
    
    gt_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    publication_uuid = Column(UUID(as_uuid=True), ForeignKey("publications.article_uuid"))
    impact_id = Column(UUID(as_uuid=True), ForeignKey("impacts.impact_id"))
    is_true_link = Column(Boolean, nullable=False)
    sdg = Column(Integer, CheckConstraint('sdg BETWEEN 1 AND 17'))
    validated_by = Column(String(255), nullable=False)
    validated_at = Column(DateTime, server_default=func.now())
    validation_method = Column(String(100))
    notes = Column(Text)


class ModelEvaluation(Base):
    __tablename__ = "model_evaluations"
    
    eval_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_version = Column(String(100), nullable=False)
    model_type = Column(String(50))
    sdg = Column(Integer, CheckConstraint('sdg BETWEEN 1 AND 17'))
    precision_at_k = Column(Float)
    recall_at_k = Column(Float)
    f1_at_k = Column(Float)
    k = Column(Integer)
    evaluation_date = Column(DateTime, server_default=func.now())
    test_set_size = Column(Integer)
    parameters = Column(JSONB)
    notes = Column(Text)


class FacultyFeedback(Base):
    __tablename__ = "faculty_feedback"
    
    feedback_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_uuid = Column(UUID(as_uuid=True), ForeignKey("faculty.person_uuid"))
    feedback_type = Column(String(50), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(UUID(as_uuid=True))
    original_value = Column(Text)
    suggested_value = Column(Text)
    comments = Column(Text)
    status = Column(String(50), default='pending')
    reviewed_by = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime)
    
    # Relationships
    faculty = relationship("Faculty", back_populates="feedback")


class DataRetentionPolicy(Base):
    __tablename__ = "data_retention_policies"
    
    policy_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False)
    retention_days = Column(Integer, nullable=False)
    description = Column(Text)
    last_purge_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255))
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(UUID(as_uuid=True))
    changes = Column(JSONB)
    ip_address = Column(INET)
    created_at = Column(DateTime, server_default=func.now())


class ImpactCard(Base):
    __tablename__ = "impact_cards"
    
    card_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_uuid = Column(UUID(as_uuid=True), ForeignKey("faculty.person_uuid", ondelete="CASCADE"))
    sdg = Column(Integer, CheckConstraint('sdg BETWEEN 1 AND 17'), nullable=False)
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=False)
    narrative = Column(Text)
    publications = Column(ARRAY(UUID))
    impacts = Column(ARRAY(UUID))
    key_outcomes = Column(ARRAY(Text))
    geography = Column(String(255))
    total_funding = Column(DECIMAL(15, 2))
    communities_reached = Column(Integer)
    start_year = Column(Integer)
    end_year = Column(Integer)
    funding_gap = Column(DECIMAL(15, 2))
    next_milestones = Column(ARRAY(Text))
    status = Column(String(50), default='draft')
    validated_by = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    faculty = relationship("Faculty", back_populates="impact_cards")


class SDGGoal(Base):
    __tablename__ = "sdg_goals"
    
    sdg_number = Column(Integer, CheckConstraint('sdg_number BETWEEN 1 AND 17'), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    color_hex = Column(String(7))
    icon_url = Column(Text)
    keywords = Column(ARRAY(Text))


class ImpactValidation(Base):
    __tablename__ = "impact_validations"
    
    validation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_id = Column(UUID(as_uuid=True), ForeignKey("impact_cards.card_id", ondelete="CASCADE"))
    visitor_id = Column(String(255))  # Anonymous tracking ID
    status = Column(String(50), nullable=False)  # 'approved', 'rejected'
    timestamp = Column(DateTime, server_default=func.now())
