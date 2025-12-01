from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any
import networkx as nx
from app.database import get_db
from app import models, models_networking, schemas_networking
from uuid import UUID

router = APIRouter()

@router.post("/student", response_model=schemas_networking.Student)
async def create_student_profile(student: schemas_networking.StudentCreate, db: AsyncSession = Depends(get_db)):
    # Check if email exists
    result = await db.execute(select(models_networking.Student).where(models_networking.Student.email == student.email))
    db_student = result.scalar_one_or_none()
    if db_student:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_student = models_networking.Student(
        name=student.name,
        email=student.email,
        major=student.major,
        year=student.year,
        bio=student.bio
    )
    db.add(new_student)
    
    # Add skills
    for skill_name in student.skills:
        result = await db.execute(select(models_networking.Skill).where(models_networking.Skill.name == skill_name))
        skill = result.scalar_one_or_none()
        if not skill:
            skill = models_networking.Skill(name=skill_name)
            db.add(skill)
        new_student.skills.append(skill)
        
    # Add interests
    for interest_name in student.interests:
        result = await db.execute(select(models_networking.Interest).where(models_networking.Interest.name == interest_name))
        interest = result.scalar_one_or_none()
        if not interest:
            interest = models_networking.Interest(name=interest_name)
            db.add(interest)
        new_student.interests.append(interest)
        
    await db.commit()
    await db.refresh(new_student)
    
    # Re-fetch with relationships for response
    result = await db.execute(
        select(models_networking.Student)
        .options(selectinload(models_networking.Student.skills), selectinload(models_networking.Student.interests))
        .where(models_networking.Student.student_id == new_student.student_id)
    )
    return result.scalar_one()

@router.post("/faculty/{person_uuid}/skills", response_model=schemas_networking.FacultyProfileUpdate)
async def update_faculty_skills(person_uuid: UUID, skills: List[str], db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Faculty)
        .options(selectinload(models.Faculty.skills), selectinload(models.Faculty.interests))
        .where(models.Faculty.person_uuid == person_uuid)
    )
    faculty = result.scalar_one_or_none()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
        
    current_skills = {s.name for s in faculty.skills}
    
    for skill_name in skills:
        if skill_name not in current_skills:
            result = await db.execute(select(models_networking.Skill).where(models_networking.Skill.name == skill_name))
            skill = result.scalar_one_or_none()
            if not skill:
                skill = models_networking.Skill(name=skill_name)
                db.add(skill)
            faculty.skills.append(skill)
            
    await db.commit()
    
    return schemas_networking.FacultyProfileUpdate(
        person_uuid=person_uuid,
        skills=[s.name for s in faculty.skills],
        interests=[i.name for i in faculty.interests]
    )

@router.get("/graph", response_model=schemas_networking.NetworkGraph)
async def get_network_graph(db: AsyncSession = Depends(get_db)):
    G = nx.Graph()
    
    # Add Students
    result = await db.execute(
        select(models_networking.Student)
        .options(selectinload(models_networking.Student.skills), selectinload(models_networking.Student.interests))
    )
    students = result.scalars().all()
    for s in students:
        G.add_node(str(s.student_id), label=s.name, type="student", group=1)
        
    # Add Faculty
    result = await db.execute(
        select(models.Faculty)
        .options(selectinload(models.Faculty.skills), selectinload(models.Faculty.interests))
    )
    faculty = result.scalars().all()
    for f in faculty:
        G.add_node(str(f.person_uuid), label=f.name, type="faculty", group=2)
        
    # Add Skills
    result = await db.execute(select(models_networking.Skill))
    skills = result.scalars().all()
    for s in skills:
        G.add_node(str(s.skill_id), label=s.name, type="skill", group=3)
        
    # Add Interests
    result = await db.execute(select(models_networking.Interest))
    interests = result.scalars().all()
    for i in interests:
        G.add_node(str(i.interest_id), label=i.name, type="interest", group=4)
        
    # Add Edges
    # Student-Skill
    for s in students:
        for sk in s.skills:
            G.add_edge(str(s.student_id), str(sk.skill_id))
        for i in s.interests:
            G.add_edge(str(s.student_id), str(i.interest_id))
            
    # Faculty-Skill
    for f in faculty:
        for sk in f.skills:
            G.add_edge(str(f.person_uuid), str(sk.skill_id))
        for i in f.interests:
            G.add_edge(str(f.person_uuid), str(i.interest_id))
            
    # Convert to response format
    nodes = [{"id": n, "label": G.nodes[n]["label"], "type": G.nodes[n]["type"], "group": G.nodes[n]["group"]} for n in G.nodes]
    edges = [{"source": u, "target": v} for u, v in G.edges]
    
    return {"nodes": nodes, "edges": edges}

@router.post("/analyze", response_model=schemas_networking.ChatAnalysisResponse)
async def analyze_network(request: schemas_networking.ChatAnalysisRequest, db: AsyncSession = Depends(get_db)):
    from app.ai_agent import create_networking_graph
    
    # Initialize workflow with DB session
    app = create_networking_graph(db)
    
    # Initial state
    initial_state = {
        "messages": [],
        "query": request.query,
        "extracted_skills": [],
        "relevant_nodes": [],
        "graph_data": {},
        "final_response": ""
    }
    
    # Run the graph
    # ainvoke returns the final state
    final_state = await app.ainvoke(initial_state)
    
    response_text = final_state.get("final_response", "I couldn't generate a response.")
    
    # Extract suggested nodes from the graph data or relevant_nodes
    # The frontend expects a specific format for suggested_connections
    suggested_nodes = []
    if "relevant_nodes" in final_state:
        suggested_nodes = final_state["relevant_nodes"]
        
    graph_data = final_state.get("graph_data", {})
        
    return {"response": response_text, "suggested_connections": suggested_nodes, "graph_data": graph_data}
