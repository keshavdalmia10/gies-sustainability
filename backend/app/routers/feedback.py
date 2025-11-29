"""
Feedback API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models import FacultyFeedback as FeedbackModel
from app.schemas import FacultyFeedback, FacultyFeedbackCreate

router = APIRouter()


@router.post("/", response_model=FacultyFeedback, status_code=201)
async def submit_feedback(
    feedback: FacultyFeedbackCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit faculty feedback/correction request
    """
    db_feedback = FeedbackModel(**feedback.model_dump())
    db.add(db_feedback)
    await db.commit()
    await db.refresh(db_feedback)
    return db_feedback


@router.get("/", response_model=List[FacultyFeedback])
async def list_feedback(
    status: Optional[str] = Query(None, description="pending, approved, rejected, resolved"),
    feedback_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    List all feedback submissions with filters
    """
    query = select(FeedbackModel)
    
    if status:
        query = query.where(FeedbackModel.status == status)
    if feedback_type:
        query = query.where(FeedbackModel.feedback_type == feedback_type)
    
    query = query.order_by(FeedbackModel.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    feedback_list = result.scalars().all()
    
    return feedback_list


@router.get("/{feedback_id}", response_model=FacultyFeedback)
async def get_feedback(
    feedback_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific feedback submission
    """
    result = await db.execute(
        select(FeedbackModel).where(FeedbackModel.feedback_id == feedback_id)
    )
    feedback = result.scalar_one_or_none()
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    return feedback


@router.patch("/{feedback_id}/resolve")
async def resolve_feedback(
    feedback_id: UUID,
    reviewed_by: str,
    new_status: str = Query(..., description="approved, rejected, resolved"),
    db: AsyncSession = Depends(get_db)
):
    """
    Resolve a feedback submission
    """
    result = await db.execute(
        select(FeedbackModel).where(FeedbackModel.feedback_id == feedback_id)
    )
    feedback = result.scalar_one_or_none()
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    feedback.status = new_status
    feedback.reviewed_by = reviewed_by
    feedback.resolved_at = func.now()
    
    await db.commit()
    await db.refresh(feedback)
    
    return {"message": f"Feedback {new_status}", "feedback_id": str(feedback_id)}


@router.get("/faculty/{faculty_id}")
async def get_faculty_feedback_history(
    faculty_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all feedback submitted by a specific faculty member
    """
    result = await db.execute(
        select(FeedbackModel)
        .where(FeedbackModel.person_uuid == faculty_id)
        .order_by(FeedbackModel.created_at.desc())
    )
    feedback_list = result.scalars().all()
    
    return feedback_list
