"""
Impacts API endpoints (grants, patents, policies)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models import Impact as ImpactModel, Grant as GrantModel, Patent as PatentModel
from app.schemas import Impact, ImpactCreate, Grant, GrantCreate, Patent, PatentCreate

router = APIRouter()


@router.get("/", response_model=List[Impact])
async def list_impacts(
    impact_type: Optional[str] = None,
    sdg: Optional[int] = Query(None, ge=1, le=17),
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """
    List all impacts with filters
    """
    query = select(ImpactModel)
    
    if impact_type:
        query = query.where(ImpactModel.impact_type == impact_type)
    if sdg:
        query = query.where(ImpactModel.sdg_primary == sdg)
    if status:
        query = query.where(ImpactModel.status == status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    impacts = result.scalars().all()
    
    return impacts


@router.get("/{impact_id}", response_model=Impact)
async def get_impact(
    impact_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single impact by ID
    """
    result = await db.execute(
        select(ImpactModel).where(ImpactModel.impact_id == impact_id)
    )
    impact = result.scalar_one_or_none()
    
    if not impact:
        raise HTTPException(status_code=404, detail="Impact not found")
    
    return impact


@router.post("/", response_model=Impact, status_code=201)
async def create_impact(
    impact: ImpactCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new impact
    """
    db_impact = ImpactModel(**impact.model_dump())
    db.add(db_impact)
    await db.commit()
    await db.refresh(db_impact)
    return db_impact


# Grant-specific endpoints
@router.post("/grants", response_model=Grant, status_code=201)
async def create_grant(
    grant: GrantCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new grant (creates both Impact and Grant records)
    """
    # Create impact first
    impact_data = grant.model_dump(exclude={'external_id', 'funder', 'funder_division', 
                                            'program', 'pi_uuid', 'co_investigators', 
                                            'keywords', 'abstract', 'award_notice_date'})
    impact_data['impact_type'] = 'grant'
    db_impact = ImpactModel(**impact_data)
    db.add(db_impact)
    await db.flush()  # Get the impact_id
    
    # Create grant
    grant_data = {
        'grant_id': db_impact.impact_id,
        'external_id': grant.external_id,
        'funder': grant.funder,
        'funder_division': grant.funder_division,
        'program': grant.program,
        'pi_uuid': grant.pi_uuid,
        'co_investigators': grant.co_investigators,
        'keywords': grant.keywords,
        'abstract': grant.abstract,
        'award_notice_date': grant.award_notice_date
    }
    db_grant = GrantModel(**grant_data)
    db.add(db_grant)
    
    await db.commit()
    await db.refresh(db_impact)
    
    return {**db_impact.__dict__, **db_grant.__dict__}


@router.get("/grants", response_model=List[Grant])
async def list_grants(
    funder: Optional[str] = None,
    pi_uuid: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    List all grants with filters
    """
    query = select(GrantModel)
    
    if funder:
        query = query.where(GrantModel.funder == funder)
    if pi_uuid:
        query = query.where(GrantModel.pi_uuid == pi_uuid)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    grants = result.scalars().all()
    
    return grants


# Patent-specific endpoints
@router.post("/patents", response_model=Patent, status_code=201)
async def create_patent(
    patent: PatentCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new patent
    """
    # Create impact first
    impact_data = patent.model_dump(exclude={'patent_number', 'inventors', 'assignee',
                                             'classification_codes', 'citations_count',
                                             'grant_date', 'filing_date'})
    impact_data['impact_type'] = 'patent'
    db_impact = ImpactModel(**impact_data)
    db.add(db_impact)
    await db.flush()
    
    # Create patent
    patent_data = {
        'patent_id': db_impact.impact_id,
        'patent_number': patent.patent_number,
        'inventors': patent.inventors,
        'assignee': patent.assignee,
        'classification_codes': patent.classification_codes,
        'citations_count': patent.citations_count,
        'grant_date': patent.grant_date,
        'filing_date': patent.filing_date
    }
    db_patent = PatentModel(**patent_data)
    db.add(db_patent)
    
    await db.commit()
    await db.refresh(db_impact)
    
    return {**db_impact.__dict__, **db_patent.__dict__}


@router.post("/match")
async def match_publication_to_impacts(
    publication_id: UUID,
    threshold: float = Query(0.75, ge=0.0, le=1.0),
    db: AsyncSession = Depends(get_db)
):
    """
    Find related impacts for a publication using the matching engine
    
    TODO: Implement actual matching logic with embeddings
    """
    # Placeholder - will implement with ML service
    return {
        "publication_id": str(publication_id),
        "matches": [],
        "message": "Matching engine not yet implemented"
    }
