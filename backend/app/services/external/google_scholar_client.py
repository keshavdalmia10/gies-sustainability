"""
Google Scholar API Client using SerpAPI

Google Scholar doesn't have an official API, so we use SerpAPI as a reliable proxy.
SerpAPI provides structured JSON results from Google Scholar.
"""

import httpx
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class GoogleScholarClient:
    """Client for Google Scholar via SerpAPI"""
    
    BASE_URL = "https://serpapi.com/search"
    
    def __init__(self, api_key: str = None):
        """
        Initialize Google Scholar client
        
        Args:
            api_key: SerpAPI key (get from https://serpapi.com)
        """
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_author(
        self,
        author_name: str,
        limit: int = 20
    ) -> Dict:
        """
        Search for author publications
        
        Args:
            author_name: Author name to search
            limit: Number of results to return
        
        Returns:
            Dictionary with author profile and publications
        """
        params = {
            "engine": "google_scholar_author",
            "author": author_name,
            "api_key": self.api_key,
            "num": limit
        }
        
        response = await self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        
        return response.json()
    
    async def search_publications(
        self,
        query: str,
        year_start: int = None,
        year_end: int = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Search for publications by keyword
        
        Args:
            query: Search query
            year_start: Start year filter
            year_end: End year filter
            limit: Number of results
        
        Returns:
            List of publications
        """
        # Build query with year filters
        full_query = query
        if year_start and year_end:
            full_query = f"{query} after:{year_start} before:{year_end}"
        elif year_start:
            full_query = f"{query} after:{year_start}"
        
        params = {
            "engine": "google_scholar",
            "q": full_query,
            "api_key": self.api_key,
            "num": limit
        }
        
        response = await self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get("organic_results", [])
    
    async def get_citation_count(self, scholar_id: str) -> Dict:
        """
        Get citation metrics for author
        
        Args:
            scholar_id: Google Scholar author ID
        
        Returns:
            Citation metrics
        """
        params = {
            "engine": "google_scholar_author",
            "author_id": scholar_id,
            "api_key": self.api_key
        }
        
        response = await self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get("cited_by", {})
    
    def parse_publication(self, pub: Dict) -> Dict:
        """
        Parse Google Scholar publication to standard format
        
        Args:
            pub: Raw publication from Google Scholar
        
        Returns:
            Standardized publication dict
        """
        return {
            "title": pub.get("title"),
            "authors": pub.get("publication_info", {}).get("authors", []),
            "year": pub.get("publication_info", {}).get("summary", "").split(",")[-1].strip() if pub.get("publication_info") else None,
            "venue": pub.get("publication_info", {}).get("summary", "").split("-")[0].strip() if pub.get("publication_info") else None,
            "citations": pub.get("inline_links", {}).get("cited_by", {}).get("total", 0),
            "link": pub.get("link"),
            "snippet": pub.get("snippet"),
            "source": "Google Scholar"
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton instance
_scholar_client: Optional[GoogleScholarClient] = None


def get_google_scholar_client() -> GoogleScholarClient:
    """Get or create singleton Google Scholar client"""
    global _scholar_client
    if _scholar_client is None:
        _scholar_client = GoogleScholarClient()
    return _scholar_client
