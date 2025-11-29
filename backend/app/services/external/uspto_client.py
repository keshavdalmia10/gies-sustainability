"""
USPTO PatentsView API Client

Fetches patent data from USPTO PatentsView public API
https://patentsview.org/apis/api-endpoints
"""

import httpx
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class USPTOClient:
    """Client for USPTO PatentsView API"""
    
    BASE_URL = os.getenv("USPTO_API_BASE", "https://api.patentsview.org/patents/query")
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_patents(
        self,
        query: Dict,
        fields: List[str] = None,
        options: Dict = None
    ) -> Dict:
        """
        Search for patents
        
        Args:
            query: Search query (PatentsView query syntax)
            fields: List of fields to return
            options: Pagination and sorting options
        
        Returns:
            API response with patent data
        
        Example query:
        {
            "_and": [
                {"_gte": {"patent_date": "2020-01-01"}},
                {"_text_phrase": {"patent_abstract": "solar energy"}}
            ]
        }
        """
        if fields is None:
            fields = [
                "patent_number",
                "patent_title",
                "patent_abstract",
                "patent_date",
                "inventor_last_name",
                "inventor_first_name",
                "assignee_organization",
                "cpc_group_id"
            ]
        
        if options is None:
            options = {
                "page": 1,
                "per_page": 100
            }
        
        params = {
            "q": query,
            "f": fields,
            "o": options
        }
        
        response = await self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        
        return response.json()
    
    async def search_by_inventor(
        self,
        inventor_last_name: str,
        inventor_first_name: str = None,
        year_start: int = None
    ) -> List[Dict]:
        """
        Search patents by inventor name
        
        Args:
            inventor_last_name: Inventor last name
            inventor_first_name: Optional first name
            year_start: Optional start year
        
        Returns:
            List of patent records
        """
        query_parts = [
            {"_eq": {"inventor_last_name": inventor_last_name}}
        ]
        
        if inventor_first_name:
            query_parts.append({
                "_eq": {"inventor_first_name": inventor_first_name}
            })
        
        if year_start:
            query_parts.append({
                "_gte": {"patent_date": f"{year_start}-01-01"}
            })
        
        query = {"_and": query_parts} if len(query_parts) > 1 else query_parts[0]
        
        result = await self.search_patents(query)
        
        return result.get("patents", [])
    
    async def search_by_assignee(
        self,
        assignee: str = "University of Illinois",
        year_start: int = None
    ) -> List[Dict]:
        """
        Search patents by assignee (organization)
        
        Args:
            assignee: Organization name
            year_start: Optional start year
        
        Returns:
            List of patent records
        """
        query_parts = [
            {"_text_phrase": {"assignee_organization": assignee}}
        ]
        
        if year_start:
            query_parts.append({
                "_gte": {"patent_date": f"{year_start}-01-01"}
            })
        
        query = {"_and": query_parts} if len(query_parts) > 1 else query_parts[0]
        
        result = await self.search_patents(query)
        
        return result.get("patents", [])
    
    async def search_by_keywords(
        self,
        keywords: str,
        assignee: str = "University of Illinois"
    ) -> List[Dict]:
        """
        Search patents by keywords in abstract or title
        
        Args:
            keywords: Keywords to search
            assignee: Organization filter
        
        Returns:
            List of patent records
        """
        query = {
            "_and": [
                {"_text_phrase": {"assignee_organization": assignee}},
                {"_or": [
                    {"_text_phrase": {"patent_abstract": keywords}},
                    {"_text_phrase": {"patent_title": keywords}}
                ]}
            ]
        }
        
        result = await self.search_patents(query)
        
        return result.get("patents", [])
    
    def parse_patent_record(self, record: Dict) -> Dict:
        """
        Parse USPTO patent record into standardized format
        
        Args:
            record: Raw USPTO patent record
        
        Returns:
            Standardized patent dictionary
        """
        # Extract inventors
        inventors = record.get("inventors", [])
        inventor_names = [
            f"{inv.get('inventor_first_name', '')} {inv.get('inventor_last_name', '')}".strip()
            for inv in inventors
        ]
        
        # Extract CPC codes
        cpc_codes = [
            cpc.get("cpc_group_id")
            for cpc in record.get("cpcs", [])
            if cpc.get("cpc_group_id")
        ]
        
        return {
            "patent_number": record.get("patent_number"),
            "title": record.get("patent_title"),
            "description": record.get("patent_abstract"),
            "assignee": record.get("assignees", [{}])[0].get("assignee_organization") if record.get("assignees") else None,
            "grant_date": record.get("patent_date"),
            "filing_date": record.get("app_date"),
            "classification_codes": cpc_codes,
            "inventors": inventor_names,
            "citations_count": len(record.get("citedby_patents", [])) if record.get("citedby_patents") else 0,
            "status": "granted"
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton instance
_uspto_client: Optional[USPTOClient] = None


def get_uspto_client() -> USPTOClient:
    """Get or create singleton USPTO client"""
    global _uspto_client
    if _uspto_client is None:
        _uspto_client = USPTOClient()
    return _uspto_client
