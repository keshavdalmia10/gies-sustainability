"""
Faculty Verification API Router

Endpoints for faculty verification and directory scraping
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from uuid import UUID
from pydantic import BaseModel

from app.database import get_db
from app.services.faculty_verification import get_faculty_verification_service

router = APIRouter()


class VerifyFacultyRequest(BaseModel):
    faculty_name: str
    institution: str = "University of Illinois"


class UpdateStatusRequest(BaseModel):
    faculty_uuid: UUID
    is_active: bool


@router.get("/scrape-directory")
async def scrape_directory(
    department: str = None
):
    """
    Scrape university faculty directory
    
    Returns current faculty listings from university website
    """
    service = get_faculty_verification_service()
    
    try:
        matches = await service.scrape_uiuc_directory(department)
        
        return {
            "source": "UIUC Gies Directory",
            "department": department or "All",
            "faculty_count": len(matches),
            "faculty": [
                {
                    "name": m.name,
                    "department": m.department,
                    "title": m.title,
                    "email": m.email,
                    "profile_url": m.profile_url
                }
                for m in matches
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Directory scraping failed: {str(e)}")


@router.post("/verify-faculty")
async def verify_faculty(request: VerifyFacultyRequest):
    """
    Verify if faculty member is currently active at institution
    
    Checks university directory and returns verification status
    """
    service = get_faculty_verification_service()
    
    result = await service.verify_faculty_status(
        faculty_name=request.faculty_name,
        institution=request.institution
    )
    
    return result


@router.get("/cross-reference")
async def cross_reference_database(
    db: AsyncSession = Depends(get_db)
):
    """
    Cross-reference database with university directory
    
    Identifies:
    - Verified active faculty
    - New faculty not in database
    - Potentially inactive faculty
    """
    service = get_faculty_verification_service()
    
    try:
        # Scrape directory
        directory_matches = await service.scrape_uiuc_directory()
        
        # Cross-reference
        report = await service.cross_reference_with_database(db, directory_matches)
        
        return report
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cross-reference failed: {str(e)}")


@router.post("/update-status")
async def update_faculty_status(
    request: UpdateStatusRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update faculty active status
    
    Manually set faculty as active/inactive based on verification
    """
    service = get_faculty_verification_service()
    
    try:
        await service.update_faculty_status(
            session=db,
            faculty_uuid=request.faculty_uuid,
            is_active=request.is_active
        )
        
        return {
            "faculty_uuid": str(request.faculty_uuid),
            "is_active": request.is_active,
            "status": "Updated successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status update failed: {str(e)}")


@router.get("/automated-verification")
async def run_automated_verification(
    db: AsyncSession = Depends(get_db)
):
    """
    Run complete automated verification pipeline
    
    1. Scrapes university directory
    2. Cross-references with database
    3. Generates recommendations
    
    This should be run periodically (e.g., monthly) to keep data current
    """
    service = get_faculty_verification_service()
    
    try:
        report = await service.automated_verification_pipeline(
            session=db,
            institution="University of Illinois"
        )
        
        return report
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification pipeline failed: {str(e)}")


@router.get("/verification-guide")
async def get_verification_guide():
    """
    Get guide for implementing faculty verification for other institutions
    
    Returns implementation instructions and best practices
    """
    return {
        "title": "Faculty Verification Implementation Guide",
        "overview": "How to implement faculty verification for your institution",
        "steps": [
            {
                "step": 1,
                "title": "Analyze Directory Structure",
                "description": "Inspect your institution's faculty directory HTML structure",
                "tools": ["Browser DevTools", "Beautiful Soup"]
            },
            {
                "step": 2,
                "title": "Customize Scraper",
                "description": "Modify the scraping logic to match your directory's HTML",
                "file": "app/services/faculty_verification.py",
                "method": "scrape_uiuc_directory"
            },
            {
                "step": 3,
                "title": "Test Scraping",
                "description": "Run GET /verification/scrape-directory to test",
                "expected": "List of faculty with names, departments, emails"
            },
            {
                "step": 4,
                "title": "Run Cross-Reference",
                "description": "Compare directory with database",
                "endpoint": "GET /verification/cross-reference"
            },
            {
                "step": 5,
                "title": "Review Matches",
                "description": "Manually review fuzzy matches and new faculty"
            },
            {
                "step": 6,
                "title": "Automate",
                "description": "Set up monthly cron job for verification",
                "command": "curl -X GET http://your-api/api/v1/verification/automated-verification"
            }
        ],
        "best_practices": [
            "Respect robots.txt and rate limits when scraping",
            "Cache directory results to reduce load",
            "Use fuzzy matching for name variations (Dr., PhD, etc.)",
            "Manual review required for confidence < 0.8",
            "Keep verification history for audit trail"
        ],
        "alternative_approaches": [
            "University API integration (if available)",
            "LDAP/Active Directory integration",
            "HR system integration",
            "Manual CSV upload with periodic updates"
        ]
    }
