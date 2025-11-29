"""
NSF Awards API Client

Fetches grant data from NSF Awards API
https://www.research.gov/common/webapi/awardapisearch-v1.htm
"""

import httpx
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

load_dotenv()


class NSFClient:
    """Client for NSF Awards API"""
    
    BASE_URL = os.getenv("NSF_API_BASE", "https://www.research.gov/awardapi-service/v1/awards.json")
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_awards(
        self,
        keywords: str = None,
        pi_name: str = None,
        institution: str = None,
        start_date: str = None,
        end_date: str = None,
        offset: int = 1,
        limit: int = 25
    ) -> Dict:
        """
        Search for NSF awards
        
        Args:
            keywords: Keywords to search in title/abstract
            pi_name: Principal Investigator name
            institution: Institution name
            start_date: Start date (YYYY or MM/DD/YYYY)
            end_date: End date (YYYY or MM/DD/YYYY)
            offset: Pagination offset (1-indexed)
            limit: Results per page (max 25)
        
        Returns:
            API response with award data
        """
        params = {
            "offset": offset,
            "printFields": "agency,id,title,piFirstName,piLastName,date,startDate,expDate,fundsObligatedAmt,abstractText"
        }
        
        if keywords:
            params["keyword"] = keywords
        if pi_name:
            params["pdPIName"] = pi_name
        if institution:
            params["rpp"] = institution
        if start_date:
            params["dateStart"] = start_date
        if end_date:
            params["dateEnd"] = end_date
        
        response = await self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        
        return response.json()
    
    async def search_by_pi(
        self,
        pi_name: str,
        year_start: int = None,
        year_end: int = None
    ) -> List[Dict]:
        """
        Search awards by PI name
        
        Args:
            pi_name: PI last name or full name
            year_start: Start year filter
            year_end: End year filter
        
        Returns:
            List of award records
        """
        result = await self.search_awards(
            pi_name=pi_name,
            start_date=str(year_start) if year_start else None,
            end_date=str(year_end) if year_end else None
        )
        
        return result.get("response", {}).get("award", [])
    
    async def search_by_keywords(
        self,
        keywords: str,
        institution: str = "University of Illinois"
    ) -> List[Dict]:
        """
        Search awards by keywords
        
        Args:
            keywords: Keywords to search
            institution: Institution filter
        
        Returns:
            List of award records
        """
        result = await self.search_awards(
            keywords=keywords,
            institution=institution
        )
        
        return result.get("response", {}).get("award", [])
    
    async def get_award_details(self, award_id: str) -> Dict:
        """
        Get detailed information for a specific award
        
        Args:
            award_id: NSF award ID (e.g., "2145678")
        
        Returns:
            Detailed award information
        """
        result = await self.search_awards()
        awards = result.get("response", {}).get("award", [])
        
        # Find matching award
        for award in awards:
            if award.get("id") == award_id:
                return award
        
        return None
    
    def parse_award_record(self, record: Dict) -> Dict:
        """
        Parse NSF award record into standardized format
        
        Args:
            record: Raw NSF award record
        
        Returns:
            Standardized grant dictionary
        """
        return {
            "external_id": record.get("id"),
            "title": record.get("title"),
            "description": record.get("abstractText"),
            "funder": "NSF",
            "funder_division": record.get("agency"),
            "program": record.get("programElement", {}).get("text") if isinstance(record.get("programElement"), dict) else None,
            "funding_amount": float(record.get("fundsObligatedAmt", 0)),
            "start_date": record.get("startDate"),
            "end_date": record.get("expDate"),
            "award_notice_date": record.get("date"),
            "pi_name": f"{record.get('piFirstName', '')} {record.get('piLastName', '')}".strip(),
            "organization": record.get("institution", {}).get("name") if isinstance(record.get("institution"), dict) else None,
            "status": "active" if record.get("expDate") else "completed",
            "keywords": []
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton instance
_nsf_client: Optional[NSFClient] = None


def get_nsf_client() -> NSFClient:
    """Get or create singleton NSF client"""
    global _nsf_client
    if _nsf_client is None:
        _nsf_client = NSFClient()
    return _nsf_client
