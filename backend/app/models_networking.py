"""
Networking Models
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

# Association Tables
student_skills = Table(
    'student_skills', Base.metadata,
    Column('student_id', UUID(as_uuid=True), ForeignKey('students.student_id')),
    Column('skill_id', UUID(as_uuid=True), ForeignKey('skills.skill_id'))
)

faculty_skills = Table(
    'faculty_skills', Base.metadata,
    Column('person_uuid', UUID(as_uuid=True), ForeignKey('faculty.person_uuid')),
    Column('skill_id', UUID(as_uuid=True), ForeignKey('skills.skill_id'))
)

student_interests = Table(
    'student_interests', Base.metadata,
    Column('student_id', UUID(as_uuid=True), ForeignKey('students.student_id')),
    Column('interest_id', UUID(as_uuid=True), ForeignKey('interests.interest_id'))
)

faculty_interests = Table(
    'faculty_interests', Base.metadata,
    Column('person_uuid', UUID(as_uuid=True), ForeignKey('faculty.person_uuid')),
    Column('interest_id', UUID(as_uuid=True), ForeignKey('interests.interest_id'))
)

class Student(Base):
    __tablename__ = "students"
    
    student_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    major = Column(String(255))
    year = Column(String(50)) # Freshman, Sophomore, etc.
    bio = Column(Text)
    
    # Relationships
    skills = relationship("Skill", secondary=student_skills, back_populates="students")
    interests = relationship("Interest", secondary=student_interests, back_populates="students")

class Skill(Base):
    __tablename__ = "skills"
    
    skill_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    
    # Relationships
    students = relationship("Student", secondary=student_skills, back_populates="skills")
    faculty = relationship("Faculty", secondary=faculty_skills, back_populates="skills")

class Interest(Base):
    __tablename__ = "interests"
    
    interest_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    
    # Relationships
    students = relationship("Student", secondary=student_interests, back_populates="interests")
    faculty = relationship("Faculty", secondary=faculty_interests, back_populates="interests")

# Add relationships to Faculty model (monkey-patching for now, or should be added to models.py)
# Ideally, we should update models.py, but to avoid circular imports or modifying existing large files too much, 
# we can define the other side of the relationship here if we import Faculty.
# However, SQLAlchemy usually handles string references well.
# We need to make sure Faculty model has these relationships defined or we use back_populates carefully.
# The 'faculty' relationship in Skill and Interest uses back_populates="skills" and "interests".
# So we need to add 'skills' and 'interests' to Faculty model.
