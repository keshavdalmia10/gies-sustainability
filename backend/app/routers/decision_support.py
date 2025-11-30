"""
Decision Support API endpoints (Dean, Donor, Student views)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any
from decimal import Decimal

from app.database import get_db
from app.models import (
    Faculty, Publication, ImpactCard as ImpactCardModel,
    Impact, Grant, Patent, SDGGoal, ImpactValidation
)
from app.schemas import DecisionSupportData, DonorViewData, DashboardStats

router = APIRouter()


@router.get("/dean", response_model=Dict[str, Any])
async def dean_dashboard_data(
    db: AsyncSession = Depends(get_db)
):
    """
    Strategic Gaps & Bets data for Dean/Provost view
    
    Returns:
    - SDG × Department matrix
    - Momentum indicators
    - Gap analysis
    - Flagship projects
    """
    # TODO: Implement complex queries for strategic analysis
    return {
        "sdg_matrix": [],
        "momentum_indicators": [],
        "gap_analysis": [],
        "flagship_projects": []
    }


@router.get("/donor", response_model=Dict[str, Any])
async def donor_view_data(
    sdg: int = Query(None, ge=1, le=17, description="Filter by SDG"),
    geography: str = Query(None, description="Illinois, Midwest, USA, Global"),
    db: AsyncSession = Depends(get_db)
):
    """
    Donor view data - fundable impact cards
    
    Returns impact cards optimized for donor decision-making
    """
    query = select(ImpactCardModel).where(ImpactCardModel.status == "published")
    
    if sdg:
        query = query.where(ImpactCardModel.sdg == sdg)
    if geography:
        query = query.where(ImpactCardModel.geography == geography)
    
    result = await db.execute(query)
    cards = result.scalars().all()
    
    # Calculate aggregates
    total_funding_gap = sum(card.funding_gap or Decimal(0) for card in cards)
    total_communities = sum(card.communities_reached or 0 for card in cards)
    
    # SDG breakdown
    sdg_breakdown = {}
    for card in cards:
        sdg_breakdown[card.sdg] = sdg_breakdown.get(card.sdg, 0) + 1
    
    return {
        "impact_cards": [
            {
                "card_id": str(card.card_id),
                "title": card.title,
                "summary": card.summary,
                "sdg": card.sdg,
                "total_funding": float(card.total_funding or 0),
                "funding_gap": float(card.funding_gap or 0),
                "key_outcomes": card.key_outcomes,
                "geography": card.geography
            }
            for card in cards
        ],
        "total_funding_opportunities": float(total_funding_gap),
        "communities_reached": total_communities,
        "sdg_breakdown": sdg_breakdown,
        "total_cards": len(cards)
    }


@router.get("/student")
async def student_view_data(
    sdg: int = Query(None, ge=1, le=17),
    keyword: str = Query(None, description="Research interest keyword"),
    db: AsyncSession = Depends(get_db)
):
    """
    Student view - Find My Mentor
    
    Returns faculty profiles filtered by SDG and research interests
    """
    query = select(Faculty).where(Faculty.active == True)
    
    # If SDG specified, find faculty with publications in that SDG
    if sdg:
        # TODO: Add join with publications to filter by SDG
        pass
    
    result = await db.execute(query.limit(50))
    faculty_list = result.scalars().all()
    
    return {
        "faculty": [
            {
                "person_uuid": str(f.person_uuid),
                "name": f.name,
                "department": f.department,
                "email": f.email,
                "photo_url": f.photo_url,
                "research_interests": f.research_interests,
                "profile_url": f.profile_url
            }
            for f in faculty_list
        ],
        "total": len(faculty_list)
    }


@router.get("/stats", response_model=Dict[str, Any])
async def dashboard_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Overall dashboard statistics
    """
    # Count total faculty
    faculty_count = await db.execute(select(func.count(Faculty.person_uuid)))
    total_faculty = faculty_count.scalar() or 0
    
    # Count publications
    pub_count = await db.execute(select(func.count(Publication.article_uuid)))
    total_pubs = pub_count.scalar() or 0
    
    # Count sustainable publications
    sustain_count = await db.execute(
        select(func.count(Publication.article_uuid)).where(Publication.is_sustain == True)
    )
    sustainable_pubs = sustain_count.scalar() or 0
    
    # Sum grant funding
    funding_sum = await db.execute(
        select(func.sum(Impact.funding_amount)).where(Impact.impact_type == 'grant')
    )
    total_funding = funding_sum.scalar() or Decimal(0)
    
    # Count patents
    patent_count = await db.execute(
        select(func.count(Patent.patent_id))
    )
    total_patents = patent_count.scalar() or 0
    
    # Count impact cards
    card_count = await db.execute(
        select(func.count(ImpactCardModel.card_id)).where(ImpactCardModel.status == 'published')
    )
    total_cards = card_count.scalar() or 0
    
    # By SDG
    by_sdg_result = await db.execute(
        select(
            Publication.sdg_top1,
            func.count(Publication.article_uuid).label('count')
        )
        .where(Publication.is_sustain == True)
        .group_by(Publication.sdg_top1)
    )
    by_sdg = {row[0]: {"count": row[1]} for row in by_sdg_result if row[0]}
    
    # Count validations
    validation_count = await db.execute(
        select(func.count(ImpactValidation.validation_id))
    )
    total_validations = validation_count.scalar() or 0
    
    # Calculate approval rate
    approval_count = await db.execute(
        select(func.count(ImpactValidation.validation_id)).where(ImpactValidation.status == 'approved')
    )
    approved_validations = approval_count.scalar() or 0
    approval_rate = (approved_validations / total_validations * 100) if total_validations > 0 else 0

    return {
        "total_faculty": total_faculty,
        "total_publications": total_pubs,
        "sustainable_publications": sustainable_pubs,
        "total_funding": float(total_funding),
        "total_patents": total_patents,
        "total_impact_cards": total_cards,
        "by_sdg": by_sdg,
        "sustainability_percentage": (sustainable_pubs / total_pubs * 100) if total_pubs > 0 else 0,
        "community_validations": total_validations,
        "community_approval_rate": approval_rate
    }


@router.get("/sdg/{sdg_number}/summary")
async def sdg_summary(
    sdg_number: int = Path(..., ge=1, le=17),
    db: AsyncSession = Depends(get_db)
):
    """
    Comprehensive summary for a specific SDG
    """
    # Get SDG info
    sdg_result = await db.execute(
        select(SDGGoal).where(SDGGoal.sdg_number == sdg_number)
    )
    sdg = sdg_result.scalar_one_or_none()
    
    if not sdg:
        raise HTTPException(status_code=404, detail="SDG not found")
    
    # Count publications
    pub_count = await db.execute(
        select(func.count(Publication.article_uuid))
        .where(Publication.sdg_top1 == sdg_number)
    )
    
    # Count impact cards
    card_count = await db.execute(
        select(func.count(ImpactCardModel.card_id))
        .where(ImpactCardModel.sdg == sdg_number, ImpactCardModel.status == 'published')
    )
    
    # Get latest evaluation
    eval_result = await db.execute(
        select(func.max(func.coalesce(func.nullif(0, 0), 0)))  # Placeholder
    )
    
    return {
        "sdg": {
            "number": sdg.sdg_number,
            "title": sdg.title,
            "description": sdg.description,
            "color": sdg.color_hex
        },
        "metrics": {
            "publications": pub_count.scalar() or 0,
            "impact_cards": card_count.scalar() or 0,
            "precision_at_5": 0.0  # TODO: Get from evaluations
        }
    }
