"""
ML Router - Endpoints for machine learning services
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from pydantic import BaseModel

from app.database import get_db
from app.models import Publication

router = APIRouter()


def _get_sdg_classifier():
    from app.services.ml.sdg_classifier import get_sdg_classifier

    return get_sdg_classifier()


def _get_impact_matcher():
    from app.services.ml.impact_matcher import get_impact_matcher

    return get_impact_matcher()


# Request/Response schemas
class SDGClassificationRequest(BaseModel):
    text: str
    title: str = None
    top_k: int = 3


class SDGClassificationResponse(BaseModel):
    is_sustainable: bool
    confidence: float
    sdg_classifications: List[dict]
    sdg_top1: int = None
    sdg_top2: int = None
    sdg_top3: int = None


class ImpactMatchRequest(BaseModel):
    publication_id: UUID
    threshold: float = 0.75
    candidate_impact_ids: List[UUID] = None


class ImpactMatchResponse(BaseModel):
    publication_id: UUID
    matches: List[dict]
    count: int


@router.post("/classify-sdg", response_model=SDGClassificationResponse)
async def classify_sdg(
    request: SDGClassificationRequest
):
    """
    Classify text for SDG relevance and identify top SDG goals
    
    Uses two-stage AI pipeline:
    1. Binary sustainability relevance (OpenAI)
    2. Top-K SDG identification (sentence-transformers)
    """
    classifier = _get_sdg_classifier()
    
    try:
        result = await classifier.classify_full(
            text=request.text,
            title=request.title,
            top_k=request.top_k
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")


@router.post("/classify-publication/{publication_id}")
async def classify_publication(
    publication_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Classify an existing publication for SDG relevance
    
    Updates the publication record with SDG classifications
    """
    from sqlalchemy import select, update
    
    # Get publication
    result = await db.execute(
        select(Publication).where(Publication.article_uuid == publication_id)
    )
    publication = result.scalar_one_or_none()
    
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    # Classify
    classifier = _get_sdg_classifier()
    
    text = publication.abstract or publication.title
    classification = await classifier.classify_full(
        text=text,
        title=publication.title,
        top_k=3
    )
    
    # Update publication
    await db.execute(
        update(Publication)
        .where(Publication.article_uuid == publication_id)
        .values(
            is_sustain=classification["is_sustainable"],
            sdg_top1=classification["sdg_top1"],
            sdg_top2=classification["sdg_top2"],
            sdg_top3=classification["sdg_top3"],
            sdg_confidence=classification["confidence"]
        )
    )
    await db.commit()
    
    return {
        "publication_id": str(publication_id),
        "classification": classification,
        "message": "Publication updated with SDG classifications"
    }


@router.post("/match-impacts", response_model=ImpactMatchResponse)
async def match_publication_impacts(
    request: ImpactMatchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Match a publication to related impacts using multi-modal similarity
    
    Returns ranked list of impacts with confidence scores
    """
    matcher = _get_impact_matcher()
    
    try:
        matches = await matcher.match_publication_to_impacts(
            session=db,
            publication_uuid=request.publication_id,
            candidate_impact_ids=request.candidate_impact_ids,
            threshold=request.threshold
        )
        
        return {
            "publication_id": request.publication_id,
            "matches": [
                {
                    "impact_id": str(impact_id),
                    "confidence_score": score
                }
                for impact_id, score in matches
            ],
            "count": len(matches)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching error: {str(e)}")


@router.post("/batch-classify")
async def batch_classify_publications(
    publication_ids: List[UUID] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Batch classify multiple publications
    
    If publication_ids not provided, classifies unclassified publications
    """
    from sqlalchemy import select, update
    
    query = select(Publication)
    
    if publication_ids:
        query = query.where(Publication.article_uuid.in_(publication_ids))
    else:
        # Get unclassified publications
        query = query.where(Publication.is_sustain == False).limit(limit)
    
    result = await db.execute(query)
    publications = result.scalars().all()
    
    classifier = _get_sdg_classifier()
    results = []
    
    for pub in publications:
        text = pub.abstract or pub.title
        classification = await classifier.classify_full(
            text=text,
            title=pub.title,
            top_k=3
        )
        
        # Update publication
        await db.execute(
            update(Publication)
            .where(Publication.article_uuid == pub.article_uuid)
            .values(
                is_sustain=classification["is_sustainable"],
                sdg_top1=classification["sdg_top1"],
                sdg_top2=classification["sdg_top2"],
                sdg_top3=classification["sdg_top3"],
                sdg_confidence=classification["confidence"]
            )
        )
        
        results.append({
            "publication_id": str(pub.article_uuid),
            "title": pub.title,
            "is_sustainable": classification["is_sustainable"],
            "sdg_top1": classification["sdg_top1"]
        })
    
    await db.commit()
    
    return {
        "total_processed": len(results),
        "results": results
    }
