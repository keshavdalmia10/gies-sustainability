"""
Networking Schemas
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID

class SkillBase(BaseModel):
    name: str

class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    skill_id: UUID
    
    class Config:
        from_attributes = True

class InterestBase(BaseModel):
    name: str

class InterestCreate(InterestBase):
    pass

class Interest(InterestBase):
    interest_id: UUID
    
    class Config:
        from_attributes = True

class StudentBase(BaseModel):
    name: str
    email: str
    major: Optional[str] = None
    year: Optional[str] = None
    bio: Optional[str] = None

class StudentCreate(StudentBase):
    skills: List[str] = []
    interests: List[str] = []

class Student(StudentBase):
    student_id: UUID
    skills: List[Skill] = []
    interests: List[Interest] = []
    
    class Config:
        from_attributes = True

class FacultyProfileUpdate(BaseModel):
    person_uuid: UUID
    skills: List[str] = []
    interests: List[str] = []

class GraphNode(BaseModel):
    id: str
    label: str
    type: str # 'student', 'faculty', 'skill', 'interest'
    group: int

class GraphEdge(BaseModel):
    source: str
    target: str
    value: int = 1

class NetworkGraph(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class ChatAnalysisRequest(BaseModel):
    query: str
    user_id: Optional[str] = None # Optional context

class ChatAnalysisResponse(BaseModel):
    response: str
    suggested_connections: List[GraphNode] = []
    graph_data: Optional[Dict[str, Any]] = None
