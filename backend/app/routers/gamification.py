from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Any
from app.database import get_db
from app.models_networking import Student

router = APIRouter(
    tags=["gamification"]
)

@router.get("/leaderboard", response_model=List[Any])
async def get_leaderboard(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """
    Get the top students by impact points.
    """
    result = await db.execute(
        select(Student)
        .order_by(desc(Student.impact_points))
        .limit(limit)
    )
    students = result.scalars().all()
    
    leaderboard = []
    for student in students:
        leaderboard.append({
            "name": student.name,
            "major": student.major,
            "points": student.impact_points or 0,
            "avatar": f"https://ui-avatars.com/api/?name={student.name}&background=random" # Simple avatar generation
        })
        
    return leaderboard
