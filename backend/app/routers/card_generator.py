"""
Impact Card Generator API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from pydantic import BaseModel

from app.database import get_db
from app.services.impact_card_generator import get_impact_card_generator

router = APIRouter()


class GenerateCardRequest(BaseModel):
    faculty_uuid: UUID
    sdg: int
    auto_save: bool = True


class GenerateCardResponse(BaseModel):
    card_id: UUID = None
    title: str
    narrative: str
    key_outcomes: List[str]
    total_funding: float
    funding_gap: float
    status: str


class BatchGenerateRequest(BaseModel):
    faculty_sdg_pairs: List[dict]  # [{"faculty_uuid": "...", "sdg": 7}, ...]


@router.post("/generate", response_model=GenerateCardResponse)
async def generate_impact_card(
    request: GenerateCardRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate an impact card with LLM-powered narrative
    
    This endpoint:
    1. Aggregates faculty publications and impacts for specific SDG
    2. Generates compelling narrative using GPT-4
    3. Calculates funding metrics and outcomes
    4. Optionally saves to database
    """
    generator = get_impact_card_generator()
    
    try:
        card_data = await generator.generate_impact_card(
            session=db,
            faculty_uuid=request.faculty_uuid,
            sdg=request.sdg,
            auto_save=request.auto_save
        )
        
        return {
            "card_id": card_data.get("card_id"),
            "title": card_data["title"],
            "narrative": card_data["narrative"],
            "key_outcomes": card_data["key_outcomes"],
            "total_funding": float(card_data["total_funding"]),
            "funding_gap": float(card_data["funding_gap"]),
            "status": card_data["status"]
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating card: {str(e)}")


@router.post("/batch-generate")
async def batch_generate_cards(
    request: BatchGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate multiple impact cards in batch
    
    Useful for generating cards for all faculty in specific SDG
    """
    generator = get_impact_card_generator()
    results = []
    errors = []
    
    for pair in request.faculty_sdg_pairs:
        try:
            card_data = await generator.generate_impact_card(
                session=db,
                faculty_uuid=UUID(pair["faculty_uuid"]),
                sdg=pair["sdg"],
                auto_save=True
            )
            
            results.append({
                "faculty_uuid": pair["faculty_uuid"],
                "sdg": pair["sdg"],
                "card_id": str(card_data.get("card_id")),
                "status": "success"
            })
        
        except Exception as e:
            errors.append({
                "faculty_uuid": pair["faculty_uuid"],
                "sdg": pair["sdg"],
                "error": str(e)
            })
    
    return {
        "total_requested": len(request.faculty_sdg_pairs),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }


@router.post("/regenerate-narrative/{card_id}")
async def regenerate_narrative(
    card_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Regenerate narrative for existing impact card
    
    Useful if you want to refresh the narrative with updated data
    """
    from app.models import ImpactCard
    from sqlalchemy import select, update
    
    # Get existing card
    result = await db.execute(
        select(ImpactCard).where(ImpactCard.card_id == card_id)
    )
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(status_code=404, detail="Impact card not found")
    
    # Regenerate
    generator = get_impact_card_generator()
    
    try:
        card_data = await generator.generate_impact_card(
            session=db,
            faculty_uuid=card.person_uuid,
            sdg=card.sdg,
            auto_save=False  # Don't auto-save, we'll update manually
        )
        
        # Update only the narrative
        await db.execute(
            update(ImpactCard)
            .where(ImpactCard.card_id == card_id)
            .values(
                narrative=card_data["narrative"],
                summary=card_data["summary"]
            )
        )
        await db.commit()
        
        return {
            "card_id": str(card_id),
            "narrative": card_data["narrative"],
            "message": "Narrative regenerated successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error regenerating narrative: {str(e)}")


@router.get("/preview/{faculty_uuid}/{sdg}")
async def preview_card_data(
    faculty_uuid: UUID,
    sdg: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Preview what data would be used for card generation
    
    Returns aggregated data without generating narrative
    Useful for checking data completeness before generating
    """
    generator = get_impact_card_generator()
    
    try:
        data = await generator.aggregate_faculty_sdg_data(
            session=db,
            faculty_uuid=faculty_uuid,
            sdg=sdg
        )
        
        return {
            "faculty_name": data["faculty"].name,
            "department": data["faculty"].department,
            "sdg": data["sdg"].sdg_number if data["sdg"] else sdg,
            "sdg_title": data["sdg"].title if data["sdg"] else f"SDG {sdg}",
            "publication_count": len(data["publications"]),
            "grant_count": len(data["grants"]),
            "patent_count": len(data["patents"]),
            "policy_count": len(data["policies"]),
            "total_impacts": len(data["impacts"]),
            "has_sufficient_data": len(data["publications"]) > 0 or len(data["grants"]) > 0
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error previewing data: {str(e)}")
