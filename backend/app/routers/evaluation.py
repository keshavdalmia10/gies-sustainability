"""
Evaluation API endpoints (Precision@k, model metrics)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models import ModelEvaluation as ModelEvaluationModel, GroundTruthSet
from app.schemas import ModelEvaluation, ModelEvaluationCreate, GroundTruthCreate

router = APIRouter()


@router.get("/metrics", response_model=List[ModelEvaluation])
async def get_evaluation_metrics(
    sdg: Optional[int] = Query(None, ge=1, le=17),
    model_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get model evaluation metrics (Precision@k, Recall@k)
    """
    query = select(ModelEvaluationModel)
    
    if sdg:
        query = query.where(ModelEvaluationModel.sdg == sdg)
    if model_type:
        query = query.where(ModelEvaluationModel.model_type == model_type)
    
    query = query.order_by(ModelEvaluationModel.evaluation_date.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    evaluations = result.scalars().all()
    
    return evaluations


@router.post("/metrics", response_model=ModelEvaluation, status_code=201)
async def create_evaluation(
    evaluation: ModelEvaluationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Store new model evaluation results
    """
    db_evaluation = ModelEvaluationModel(**evaluation.model_dump())
    db.add(db_evaluation)
    await db.commit()
    await db.refresh(db_evaluation)
    return db_evaluation


@router.get("/metrics/latest")
async def get_latest_metrics(
    sdg: int = Query(..., ge=1, le=17),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the latest evaluation metrics for a specific SDG
    """
    result = await db.execute(
        select(ModelEvaluationModel)
        .where(ModelEvaluationModel.sdg == sdg)
        .order_by(ModelEvaluationModel.evaluation_date.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()
    
    if not latest:
        return {
            "sdg": sdg,
            "message": "No evaluation data available",
            "target_precision_at_5": 0.85
        }
    
    return {
        "sdg": sdg,
        "model_version": latest.model_version,
        "precision_at_k": latest.precision_at_k,
        "recall_at_k": latest.recall_at_k,
        "k": latest.k,
        "evaluation_date": latest.evaluation_date,
        "target_met": latest.precision_at_k >= 0.85 if latest.precision_at_k else False,
        "target_precision_at_5": 0.85
    }


@router.post("/ground-truth", status_code=201)
async def add_ground_truth(
    ground_truth: GroundTruthCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Add a ground truth validation record
    """
    db_gt = GroundTruthSet(**ground_truth.model_dump())
    db.add(db_gt)
    await db.commit()
    await db.refresh(db_gt)
    return {"message": "Ground truth record added", "gt_id": str(db_gt.gt_id)}


@router.get("/ground-truth")
async def list_ground_truth(
    sdg: Optional[int] = Query(None, ge=1, le=17),
    db: AsyncSession = Depends(get_db)
):
    """
    List ground truth validation records
    """
    query = select(GroundTruthSet)
    
    if sdg:
        query = query.where(GroundTruthSet.sdg == sdg)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    return records


@router.get("/ground-truth/stats")
async def ground_truth_stats(
    sdg: int = Query(..., ge=1, le=17),
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics about ground truth set for a specific SDG
    """
    # Count total records
    total_result = await db.execute(
        select(func.count(GroundTruthSet.gt_id))
        .where(GroundTruthSet.sdg == sdg)
    )
    total = total_result.scalar() or 0
    
    # Count true links
    true_links_result = await db.execute(
        select(func.count(GroundTruthSet.gt_id))
        .where(GroundTruthSet.sdg == sdg, GroundTruthSet.is_true_link == True)
    )
    true_links = true_links_result.scalar() or 0
    
    return {
        "sdg": sdg,
        "total_records": total,
        "true_links": true_links,
        "false_links": total - true_links,
        "coverage_percentage": (total / 20) * 100 if total else 0,  # Target: 20 records
        "target_size": 20
    }
