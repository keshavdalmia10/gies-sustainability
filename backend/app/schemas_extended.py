"""
Pydantic schemas for extended data types
"""

from pydantic import BaseModel, UUID4
from typing import List, Optional, Dict
from datetime import date
from decimal import Decimal


# Course Curricula Schemas

class CourseCurriculumBase(BaseModel):
    course_code: str
    course_name: str
    instructor_uuid: Optional[UUID4] = None
    department: Optional[str] = None
    semester: Optional[str] = None
    year: Optional[int] = None
    sdg_primary: Optional[int] = None
    sdg_secondary: Optional[List[int]] = None
    description: Optional[str] = None
    syllabus_url: Optional[str] = None
    sustainability_topics: Optional[List[str]] = None
    learning_outcomes: Optional[List[str]] = None
    enrollment_count: Optional[int] = None


class CourseCurriculumCreate(CourseCurriculumBase):
    pass


class CourseCurriculum(CourseCurriculumBase):
    course_id: UUID4
    student_projects_count: int = 0
    created_at: date
    
    class Config:
        from_attributes = True


# Student Project Schemas

class StudentProjectBase(BaseModel):
    project_title: str
    project_type: Optional[str] = None  # capstone, thesis, research, competition
    course_id: Optional[UUID4] = None
    advisor_uuid: Optional[UUID4] = None
    student_names: Optional[List[str]] = None
    sdg_primary: Optional[int] = None
    sdg_secondary: Optional[List[int]] = None
    description: Optional[str] = None
    abstract: Optional[str] = None
    outcomes: Optional[str] = None
    award_received: Optional[str] = None
    presentation_date: Optional[date] = None
    project_year: Optional[int] = None
    repository_url: Optional[str] = None
    publication_resulted: bool = False
    community_partner: Optional[str] = None
    impact_metrics: Optional[Dict] = None


class StudentProjectCreate(StudentProjectBase):
    pass


class StudentProject(StudentProjectBase):
    project_id: UUID4
    created_at: date
    
    class Config:
        from_attributes = True


# Corporate Partnership Schemas

class CorporatePartnershipBase(BaseModel):
    partnership_name: str
    corporate_partner: str
    faculty_lead_uuid: Optional[UUID4] = None
    partnership_type: Optional[str] = None  # research, sponsorship, internship, consulting
    sdg_primary: Optional[int] = None
    sdg_secondary: Optional[List[int]] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    funding_amount: Optional[Decimal] = None
    deliverables: Optional[List[str]] = None
    outcomes: Optional[str] = None
    student_participants_count: Optional[int] = None
    publications_count: int = 0
    patents_count: int = 0
    industry_sector: Optional[str] = None
    geography: Optional[str] = None
    status: str = "active"  # active, completed, pending


class CorporatePartnershipCreate(CorporatePartnershipBase):
    pass


class CorporatePartnership(CorporatePartnershipBase):
    partnership_id: UUID4
    created_at: date
    
    class Config:
        from_attributes = True


# Enhanced Policy Schema (extends existing)

class PolicyEnhanced(BaseModel):
    """Enhanced policy with additional metadata"""
    policy_id: UUID4
    title: str
    description: Optional[str] = None
    policy_type: Optional[str] = None  # federal, state, local, international
    jurisdiction: Optional[str] = None
    policy_url: Optional[str] = None
    faculty_contributor_uuids: Optional[List[UUID4]] = None
    implementation_status: Optional[str] = None  # proposed, enacted, implemented
    policy_impact_description: Optional[str] = None
    citations_count: int = 0
    media_coverage: Optional[List[str]] = None
    sdg_primary: Optional[int] = None
    
    class Config:
        from_attributes = True


# Link Schemas

class CoursePublicationLinkCreate(BaseModel):
    course_id: UUID4
    publication_uuid: UUID4


class PartnershipPublicationLinkCreate(BaseModel):
    partnership_id: UUID4
    publication_uuid: UUID4


class ProjectImpactLinkCreate(BaseModel):
    project_id: UUID4
    impact_id: UUID4


# Summary Schemas

class SustainabilityTeachingSummary(BaseModel):
    """Faculty sustainability teaching summary"""
    person_uuid: UUID4
    name: str
    department: Optional[str]
    sustainability_courses_count: int
    sdgs_taught: List[int]
    total_students_reached: int
    total_student_projects: int


class PartnershipPortfolio(BaseModel):
    """Partnership portfolio by SDG"""
    sdg_number: int
    sdg_title: str
    partnership_count: int
    total_funding: Decimal
    partners: List[str]


class StudentImpactStat(BaseModel):
    """Student impact statistics"""
    project_year: int
    sdg_primary: Optional[int]
    project_count: int
    faculty_advisors: int
    publications_resulted: int
    community_partners: int
