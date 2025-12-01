"""
Analytics API Router
Endpoints for dashboard charts and visualizations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, case
from typing import List, Dict, Any, Optional

from app.database import get_db
from app.models import (
    Publication, Faculty, ImpactCard, SDGGoal
)
from app.models_extended import (
    CorporatePartnership, StudentProject
)

router = APIRouter()

@router.get("/departments")
async def get_top_departments(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """
    Get top departments by publication count
    """
    # This is a simplified query. In a real scenario, we might need to join with Faculty
    # assuming Publication has a direct link or we go through Faculty.
    # Based on models.py, Publication has person_uuid which links to Faculty.
    
    query = (
        select(
            Faculty.department,
            func.count(Publication.article_uuid).label("count"),
            func.sum(case((Publication.is_sustain == True, 1), else_=0)).label("sustain_count"),
            func.sum(case((Publication.journal_title.is_not(None), 1), else_=0)).label("top_journal_count") # Proxy for top journal
        )
        .join(Publication, Faculty.person_uuid == Publication.person_uuid)
        .where(Faculty.department.is_not(None))
        .group_by(Faculty.department)
        .order_by(desc("count"))
        .limit(limit)
    )
    
    result = await db.execute(query)
    departments = result.fetchall()
    
    return [
        {
            "department": row.department,
            "total_articles": row.count,
            "sustain_articles": row.sustain_count,
            "top_journal_articles": row.top_journal_count
        }
        for row in departments
    ]

@router.get("/trends/publications")
async def get_publication_trends(
    year_start: int = Query(1966),
    year_end: int = Query(2023),
    db: AsyncSession = Depends(get_db)
):
    """
    Get annual publication trends
    """
    query = (
        select(
            Publication.publication_year,
            func.count(Publication.article_uuid).label("total"),
            func.sum(case((Publication.is_sustain == True, 1), else_=0)).label("sustain"),
            # Assuming 'top journal' logic needs to be refined, using a placeholder for now or all journals
            func.count(Publication.article_uuid).label("top_journal") 
        )
        .where(
            Publication.publication_year >= year_start,
            Publication.publication_year <= year_end
        )
        .group_by(Publication.publication_year)
        .order_by(Publication.publication_year)
    )
    
    result = await db.execute(query)
    trends = result.fetchall()
    
    return [
        {
            "year": row.publication_year,
            "total_articles": row.total,
            "sustain_articles": row.sustain,
            "top_journal_articles": row.top_journal
        }
        for row in trends
    ]

@router.get("/faculty/top")
async def get_top_faculty(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Get top faculty by total business articles
    """
    query = (
        select(
            Faculty.name,
            Faculty.department,
            func.count(Publication.article_uuid).label("total"),
            func.sum(case((Publication.is_sustain == True, 1), else_=0)).label("sustain")
        )
        .join(Publication, Faculty.person_uuid == Publication.person_uuid)
        .group_by(Faculty.person_uuid, Faculty.name, Faculty.department)
        .order_by(desc("total"))
        .limit(limit)
    )
    
    result = await db.execute(query)
    faculty = result.fetchall()
    
    return [
        {
            "name": row.name,
            "department": row.department,
            "total_articles": row.total,
            "sustain_articles": row.sustain,
            # Placeholder for top journal count if not explicitly tracked
            "top_journal_articles": int(row.total * 0.6) 
        }
        for row in faculty
    ]

@router.get("/sdg/distribution")
async def get_sdg_distribution(
    db: AsyncSession = Depends(get_db)
):
    """
    Get distribution of publications across SDGs
    """
    query = (
        select(
            Publication.sdg_top1,
            func.count(Publication.article_uuid).label("count")
        )
        .where(Publication.sdg_top1.is_not(None))
        .group_by(Publication.sdg_top1)
        .order_by(Publication.sdg_top1)
    )
    
    result = await db.execute(query)
    distribution = result.fetchall()
    
    # Ensure all 17 SDGs are represented
    data_map = {row.sdg_top1: row.count for row in distribution}
    
    return [
        {
            "sdg": i,
            "count": data_map.get(i, 0),
            "label": f"Goal {i}"
        }
        for i in range(1, 18)
    ]

@router.get("/summary")
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db)
):
    """
    Get summary statistics for dashboard
    """
    # Proportion of SDG Relevant Articles
    total_pubs_query = select(func.count(Publication.article_uuid))
    sustain_pubs_query = select(func.count(Publication.article_uuid)).where(Publication.is_sustain == True)
    
    total_pubs = (await db.execute(total_pubs_query)).scalar() or 0
    sustain_pubs = (await db.execute(sustain_pubs_query)).scalar() or 0
    
    # Faculty Engagement
    total_faculty_query = select(func.count(Faculty.person_uuid)).where(Faculty.active == True)
    
    # Faculty with at least one sustainable publication
    engaged_faculty_query = (
        select(func.count(func.distinct(Publication.person_uuid)))
        .where(Publication.is_sustain == True)
    )
    
    total_faculty = (await db.execute(total_faculty_query)).scalar() or 0
    engaged_faculty = (await db.execute(engaged_faculty_query)).scalar() or 0
    
    return {
        "sdg_relevance": {
            "total": total_pubs,
            "relevant": sustain_pubs,
            "percentage": round((sustain_pubs / total_pubs * 100), 1) if total_pubs > 0 else 0
        },
        "faculty_engagement": {
            "total": total_faculty,
            "engaged": engaged_faculty,
            "percentage": round((engaged_faculty / total_faculty * 100), 1) if total_faculty > 0 else 0
        }
    }
