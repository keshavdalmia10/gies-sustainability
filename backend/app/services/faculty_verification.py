"""
Faculty Verification Service

Automated faculty directory scraping and cross-reference validation
for scaling to multiple institutions
"""

import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from dataclasses import dataclass
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models import Faculty
from uuid import UUID


@dataclass
class FacultyMatch:
    """Faculty verification match result"""
    name: str
    department: str
    title: Optional[str]
    email: Optional[str]
    profile_url: Optional[str]
    confidence_score: float
    source: str


class FacultyVerificationService:
    """
    Service for verifying faculty affiliations and status
    
    Scrapes university directories and cross-references with database
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
    
    async def scrape_uiuc_directory(
        self,
        department: str = None
    ) -> List[FacultyMatch]:
        """
        Scrape University of Illinois faculty directory
        
        Args:
            department: Optional department filter
        
        Returns:
            List of faculty matches
        """
        # UIUC Gies College directory
        base_url = "https://giesbusiness.illinois.edu/people/directory"
        
        try:
            response = await self.client.get(base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            faculty_matches = []
            
            # Find faculty listings (this is a simplified example)
            # Real implementation would need to match the actual HTML structure
            faculty_cards = soup.find_all('div', class_='faculty-card')
            
            for card in faculty_cards:
                name_elem = card.find('h3', class_='name')
                dept_elem = card.find('span', class_='department')
                title_elem = card.find('span', class_='title')
                email_elem = card.find('a', class_='email')
                profile_elem = card.find('a', class_='profile-link')
                
                if name_elem:
                    match = FacultyMatch(
                        name=name_elem.text.strip(),
                        department=dept_elem.text.strip() if dept_elem else "",
                        title=title_elem.text.strip() if title_elem else None,
                        email=email_elem['href'].replace('mailto:', '') if email_elem else None,
                        profile_url=profile_elem['href'] if profile_elem else None,
                        confidence_score=1.0,  # Direct from source
                        source="UIUC Gies Directory"
                    )
                    
                    if not department or department.lower() in match.department.lower():
                        faculty_matches.append(match)
            
            return faculty_matches
        
        except Exception as e:
            print(f"Error scraping directory: {e}")
            return []
    
    async def verify_faculty_status(
        self,
        faculty_name: str,
        institution: str = "University of Illinois"
    ) -> Dict:
        """
        Verify if faculty member is currently active at institution
        
        Args:
            faculty_name: Faculty member name
            institution: Institution name
        
        Returns:
            Verification result with confidence score
        """
        # Try to find in directory
        matches = await self.scrape_uiuc_directory()
        
        # Fuzzy match on name
        best_match = None
        best_score = 0.0
        
        for match in matches:
            score = self._calculate_name_similarity(faculty_name, match.name)
            if score > best_score and score > 0.7:
                best_score = score
                best_match = match
        
        return {
            "verified": best_score > 0.8,
            "confidence": best_score,
            "current_status": "Active" if best_score > 0.8 else "Unknown",
            "match_details": best_match.__dict__ if best_match else None,
            "verification_date": "2024-01-01",  # Current date in production
            "source": "University Directory"
        }
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two names
        
        Uses simple token matching (production would use Levenshtein distance)
        
        Args:
            name1: First name
            name2: Second name
        
        Returns:
            Similarity score 0-1
        """
        # Normalize
        tokens1 = set(re.findall(r'\w+', name1.lower()))
        tokens2 = set(re.findall(r'\w+', name2.lower()))
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        
        return intersection / union if union > 0 else 0.0
    
    async def cross_reference_with_database(
        self,
        session: AsyncSession,
        directory_matches: List[FacultyMatch]
    ) -> Dict:
        """
        Cross-reference directory data with database
        
        Args:
            session: Database session
            directory_matches: Matches from directory scraping
        
        Returns:
            Status report with matches and discrepancies
        """
        matched = []
        new_faculty = []
        inactive = []
        
        # Get all faculty from database
        result = await session.execute(select(Faculty))
        db_faculty = result.scalars().all()
        
        # Create name index
        db_names = {f.name: f for f in db_faculty}
        directory_names = {m.name: m for m in directory_matches}
        
        # Find matches
        for name, match in directory_names.items():
            if name in db_names:
                matched.append({
                    "name": name,
                    "in_database": True,
                    "in_directory": True,
                    "status": "Verified"
                })
            else:
                # Check for fuzzy match
                best_match = None
                best_score = 0.0
                
                for db_name in db_names.keys():
                    score = self._calculate_name_similarity(name, db_name)
                    if score > best_score:
                        best_score = score
                        best_match = db_name
                
                if best_score > 0.8:
                    matched.append({
                        "name": name,
                        "database_name": best_match,
                        "similarity": best_score,
                        "status": "Fuzzy Match"
                    })
                else:
                    new_faculty.append({
                        "name": name,
                        "department": match.department,
                        "status": "Not in Database"
                    })
        
        # Find potentially inactive faculty
        for name, faculty in db_names.items():
            if name not in directory_names:
                # Check for fuzzy match
                found = False
                for dir_name in directory_names.keys():
                    if self._calculate_name_similarity(name, dir_name) > 0.8:
                        found = True
                        break
                
                if not found:
                    inactive.append({
                        "name": name,
                        "uuid": str(faculty.person_uuid),
                        "status": "Possibly Inactive"
                    })
        
        return {
            "total_directory": len(directory_matches),
            "total_database": len(db_faculty),
            "matched": len(matched),
            "new_faculty": len(new_faculty),
            "potentially_inactive": len(inactive),
            "matches": matched,
            "new_faculty_list": new_faculty,
            "potentially_inactive_list": inactive
        }
    
    async def update_faculty_status(
        self,
        session: AsyncSession,
        faculty_uuid: UUID,
        is_active: bool
    ):
        """
        Update faculty active status in database
        
        Args:
            session: Database session
            faculty_uuid: Faculty UUID
            is_active: Whether faculty is active
        """
        await session.execute(
            update(Faculty)
            .where(Faculty.person_uuid == faculty_uuid)
            .values(is_active=is_active)
        )
        await session.commit()
    
    async def automated_verification_pipeline(
        self,
        session: AsyncSession,
        institution: str = "University of Illinois"
    ) -> Dict:
        """
        Run complete automated verification pipeline
        
        1. Scrape directory
        2. Cross-reference with database
        3. Generate report
        
        Args:
            session: Database session
            institution: Institution name
        
        Returns:
            Verification report
        """
        # Scrape directory
        directory_matches = await self.scrape_uiuc_directory()
        
        # Cross-reference
        report = await self.cross_reference_with_database(session, directory_matches)
        
        report["institution"] = institution
        report["recommendations"] = []
        
        if report["new_faculty"]:
            report["recommendations"].append(
                f"Add {len(report['new_faculty'])} new faculty to database"
            )
        
        if report["potentially_inactive"]:
            report["recommendations"].append(
                f"Review {len(report['potentially_inactive'])} potentially inactive faculty"
            )
        
        return report
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton instance
_verification_service: Optional[FacultyVerificationService] = None


def get_faculty_verification_service() -> FacultyVerificationService:
    """Get or create singleton verification service"""
    global _verification_service
    if _verification_service is None:
        _verification_service = FacultyVerificationService()
    return _verification_service
