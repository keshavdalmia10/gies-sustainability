"""
Data Source Management API Router

Endpoints for managing and comparing publication data sources
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from pydantic import BaseModel

from app.services.data_quality import (
    get_source_comparison,
    recommend_source,
    get_cost_benefit_analysis,
    DataSource,
    DATA_SOURCE_COMPARISON
)
from app.services.external import (
    get_google_scholar_client,
    get_scopus_client,
    get_wos_client
)

router = APIRouter()


class SourceRecommendationRequest(BaseModel):
    use_case: str


class DataSourceInfo(BaseModel):
    source: str
    pros: List[str]
    cons: List[str]
    cost: str
    api_complexity: str
    overall_quality_score: float
    best_for: List[str]
    update_frequency: str
    authentication: str


@router.get("/sources", response_model=List[DataSourceInfo])
async def get_all_sources():
    """
    Get comprehensive comparison of all data sources
    
    Returns detailed pros/cons, costs, and quality metrics for:
    - Google Scholar
    - Scopus
    - Web of Science
    - NIH RePORTER
    - NSF Awards
    - USPTO PatentsView
    """
    comparison = get_source_comparison()
    
    result = []
    for source, info in comparison.items():
        result.append(DataSourceInfo(
            source=source.value,
            pros=info["pros"],
            cons=info["cons"],
            cost=info["cost"],
            api_complexity=info["api_complexity"],
            overall_quality_score=info["data_quality"].overall_score,
            best_for=info["best_for"],
            update_frequency=info["update_frequency"],
            authentication=info["authentication"]
        ))
    
    return result


@router.get("/sources/{source_name}")
async def get_source_details(source_name: str):
    """
    Get detailed information about a specific data source
    
    Args:
        source_name: One of google_scholar, scopus, web_of_science, nih, nsf, uspto
    """
    # Map URL-friendly names to enum
    source_map = {
        "google_scholar": DataSource.GOOGLE_SCHOLAR,
        "scopus": DataSource.SCOPUS,
        "web_of_science": DataSource.WEB_OF_SCIENCE,
        "nih": DataSource.NIH_REPORTER,
        "nsf": DataSource.NSF_AWARDS,
        "uspto": DataSource.USPTO
    }
    
    source = source_map.get(source_name.lower())
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    comparison = get_source_comparison()
    info = comparison[source]
    
    # Add quality metrics breakdown
    quality = info["data_quality"]
    
    return {
        "source": source.value,
        "overview": info,
        "quality_metrics": {
            "completeness": quality.completeness,
            "accuracy": quality.accuracy,
            "timeliness": quality.timeliness,
            "consistency": quality.consistency,
            "coverage": quality.coverage,
            "overall_score": quality.overall_score
        }
    }


@router.post("/sources/recommend")
async def recommend_sources(request: SourceRecommendationRequest):
    """
    Get source recommendations for a specific use case
    
    Examples:
    - "citation analysis"
    - "grant tracking"
    - "comprehensive exploratory search"
    - "tenure evaluation"
    - "patent analysis"
    """
    recommendations = recommend_source(request.use_case)
    
    return {
        "use_case": request.use_case,
        "recommended_sources": [source.value for source in recommendations],
        "explanation": f"Based on the use case '{request.use_case}', these sources provide the best balance of coverage, quality, and cost."
    }


@router.get("/cost-benefit-analysis")
async def get_cost_analysis():
    """
    Get cost-benefit analysis for scaling to multiple institutions
    
    Returns recommendations for:
    - Single institution
    - 5 institutions
    - 20+ institutions
    - National scale
    """
    return get_cost_benefit_analysis()


@router.get("/quality-comparison")
async def get_quality_comparison():
    """
    Get side-by-side quality metrics comparison
    
    Returns quality scores across all dimensions for easy comparison
    """
    comparison = get_source_comparison()
    
    result = {}
    for source, info in comparison.items():
        quality = info["data_quality"]
        result[source.value] = {
            "completeness": quality.completeness,
            "accuracy": quality.accuracy,
            "timeliness": quality.timeliness,
            "consistency": quality.consistency,
            "coverage": quality.coverage,
            "overall_score": quality.overall_score
        }
    
    return result


@router.get("/search-test/{source}")
async def test_source_search(
    source: str,
    query: str = "solar energy",
    author: str = None
):
    """
    Test search functionality for a specific source
    
    Useful for demonstrating API integration and data quality
    
    Args:
        source: google_scholar, scopus, or web_of_science
        query: Search query
        author: Optional author filter
    """
    try:
        if source == "google_scholar":
            client = get_google_scholar_client()
            if author:
                results = await client.search_author(author, limit=5)
            else:
                results = await client.search_publications(query, limit=5)
            
            return {
                "source": "Google Scholar",
                "query": query,
                "results_count": len(results),
                "sample_results": results[:3]
            }
        
        elif source == "scopus":
            client = get_scopus_client()
            if author:
                results = await client.search_author(author)
            else:
                results = await client.search_publications(query)
            
            return {
                "source": "Scopus",
                "query": query,
                "results_count": len(results),
                "sample_results": results[:3]
            }
        
        elif source == "web_of_science":
            client = get_wos_client()
            if author:
                results = await client.search_by_author(author)
            else:
                results = await client.search_by_keywords(query)
            
            return {
                "source": "Web of Science",
                "query": query,
                "results_count": len(results),
                "sample_results": results[:3]
            }
        
        else:
            raise HTTPException(status_code=400, detail="Invalid source. Use: google_scholar, scopus, or web_of_science")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/integration-status")
async def get_integration_status():
    """
    Get status of all data source integrations
    
    Shows which sources are configured and ready to use
    """
    import os
    
    return {
        "google_scholar": {
            "implemented": True,
            "api_key_configured": bool(os.getenv("SERPAPI_KEY")),
            "status": "Ready" if os.getenv("SERPAPI_KEY") else "Needs API key"
        },
        "scopus": {
            "implemented": True,
            "api_key_configured": bool(os.getenv("SCOPUS_API_KEY")),
            "status": "Ready" if os.getenv("SCOPUS_API_KEY") else "Needs API key"
        },
        "web_of_science": {
            "implemented": True,
            "api_key_configured": bool(os.getenv("WOS_API_KEY")),
            "status": "Ready" if os.getenv("WOS_API_KEY") else "Needs API key"
        },
        "nih_reporter": {
            "implemented": True,
            "api_key_configured": True,
            "status": "Ready (no key required)"
        },
        "nsf_awards": {
            "implemented": True,
            "api_key_configured": True,
            "status": "Ready (no key required)"
        },
        "uspto": {
            "implemented": True,
            "api_key_configured": True,
            "status": "Ready (no key required)"
        }
    }
