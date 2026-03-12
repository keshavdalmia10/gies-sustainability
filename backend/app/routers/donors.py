from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app import models, models_extended

router = APIRouter(
    tags=["donors"]
)

class DonorSearchRequest(BaseModel):
    project_description: str

class DonorMatch(BaseModel):
    name: str
    type: str  # Corporate, Foundation, Government, etc.
    match_reason: str
    website: str
    contact_info: Optional[str] = None

class DonorSearchResponse(BaseModel):
    matches: List[DonorMatch]

@router.post("/search", response_model=DonorSearchResponse)
async def search_donors(request: DonorSearchRequest):
    """
    Search for donors based on a project description using AI.
    """
    try:
        # Initialize LLM
        # Note: Requires OPENAI_API_KEY in environment
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import SystemMessage, HumanMessage

        llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        
        system_prompt = """You are an expert fundraising consultant. 
        Your goal is to identify REAL-WORLD donors (foundations, corporations, government grants) 
        that would be highly likely to fund the user's specific project.
        
        For each donor, you must provide:
        1. Name: The exact name of the organization.
        2. Type: e.g., "Corporate CSR", "Private Foundation", "Government Grant".
        3. Match Reason: A specific explanation of why this donor matches THIS project (cite their known focus areas).
        4. Website: The URL to their grants/sustainability page.
        5. Contact Info: A generic email or "Apply via website" if unknown.
        
        Return the result as a JSON object with a single key "matches" containing a list of these objects.
        Ensure the JSON is valid.
        """
        
        user_prompt = f"Project Description: {request.project_description}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = await llm.ainvoke(messages)
        content = response.content
        
        # Clean up code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        data = json.loads(content)
        
        # Normalize keys to lowercase to match Pydantic model
        if "matches" in data:
            normalized_matches = []
            for match in data["matches"]:
                normalized_match = {}
                for k, v in match.items():
                    # Handle keys with spaces like "Match Reason" -> "match_reason"
                    key = k.lower().replace(" ", "_")
                    normalized_match[key] = v
                normalized_matches.append(normalized_match)
            data["matches"] = normalized_matches
            
        return data
        
    except Exception as e:
        print(f"DEBUG: Router Error: {e}")
        import traceback
        traceback.print_exc()
        print(f"Error in donor search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class ProjectSearchRequest(BaseModel):
    donor_interest: str

class ProjectMatch(BaseModel):
    name: str
    type: str  # Faculty or Student Project
    title: str # Faculty Title or Project Title
    description: str # Current Work or Project Description
    match_reason: str
    email: Optional[str] = None

class ProjectSearchResponse(BaseModel):
    matches: List[ProjectMatch]

@router.post("/find-projects", response_model=ProjectSearchResponse)
async def find_projects(request: ProjectSearchRequest, db: AsyncSession = Depends(get_db)):
    """
    Search for faculty and student projects that match a donor's interest.
    """
    try:
        # 1. Fetch Faculty with current_work
        faculty_result = await db.execute(
            select(models.Faculty).where(models.Faculty.current_work.isnot(None))
        )
        faculty_list = faculty_result.scalars().all()
        
        # 2. Fetch Student Projects (assuming we have some, otherwise mock for now or fetch all)
        # For MVP, let's fetch all student projects
        projects_result = await db.execute(select(models_extended.StudentProject))
        projects_list = projects_result.scalars().all()
        
        # 3. Prepare context for LLM
        context_items = []
        for f in faculty_list:
            context_items.append(f"FACULTY: {f.name} | Current Work: {f.current_work} | Interests: {', '.join(f.research_interests or [])} | Email: {f.email}")
            
        for p in projects_list:
            context_items.append(f"STUDENT_PROJECT: {p.project_title} | Description: {p.description} | Advisor: {p.advisor_uuid}") # Ideally resolve advisor name
            
        context_str = "\n".join(context_items)
        
        if not context_str:
            return {"matches": []}

        # 4. AI Matching
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import SystemMessage, HumanMessage

        llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
        
        system_prompt = """You are an expert grant evaluator.
        A donor is looking to fund projects. 
        Given the list of Faculty and Student Projects below, identify the top 3-5 matches for the donor's interest.
        
        Return a JSON object with a key "matches" containing a list of objects with:
        - name: Name of Faculty or "Student Team"
        - type: "Faculty" or "Student Project"
        - title: The project title or faculty position
        - description: A brief summary of their work
        - match_reason: Why this specific work matches the donor's interest
        - email: The email if available (for faculty)
        """
        
        user_prompt = f"Donor Interest: {request.donor_interest}\n\nCandidates:\n{context_str}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = await llm.ainvoke(messages)
        content = response.content
        
        # Clean JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        data = json.loads(content)
        
        # Normalize keys
        if "matches" in data:
            normalized_matches = []
            for match in data["matches"]:
                normalized_match = {}
                for k, v in match.items():
                    key = k.lower().replace(" ", "_")
                    normalized_match[key] = v
                normalized_matches.append(normalized_match)
            data["matches"] = normalized_matches
            
        return data

    except Exception as e:
        print(f"Error in project search: {e}")
        raise HTTPException(status_code=500, detail=str(e))
