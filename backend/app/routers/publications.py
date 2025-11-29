"""
Publications API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models import Publication as PublicationModel
from app.schemas import Publication, PublicationCreate, PublicationFilter

router = APIRouter()


@router.get("/", response_model=List[Publication])
async def list_publications(
    sdg: Optional[int] = Query(None, ge=1, le=17),
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
    is_sustain: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    List publications with filters
    """
    query = select(PublicationModel)
    
    filters = []
    if sdg:
        filters.append(PublicationModel.sdg_top1 == sdg)
    if year_start:
        filters.append(PublicationModel.publication_year >= year_start)
    if year_end:
        filters.append(PublicationModel.publication_year <= year_end)
    if is_sustain is not None:
        filters.append(PublicationModel.is_sustain == is_sustain)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    publications = result.scalars().all()
    
    return publications


@router.get("/{publication_id}", response_model=Publication)
async def get_publication(
    publication_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single publication by ID
    """
    result = await db.execute(
        select(PublicationModel).where(PublicationModel.article_uuid == publication_id)
    )
    publication = result.scalar_one_or_none()
    
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    return publication


@router.post("/", response_model=Publication, status_code=201)
async def create_publication(
    publication: PublicationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new publication
    """
    db_publication = PublicationModel(**publication.model_dump())
    db.add(db_publication)
    await db.commit()
    await db.refresh(db_publication)
    return db_publication


@router.get("/sdg/{sdg_number}", response_model=List[Publication])
async def get_publications_by_sdg(
    sdg_number: int = Path(..., ge=1, le=17),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all publications for a specific SDG
    """
    query = select(PublicationModel).where(
        PublicationModel.sdg_top1 == sdg_number
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    publications = result.scalars().all()
    
    return publications
