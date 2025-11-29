"""
Impact Cards API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models import ImpactCard as ImpactCardModel, Faculty, SDGGoal
from app.schemas import (
    ImpactCard, ImpactCardCreate, ImpactCardUpdate, 
    ImpactCardDetailed, ImpactCardFilter
)

router = APIRouter()


@router.get("/", response_model=List[ImpactCard])
async def list_impact_cards(
    sdg: Optional[int] = Query(None, ge=1, le=17),
    department: Optional[str] = None,
    status: str = Query("published", description="published, validated, draft"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """
    List all impact cards with filters
    """
    query = select(ImpactCardModel).where(ImpactCardModel.status == status)
    
    if sdg:
        query = query.where(ImpactCardModel.sdg == sdg)
    
    # TODO: Add department filter via join with Faculty
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    cards = result.scalars().all()
    
    return cards


@router.get("/{card_id}", response_model=ImpactCardDetailed)
async def get_impact_card(
    card_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed impact card with all nested data
    """
    # Get card
    result = await db.execute(
        select(ImpactCardModel).where(ImpactCardModel.card_id == card_id)
    )
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(status_code=404, detail="Impact card not found")
    
    # Get faculty info
    faculty_result = await db.execute(
        select(Faculty).where(Faculty.person_uuid == card.person_uuid)
    )
    faculty = faculty_result.scalar_one()
    
    # Get SDG info
    sdg_result = await db.execute(
        select(SDGGoal).where(SDGGoal.sdg_number == card.sdg)
    )
    sdg = sdg_result.scalar_one()
    
    # Build detailed response
    card_dict = {
        **card.__dict__,
        "faculty_name": faculty.name,
        "faculty_department": faculty.department,
        "sdg_title": sdg.title,
        "sdg_color": sdg.color_hex,
        "publication_details": [],  # TODO: Fetch actual publications
        "impact_details": []  # TODO: Fetch actual impacts
    }
    
    return card_dict


@router.post("/", response_model=ImpactCard, status_code=201)
async def create_impact_card(
    card: ImpactCardCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new impact card
    """
    db_card = ImpactCardModel(**card.model_dump())
    db.add(db_card)
    await db.commit()
    await db.refresh(db_card)
    return db_card


@router.patch("/{card_id}", response_model=ImpactCard)
async def update_impact_card(
    card_id: UUID,
    card_update: ImpactCardUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an impact card
    """
    result = await db.execute(
        select(ImpactCardModel).where(ImpactCardModel.card_id == card_id)
    )
    db_card = result.scalar_one_or_none()
    
    if not db_card:
        raise HTTPException(status_code=404, detail="Impact card not found")
    
    # Update fields
    update_data = card_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_card, field, value)
    
    await db.commit()
    await db.refresh(db_card)
    return db_card


@router.delete("/{card_id}", status_code=204)
async def delete_impact_card(
    card_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an impact card
    """
    result = await db.execute(
        select(ImpactCardModel).where(ImpactCardModel.card_id == card_id)
    )
    db_card = result.scalar_one_or_none()
    
    if not db_card:
        raise HTTPException(status_code=404, detail="Impact card not found")
    
    await db.delete(db_card)
    await db.commit()
    return None


@router.post("/{card_id}/publish")
async def publish_impact_card(
    card_id: UUID,
    validated_by: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Publish an impact card (change status to published)
    """
    result = await db.execute(
        select(ImpactCardModel).where(ImpactCardModel.card_id == card_id)
    )
    db_card = result.scalar_one_or_none()
    
    if not db_card:
        raise HTTPException(status_code=404, detail="Impact card not found")
    
    db_card.status = "published"
    db_card.validated_by = validated_by
    
    await db.commit()
    await db.refresh(db_card)
    
    return {"message": "Impact card published successfully", "card_id": str(card_id)}
