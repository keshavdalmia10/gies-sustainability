"""
API Router for Extended Data Types

Endpoints for courses, student projects, corporate partnerships
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas_extended import (
    CourseCurriculum, CourseCurriculumCreate,
    StudentProject, StudentProjectCreate,
    CorporatePartnership, CorporatePartnershipCreate,
    SustainabilityTeachingSummary, PartnershipPortfolio, StudentImpactStat
)
from app.models_extended import (
    CourseCurriculum as CourseCurriculumModel,
    StudentProject as StudentProjectModel,
    CorporatePartnership as CorporatePartnershipModel
)

router = APIRouter()


# ===== Course Curricula Endpoints =====

@router.get("/courses", response_model=List[CourseCurriculum])
async def get_courses(
    sdg: Optional[int] = None,
    department: Optional[str] = None,
    year: Optional[int] = None,
    instructor_uuid: Optional[UUID] = None,
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Get sustainability-focused courses"""
    query = select(CourseCurriculumModel)
    
    if sdg:
        query = query.where(CourseCurriculumModel.sdg_primary == sdg)
    if department:
        query = query.where(CourseCurriculumModel.department == department)
    if year:
        query = query.where(CourseCurriculumModel.year == year)
    if instructor_uuid:
        query = query.where(CourseCurriculumModel.instructor_uuid == instructor_uuid)
    
    query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/courses", response_model=CourseCurriculum, status_code=201)
async def create_course(
    course: CourseCurriculumCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new course record"""
    db_course = CourseCurriculumModel(**course.dict())
    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return db_course


@router.get("/courses/{course_id}", response_model=CourseCurriculum)
async def get_course(
    course_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get specific course"""
    result = await db.execute(
        select(CourseCurriculumModel).where(CourseCurriculumModel.course_id == course_id)
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return course


@router.get("/teaching-summary", response_model=List[SustainabilityTeachingSummary])
async def get_teaching_summary(
    db: AsyncSession = Depends(get_db)
):
    """Get faculty sustainability teaching summary"""
    query = """
        SELECT * FROM faculty_sustainability_teaching
        ORDER BY sustainability_courses_count DESC
        LIMIT 100
    """
    result = await db.execute(query)
    return result.fetchall()


# ===== Student Projects Endpoints =====

@router.get("/student-projects", response_model=List[StudentProject])
async def get_student_projects(
    sdg: Optional[int] = None,
    project_type: Optional[str] = None,
    advisor_uuid: Optional[UUID] = None,
    year: Optional[int] = None,
    has_publication: Optional[bool] = None,
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Get student sustainability projects"""
    query = select(StudentProjectModel)
    
    if sdg:
        query = query.where(StudentProjectModel.sdg_primary == sdg)
    if project_type:
        query = query.where(StudentProjectModel.project_type == project_type)
    if advisor_uuid:
        query = query.where(StudentProjectModel.advisor_uuid == advisor_uuid)
    if year:
        query = query.where(StudentProjectModel.project_year == year)
    if has_publication is not None:
        query = query.where(StudentProjectModel.publication_resulted == has_publication)
    
    query = query.limit(limit).order_by(StudentProjectModel.project_year.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/student-projects", response_model=StudentProject, status_code=201)
async def create_student_project(
    project: StudentProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new student project record"""
    db_project = StudentProjectModel(**project.dict())
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project


@router.get("/student-projects/{project_id}", response_model=StudentProject)
async def get_student_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get specific student project"""
    result = await db.execute(
        select(StudentProjectModel).where(StudentProjectModel.project_id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Student project not found")
    
    return project


@router.get("/student-impact-stats", response_model=List[StudentImpactStat])
async def get_student_impact_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get student impact statistics"""
    query = "SELECT * FROM student_impact_summary ORDER BY project_year DESC"
    result = await db.execute(query)
    return result.fetchall()


# ===== Corporate Partnerships Endpoints =====

@router.get("/partnerships", response_model=List[CorporatePartnership])
async def get_partnerships(
    sdg: Optional[int] = None,
    partnership_type: Optional[str] = None,
    industry_sector: Optional[str] = None,
    status: Optional[str] = None,
    faculty_lead_uuid: Optional[UUID] = None,
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Get corporate partnerships"""
    query = select(CorporatePartnershipModel)
    
    if sdg:
        query = query.where(CorporatePartnershipModel.sdg_primary == sdg)
    if partnership_type:
        query = query.where(CorporatePartnershipModel.partnership_type == partnership_type)
    if industry_sector:
        query = query.where(CorporatePartnershipModel.industry_sector == industry_sector)
    if status:
        query = query.where(CorporatePartnershipModel.status == status)
    if faculty_lead_uuid:
        query = query.where(CorporatePartnershipModel.faculty_lead_uuid == faculty_lead_uuid)
    
    query = query.limit(limit).order_by(CorporatePartnershipModel.start_date.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/partnerships", response_model=CorporatePartnership, status_code=201)
async def create_partnership(
    partnership: CorporatePartnershipCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new corporate partnership record"""
    db_partnership = CorporatePartnershipModel(**partnership.dict())
    db.add(db_partnership)
    await db.commit()
    await db.refresh(db_partnership)
    return db_partnership


@router.get("/partnerships/{partnership_id}", response_model=CorporatePartnership)
async def get_partnership(
    partnership_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get specific partnership"""
    result = await db.execute(
        select(CorporatePartnershipModel).where(
            CorporatePartnershipModel.partnership_id == partnership_id
        )
    )
    partnership = result.scalar_one_or_none()
    
    if not partnership:
        raise HTTPException(status_code=404, detail="Partnership not found")
    
    return partnership


@router.get("/partnership-portfolio", response_model=List[PartnershipPortfolio])
async def get_partnership_portfolio(
    db: AsyncSession = Depends(get_db)
):
    """Get partnership portfolio by SDG"""
    query = "SELECT * FROM partnerships_by_sdg ORDER BY partnership_count DESC"
    result = await db.execute(query)
    return result.fetchall()


# ===== Dashboard Stats =====

@router.get("/extended-stats")
async def get_extended_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive statistics for all extended data types"""
    
    # Course stats
    course_count = await db.execute(select(func.count(CourseCurriculumModel.course_id)))
    total_enrollment = await db.execute(select(func.sum(CourseCurriculumModel.enrollment_count)))
    
    # Student project stats
    project_count = await db.execute(select(func.count(StudentProjectModel.project_id)))
    projects_with_pubs = await db.execute(
        select(func.count(StudentProjectModel.project_id))
        .where(StudentProjectModel.publication_resulted == True)
    )
    
    # Partnership stats
    partnership_count = await db.execute(select(func.count(CorporatePartnershipModel.partnership_id)))
    total_partnership_funding = await db.execute(
        select(func.sum(CorporatePartnershipModel.funding_amount))
    )
    
    return {
        "courses": {
            "total_courses": course_count.scalar(),
            "total_students_reached": total_enrollment.scalar() or 0
        },
        "student_projects": {
            "total_projects": project_count.scalar(),
            "projects_with_publications": projects_with_pubs.scalar()
        },
        "partnerships": {
            "total_partnerships": partnership_count.scalar(),
            "total_funding": float(total_partnership_funding.scalar() or 0)
        }
    }
