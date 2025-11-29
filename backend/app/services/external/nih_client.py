"""
NIH RePORTER API Client

Fetches grant data from NIH RePORTER public API
https://api.reporter.nih.gov/
"""

import httpx
from typing import List, Dict, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class NIHClient:
    """Client for NIH RePORTER API"""
    
    BASE_URL = os.getenv("NIH_API_BASE", "https://api.reporter.nih.gov/v2")
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_grants(
        self,
        criteria: Dict,
        offset: int = 0,
        limit: int = 100
    ) -> Dict:
        """
        Search for grants using RePORTER API
        
        Args:
            criteria: Search criteria (keywords, fiscal_years, etc.)
            offset: Pagination offset
            limit: Results per page (max 500)
        
        Returns:
            API response with grant data
        
        Example criteria:
        {
            "criteria": {
                "pi_names": [{"any_name": "Smith"}],
                "keywords": ["solar energy"],
                "fiscal_years": [2022, 2023],
                "include_active_projects": True
            },
            "offset": 0,
            "limit": 100,
            "sort_field": "fiscal_year",
            "sort_order": "desc"
        }
        """
        url = f"{self.BASE_URL}/projects/search"
        
        payload = {
            "criteria": criteria,
            "offset": offset,
            "limit": min(limit, 500),  # API max is 500
            "sort_field": "fiscal_year",
            "sort_order": "desc"
        }
        
        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    async def search_by_pi_name(
        self,
        pi_name: str,
        fiscal_years: List[int] = None
    ) -> List[Dict]:
        """
        Search grants by Principal Investigator name
        
        Args:
            pi_name: PI last name or full name
            fiscal_years: Optional list of fiscal years to filter
        
        Returns:
            List of grant records
        """
        # Split name if full name provided
        name_parts = pi_name.split()
        
        criteria = {
            "pi_names": [{
                "last_name": name_parts[-1] if len(name_parts) > 1 else pi_name
            }],
            "include_active_projects": True
        }
        
        if fiscal_years:
            criteria["fiscal_years"] = fiscal_years
        
        result = await self.search_grants(criteria)
        
        return result.get("results", [])
    
    async def search_by_keywords(
        self,
        keywords: List[str],
        fiscal_years: List[int] = None,
        organization: str = "University of Illinois"
    ) -> List[Dict]:
        """
        Search grants by keywords
        
        Args:
            keywords: List of keywords to search
            fiscal_years: Optional fiscal years filter
            organization: Organization name filter
        
        Returns:
            List of grant records
        """
        criteria = {
            "keywords": keywords,
            "include_active_projects": True
        }
        
        if fiscal_years:
            criteria["fiscal_years"] = fiscal_years
        
        if organization:
            criteria["org_names"] = [organization]
        
        result = await self.search_grants(criteria)
        
        return result.get("results", [])
    
    async def get_project_details(self, project_number: str) -> Dict:
        """
        Get detailed information for a specific project
        
        Args:
            project_number: NIH project number (e.g., "5R01CA123456")
        
        Returns:
            Detailed project information
        """
        url = f"{self.BASE_URL}/projects/search"
        
        payload = {
            "criteria": {
                "project_nums": [project_number]
            },
            "offset": 0,
            "limit": 1
        }
        
        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        results = data.get("results", [])
        
        return results[0] if results else None
    
    def parse_grant_record(self, record: Dict) -> Dict:
        """
        Parse NIH grant record into standardized format
        
        Args:
            record: Raw NIH grant record
        
        Returns:
            Standardized grant dictionary
        """
        return {
            "external_id": record.get("project_num"),
            "title": record.get("project_title"),
            "description": record.get("abstract_text"),
            "funder": "NIH",
            "funder_division": record.get("ic_name"),  # Institute/Center
            "program": record.get("program_officer_name"),
            "funding_amount": record.get("award_amount"),
            "start_date": record.get("project_start_date"),
            "end_date": record.get("project_end_date"),
            "award_notice_date": record.get("award_notice_date"),
            "pi_name": " ".join(filter(None, [
                record.get("principal_investigators", [{}])[0].get("first_name"),
                record.get("principal_investigators", [{}])[0].get("last_name")
            ])) if record.get("principal_investigators") else None,
            "organization": record.get("organization", {}).get("org_name"),
            "status": "active" if record.get("is_active") else "completed",
            "keywords": record.get("project_terms", [])
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton instance
_nih_client: Optional[NIHClient] = None


def get_nih_client() -> NIHClient:
    """Get or create singleton NIH client"""
    global _nih_client
    if _nih_client is None:
        _nih_client = NIHClient()
    return _nih_client
