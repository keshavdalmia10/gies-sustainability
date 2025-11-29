"""
Extended ORM models for additional data types

Course curricula, student projects, corporate partnerships, and policy enhancements
"""

from sqlalchemy import Column, String, Integer, Text, Date, Boolean, DECIMAL, ARRAY, JSON
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .models import Base


class CourseCurriculum(Base):
    """Course with sustainability focus"""
    __tablename__ = "course_curricula"
    
    course_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_code = Column(String(20), nullable=False)
    course_name = Column(String(255), nullable=False)
    instructor_uuid = Column(UUID(as_uuid=True), ForeignKey("faculty.person_uuid"))
    department = Column(String(100))
    semester = Column(String(20))
    year = Column(Integer)
    sdg_primary = Column(Integer, ForeignKey("sdg_goals.sdg_number"))
    sdg_secondary = Column(ARRAY(Integer))
    description = Column(Text)
    syllabus_url = Column(String(500))
    sustainability_topics = Column(ARRAY(Text))
    learning_outcomes = Column(ARRAY(Text))
    enrollment_count = Column(Integer)
    student_projects_count = Column(Integer, default=0)
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    instructor = relationship("Faculty", back_populates="courses")
    student_projects = relationship("StudentProject", back_populates="course")


class StudentProject(Base):
    """Student sustainability project"""
    __tablename__ = "student_projects"
    
    project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_title = Column(String(500), nullable=False)
    project_type = Column(String(50))  # capstone, thesis, research, competition
    course_id = Column(UUID(as_uuid=True), ForeignKey("course_curricula.course_id"))
    advisor_uuid = Column(UUID(as_uuid=True), ForeignKey("faculty.person_uuid"))
    student_names = Column(ARRAY(Text))
    sdg_primary = Column(Integer, ForeignKey("sdg_goals.sdg_number"))
    sdg_secondary = Column(ARRAY(Integer))
    description = Column(Text)
    abstract = Column(Text)
    outcomes = Column(Text)
    award_received = Column(String(255))
    presentation_date = Column(Date)
    project_year = Column(Integer)
    repository_url = Column(String(500))
    publication_resulted = Column(Boolean, default=False)
    community_partner = Column(String(255))
    impact_metrics = Column(JSONB)
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship("CourseCurriculum", back_populates="student_projects")
    advisor = relationship("Faculty", back_populates="advised_projects")


class CorporatePartnership(Base):
    """Corporate sustainability partnership"""
    __tablename__ = "corporate_partnerships"
    
    partnership_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partnership_name = Column(String(255), nullable=False)
    corporate_partner = Column(String(255), nullable=False)
    faculty_lead_uuid = Column(UUID(as_uuid=True), ForeignKey("faculty.person_uuid"))
    partnership_type = Column(String(100))  # research, sponsorship, internship, consulting
    sdg_primary = Column(Integer, ForeignKey("sdg_goals.sdg_number"))
    sdg_secondary = Column(ARRAY(Integer))
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    funding_amount = Column(DECIMAL(15, 2))
    deliverables = Column(ARRAY(Text))
    outcomes = Column(Text)
    student_participants_count = Column(Integer)
    publications_count = Column(Integer, default=0)
    patents_count = Column(Integer, default=0)
    industry_sector = Column(String(100))
    geography = Column(String(100))
    status = Column(String(50))  # active, completed, pending
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    faculty_lead = relationship("Faculty", back_populates="partnerships")


# Link tables

class CoursePublicationLink(Base):
    """Links courses to resulting publications"""
    __tablename__ = "course_publication_links"
    
    link_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("course_curricula.course_id", ondelete="CASCADE"))
    publication_uuid = Column(UUID(as_uuid=True), ForeignKey("publications.article_uuid", ondelete="CASCADE"))
    created_at = Column(Date, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('course_id', 'publication_uuid', name='_course_publication_uc'),
    )


class PartnershipPublicationLink(Base):
    """Links partnerships to resulting publications"""
    __tablename__ = "partnership_publication_links"
    
    link_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partnership_id = Column(UUID(as_uuid=True), ForeignKey("corporate_partnerships.partnership_id", ondelete="CASCADE"))
    publication_uuid = Column(UUID(as_uuid=True), ForeignKey("publications.article_uuid", ondelete="CASCADE"))
    created_at = Column(Date, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('partnership_id', 'publication_uuid', name='_partnership_publication_uc'),
    )


class ProjectImpactLink(Base):
    """Links student projects to broader impacts"""
    __tablename__ = "project_impact_links"
    
    link_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("student_projects.project_id", ondelete="CASCADE"))
    impact_id = Column(UUID(as_uuid=True), ForeignKey("impacts.impact_id", ondelete="CASCADE"))
    created_at = Column(Date, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('project_id', 'impact_id', name='_project_impact_uc'),
    )


# Update Faculty model to add new relationships (add these to existing models.py)
"""
Add to Faculty class in models.py:

courses = relationship("CourseCurriculum", back_populates="instructor")
advised_projects = relationship("StudentProject", back_populates="advisor")
partnerships = relationship("CorporatePartnership", back_populates="faculty_lead")
"""
