"""
Scopus API Client

Elsevier Scopus API for comprehensive publication data
Requires API key from https://dev.elsevier.com
"""

import httpx
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class ScopusClient:
    """Client for Elsevier Scopus API"""
    
    BASE_URL = "https://api.elsevier.com/content"
    
    def __init__(self, api_key: str = None):
        """
        Initialize Scopus client
        
        Args:
            api_key: Elsevier API key
        """
        self.api_key = api_key or os.getenv("SCOPUS_API_KEY")
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_author(
        self,
        author_name: str,
        affiliation: str = None
    ) -> List[Dict]:
        """
        Search for author by name
        
        Args:
            author_name: Author name
            affiliation: Institution affiliation filter
        
        Returns:
            List of author matches
        """
        query = f"AUTHLAST({author_name.split()[-1]})"
        if affiliation:
            query += f" AND AFFIL({affiliation})"
        
        params = {
            "query": query,
            "apiKey": self.api_key
        }
        
        response = await self.client.get(
            f"{self.BASE_URL}/search/author",
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        return data.get("search-results", {}).get("entry", [])
    
    async def get_author_publications(
        self,
        author_id: str,
        year_start: int = None,
        year_end: int = None
    ) -> List[Dict]:
        """
        Get all publications for an author
        
        Args:
            author_id: Scopus author ID
            year_start: Start year filter
            year_end: End year filter
        
        Returns:
            List of publications
        """
        query = f"AU-ID({author_id})"
        
        if year_start and year_end:
            query += f" AND PUBYEAR > {year_start-1} AND PUBYEAR < {year_end+1}"
        elif year_start:
            query += f" AND PUBYEAR > {year_start-1}"
        
        params = {
            "query": query,
            "apiKey": self.api_key,
            "count": 200
        }
        
        response = await self.client.get(
            f"{self.BASE_URL}/search/scopus",
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        return data.get("search-results", {}).get("entry", [])
    
    async def search_publications(
        self,
        keywords: str,
        affiliation: str = "University of Illinois",
        year_start: int = None
    ) -> List[Dict]:
        """
        Search publications by keywords
        
        Args:
            keywords: Search keywords
            affiliation: Institution filter
            year_start: Start year
        
        Returns:
            List of publications
        """
        query = f"TITLE-ABS-KEY({keywords})"
        
        if affiliation:
            query += f" AND AFFIL({affiliation})"
        
        if year_start:
            query += f" AND PUBYEAR > {year_start-1}"
        
        params = {
            "query": query,
            "apiKey": self.api_key,
            "count": 100
        }
        
        response = await self.client.get(
            f"{self.BASE_URL}/search/scopus",
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        return data.get("search-results", {}).get("entry", [])
    
    async def get_citation_count(self, scopus_id: str) -> Dict:
        """
        Get citation metrics for publication
        
        Args:
            scopus_id: Scopus document ID
        
        Returns:
            Citation metrics
        """
        params = {"apiKey": self.api_key}
        
        response = await self.client.get(
            f"{self.BASE_URL}/abstract/scopus_id/{scopus_id}",
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        abstract = data.get("abstracts-retrieval-response", {})
        
        return {
            "cited_by_count": int(abstract.get("coredata", {}).get("citedby-count", 0)),
            "h_index": None  # Would need author query for this
        }
    
    def parse_publication(self, pub: Dict) -> Dict:
        """
        Parse Scopus publication to standard format
        
        Args:
            pub: Raw publication from Scopus
        
        Returns:
            Standardized publication dict
        """
        return {
            "scopus_id": pub.get("dc:identifier", "").replace("SCOPUS_ID:", ""),
            "title": pub.get("dc:title"),
            "authors": pub.get("dc:creator"),
            "year": pub.get("prism:coverDate", "").split("-")[0] if pub.get("prism:coverDate") else None,
            "venue": pub.get("prism:publicationName"),
            "doi": pub.get("prism:doi"),
            "citations": int(pub.get("citedby-count", 0)),
            "abstract": pub.get("dc:description"),
            "keywords": pub.get("authkeywords", "").split(" | ") if pub.get("authkeywords") else [],
            "source": "Scopus"
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton instance
_scopus_client: Optional[ScopusClient] = None


def get_scopus_client() -> ScopusClient:
    """Get or create singleton Scopus client"""
    global _scopus_client
    if _scopus_client is None:
        _scopus_client = ScopusClient()
    return _scopus_client
