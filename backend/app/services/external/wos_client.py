"""
Web of Science API Client

Clarivate Web of Science API for high-quality publication data
Requires API key from https://developer.clarivate.com
"""

import httpx
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class WebOfScienceClient:
    """Client for Clarivate Web of Science API"""
    
    BASE_URL = "https://api.clarivate.com/api/wos"
    
    def __init__(self, api_key: str = None):
        """
        Initialize Web of Science client
        
        Args:
            api_key: Clarivate API key
        """
        self.api_key = api_key or os.getenv("WOS_API_KEY")
        self.client = httpx.AsyncClient(timeout=30.0)
        self.client.headers.update({"X-ApiKey": self.api_key})
    
    async def search_publications(
        self,
        query: str,
        database: str = "WOS",
        count: int = 100,
        first_record: int = 1
    ) -> Dict:
        """
        Search publications using WoS query language
        
        Args:
            query: WoS query (e.g., "AU=Smith AND OG=University of Illinois")
            database: Database to search (WOS, BIOSIS, etc.)
            count: Number of records to return
            first_record: Starting record number
        
        Returns:
            Search results
        """
        params = {
            "databaseId": database,
            "usrQuery": query,
            "count": min(count, 100),  # Max 100 per request
            "firstRecord": first_record
        }
        
        response = await self.client.get(
            f"{self.BASE_URL}/query",
            params=params
        )
        response.raise_for_status()
        
        return response.json()
    
    async def search_by_author(
        self,
        author_name: str,
        organization: str = "University of Illinois",
        year_start: int = None
    ) -> List[Dict]:
        """
        Search publications by author
        
        Args:
            author_name: Author name
            organization: Organization filter
            year_start: Start year
        
        Returns:
            List of publications
        """
        # Build WoS query
        last_name = author_name.split()[-1]
        query = f"AU={last_name}"
        
        if organization:
            query += f" AND OG={organization}"
        
        if year_start:
            query += f" AND PY={year_start}-{year_start + 10}"
        
        results = await self.search_publications(query)
        
        return results.get("Data", {}).get("Records", {}).get("records", {}).get("REC", [])
    
    async def search_by_keywords(
        self,
        keywords: str,
        organization: str = "University of Illinois",
        year_start: int = None
    ) -> List[Dict]:
        """
        Search publications by keywords
        
        Args:
            keywords: Search keywords
            organization: Organization filter
            year_start: Start year
        
        Returns:
            List of publications
        """
        query = f"TS=({keywords})"
        
        if organization:
            query += f" AND OG={organization}"
        
        if year_start:
            query += f" AND PY={year_start}-2024"
        
        results = await self.search_publications(query)
        
        return results.get("Data", {}).get("Records", {}).get("records", {}).get("REC", [])
    
    async def get_citation_report(
        self,
        unique_ids: List[str]
    ) -> Dict:
        """
        Get citation report for publications
        
        Args:
            unique_ids: List of WoS unique IDs
        
        Returns:
            Citation report
        """
        payload = {
            "databaseId": "WOS",
            "uniqueIds": unique_ids
        }
        
        response = await self.client.post(
            f"{self.BASE_URL}/citations",
            json=payload
        )
        response.raise_for_status()
        
        return response.json()
    
    def parse_publication(self, pub: Dict) -> Dict:
        """
        Parse WoS publication to standard format
        
        Args:
            pub: Raw publication from WoS
        
        Returns:
            Standardized publication dict
        """
        static = pub.get("static_data", {})
        summary = static.get("summary", {})
        titles = summary.get("titles", {}).get("title", [])
        
        # Extract title
        title = None
        for t in titles if isinstance(titles, list) else [titles]:
            if t.get("type") == "item":
                title = t.get("content")
                break
        
        # Extract authors
        names = summary.get("names", {}).get("name", [])
        authors = []
        for name in names if isinstance(names, list) else [names]:
            if name.get("role") == "author":
                full_name = name.get("full_name") or f"{name.get('first_name', '')} {name.get('last_name', '')}".strip()
                authors.append(full_name)
        
        return {
            "wos_id": pub.get("UID"),
            "title": title,
            "authors": authors,
            "year": summary.get("pub_info", {}).get("pubyear"),
            "venue": summary.get("pub_info", {}).get("coverdate"),
            "doi": None,  # Would need to extract from identifiers
            "citations": None,  # Would need separate citation query
            "abstract": None,  # Not in standard query
            "source": "Web of Science"
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton instance
_wos_client: Optional[WebOfScienceClient] = None


def get_wos_client() -> WebOfScienceClient:
    """Get or create singleton Web of Science client"""
    global _wos_client
    if _wos_client is None:
        _wos_client = WebOfScienceClient()
    return _wos_client
