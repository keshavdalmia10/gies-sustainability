"""
Faculty API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models import Faculty as FacultyModel, Publication, Grant
from app.schemas import (
    Faculty, FacultyCreate, FacultyUpdate, FacultyWithStats,
    PaginatedResponse
)

router = APIRouter()


@router.get("/", response_model=List[Faculty])
async def list_faculty(
    department: Optional[str] = None,
    active: Optional[bool] = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    List all faculty with optional filters
    """
    query = select(FacultyModel)
    
    if department:
        query = query.where(FacultyModel.department == department)
    if active is not None:
        query = query.where(FacultyModel.active == active)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    faculty = result.scalars().all()
    
    return faculty


@router.get("/{faculty_id}", response_model=FacultyWithStats)
async def get_faculty(
    faculty_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single faculty member with statistics
    """
    # Get faculty
    result = await db.execute(
        select(FacultyModel).where(FacultyModel.person_uuid == faculty_id)
    )
    faculty = result.scalar_one_or_none()
    
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    # Get stats
    pub_count_result = await db.execute(
        select(func.count(Publication.article_uuid)).where(
            Publication.person_uuid == faculty_id
        )
    )
    pub_count = pub_count_result.scalar() or 0
    
    sustain_count_result = await db.execute(
        select(func.count(Publication.article_uuid)).where(
            Publication.person_uuid == faculty_id,
            Publication.is_sustain == True
        )
    )
    sustain_count = sustain_count_result.scalar() or 0
    
    # Convert to dict and add stats
    faculty_dict = {
        "person_uuid": faculty.person_uuid,
        "name": faculty.name,
        "email": faculty.email,
        "department": faculty.department,
        "active": faculty.active,
        "profile_url": faculty.profile_url,
        "photo_url": faculty.photo_url,
        "research_interests": faculty.research_interests or [],
        "created_at": faculty.created_at,
        "updated_at": faculty.updated_at,
        "publication_count": pub_count,
        "sustainable_pub_count": sustain_count,
        "total_grant_funding": 0,  # TODO: Calculate from grants
        "patent_count": 0  # TODO: Calculate from patents
    }
    
    return faculty_dict


@router.post("/", response_model=Faculty, status_code=201)
async def create_faculty(
    faculty: FacultyCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new faculty member
    """
    db_faculty = FacultyModel(**faculty.model_dump())
    db.add(db_faculty)
    await db.commit()
    await db.refresh(db_faculty)
    return db_faculty


@router.patch("/{faculty_id}", response_model=Faculty)
async def update_faculty(
    faculty_id: UUID,
    faculty_update: FacultyUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update faculty information
    """
    result = await db.execute(
        select(FacultyModel).where(FacultyModel.person_uuid == faculty_id)
    )
    db_faculty = result.scalar_one_or_none()
    
    if not db_faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    # Update only provided fields
    update_data = faculty_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_faculty, field, value)
    
    await db.commit()
    await db.refresh(db_faculty)
    return db_faculty


@router.delete("/{faculty_id}", status_code=204)
async def delete_faculty(
    faculty_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a faculty member
    """
    result = await db.execute(
        select(FacultyModel).where(FacultyModel.person_uuid == faculty_id)
    )
    db_faculty = result.scalar_one_or_none()
    
    if not db_faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    await db.delete(db_faculty)
    await db.commit()
    return None


@router.get("/{faculty_id}/publications", response_model=List[dict])
async def get_faculty_publications(
    faculty_id: UUID,
    sdg: Optional[int] = Query(None, ge=1, le=17),
    db: AsyncSession = Depends(get_db)
):
    """
    Get publications for a faculty member, optionally filtered by SDG
    """
    query = select(Publication).where(Publication.person_uuid == faculty_id)
    
    if sdg:
        query = query.where(Publication.sdg_top1 == sdg)
    
    result = await db.execute(query)
    publications = result.scalars().all()
    
    return [
        {
            "article_uuid": str(p.article_uuid),
            "title": p.title,
            "publication_year": p.publication_year,
            "journal_title": p.journal_title,
            "sdg_top1": p.sdg_top1,
            "is_sustain": p.is_sustain
        }
        for p in publications
    ]
