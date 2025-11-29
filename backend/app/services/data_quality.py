"""
Data Source Comparison & Quality Scoring

Comprehensive analysis of publication data sources and quality assessment framework
"""

from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class DataSource(Enum):
    """Supported data sources"""
    GOOGLE_SCHOLAR = "Google Scholar"
    SCOPUS = "Scopus"
    WEB_OF_SCIENCE = "Web of Science"
    NIH_REPORTER = "NIH RePORTER"
    NSF_AWARDS = "NSF Awards"
    USPTO = "USPTO PatentsView"


@dataclass
class DataQualityMetrics:
    """Data quality assessment metrics"""
    completeness: float  # 0-1, % of expected fields populated
    accuracy: float  # 0-1, estimated accuracy
    timeliness: float  # 0-1, how current the data is
    consistency: float  # 0-1, internal consistency
    coverage: float  # 0-1, scope of data coverage
    
    @property
    def overall_score(self) -> float:
        """Weighted overall quality score"""
        return (
            self.completeness * 0.25 +
            self.accuracy * 0.30 +
            self.timeliness * 0.15 +
            self.consistency * 0.15 +
            self.coverage * 0.15
        )


# Comprehensive source comparison
DATA_SOURCE_COMPARISON = {
    DataSource.GOOGLE_SCHOLAR: {
        "pros": [
            "Broadest coverage - includes preprints, theses, books",
            "Free to use (via SerpAPI)",
            "Simple API through SerpAPI",
            "Citation metrics included",
            "Fast updates for new publications",
            "Multidisciplinary coverage"
        ],
        "cons": [
            "Lower data quality - may include duplicates",
            "Limited metadata (no abstracts, keywords often missing)",
            "No controlled vocabulary or subject classification",
            "Rate limits on SerpAPI free tier",
            "Less reliable for systematic reviews",
            "Citation counts can be inflated"
        ],
        "cost": "Free with SerpAPI (100 searches/month), then $50/month",
        "api_complexity": "Low - simple REST API",
        "data_quality": DataQualityMetrics(
            completeness=0.65,
            accuracy=0.70,
            timeliness=0.95,
            consistency=0.60,
            coverage=0.95
        ),
        "best_for": [
            "Broad exploratory searches",
            "Citation tracking",
            "Grey literature",
            "Multidisciplinary research"
        ],
        "update_frequency": "Daily",
        "authentication": "SerpAPI key required"
    },
    
    DataSource.SCOPUS: {
        "pros": [
            "High-quality curated data",
            "Comprehensive metadata (abstracts, keywords, affiliations)",
            "Author disambiguation and profiles",
            "Strong coverage in STEM and social sciences",
            "Subject area classifications",
            "H-index and other bibliometrics"
        ],
        "cons": [
            "Expensive ($5,000-50,000/year institutional)",
            "Limited humanities coverage",
            "Complex API with learning curve",
            "Fewer preprints than Google Scholar",
            "Author IDs not always accurate",
            "Rate limits on API calls"
        ],
        "cost": "$5,000-50,000/year (institutional), free API with limits",
        "api_complexity": "Medium - well-documented REST API",
        "data_quality": DataQualityMetrics(
            completeness=0.90,
            accuracy=0.90,
            timeliness=0.85,
            consistency=0.90,
            coverage=0.75
        ),
        "best_for": [
            "Systematic reviews",
            "Bibliometric analysis",
            "Research evaluation",
            "STEM research"
        ],
        "update_frequency": "Weekly",
        "authentication": "Elsevier API key required"
    },
    
    DataSource.WEB_OF_SCIENCE: {
        "pros": [
            "Highest quality curation standards",
            "Trusted for research evaluation (REF, tenure)",
            "Strong citation indexing since 1900",
            "Excellent for bibliometric analysis",
            "Times Cited counts considered gold standard",
            "Subject expertise in selection"
        ],
        "cons": [
            "Most expensive ($10,000-100,000/year institutional)",
            "Narrower coverage than Scopus or Scholar",
            "English language bias",
            "Complex query language",
            "Slower to index new publications",
            "Limited API quota"
        ],
        "cost": "$10,000-100,000/year (institutional)",
        "api_complexity": "High - complex query syntax",
        "data_quality": DataQualityMetrics(
            completeness=0.95,
            accuracy=0.95,
            timeliness=0.75,
            consistency=0.95,
            coverage=0.70
        ),
        "best_for": [
            "Research assessment (tenure, grants)",
            "Citation analysis",
            "Impact factor calculations",
            "High-stakes evaluation"
        ],
        "update_frequency": "Weekly",
        "authentication": "Clarivate API key required"
    },
    
    DataSource.NIH_REPORTER: {
        "pros": [
            "Completely free and public",
            "Comprehensive US health research grants",
            "High data quality",
            "No API limits",
            "Direct from funder",
            "Includes abstracts and full metadata"
        ],
        "cons": [
            "Only NIH-funded research",
            "US-focused",
            "No citation metrics",
            "Limited to biomedical/health",
            "Grants only, not publications directly"
        ],
        "cost": "Free",
        "api_complexity": "Low - simple REST API",
        "data_quality": DataQualityMetrics(
            completeness=0.95,
            accuracy=0.98,
            timeliness=0.90,
            consistency=0.95,
            coverage=0.40
        ),
        "best_for": [
            "Health/biomedical research funding",
            "Grant tracking",
            "PI identification"
        ],
        "update_frequency": "Weekly",
        "authentication": "None required"
    },
    
    DataSource.NSF_AWARDS: {
        "pros": [
            "Completely free and public",
            "All NSF-funded research",
            "High data quality",
            "No authentication required",
            "Comprehensive STEM coverage"
        ],
        "cons": [
            "Only NSF-funded research",
            "US-focused",
            "No citation metrics",
            "Grants only, not publications",
            "25 results per page limit"
        ],
        "cost": "Free",
        "api_complexity": "Low - REST API",
        "data_quality": DataQualityMetrics(
            completeness=0.90,
            accuracy=0.98,
            timeliness=0.90,
            consistency=0.95,
            coverage=0.35
        ),
        "best_for": [
            "STEM research funding",
            "Grant tracking",
            "Interdisciplinary research"
        ],
        "update_frequency": "Daily",
        "authentication": "None required"
    },
    
    DataSource.USPTO: {
        "pros": [
            "Completely free and public",
            "All US patents",
            "High quality data",
            "Full text searchable",
            "Historical data back to 1976"
        ],
        "cons": [
            "Only US patents",
            "Complex query syntax",
            "No international patents",
            "Rate limits on queries",
            "Inventor disambiguation needed"
        ],
        "cost": "Free",
        "api_complexity": "Medium - query language required",
        "data_quality": DataQualityMetrics(
            completeness=0.98,
            accuracy=0.99,
            timeliness=0.85,
            consistency=0.98,
            coverage=0.50
        ),
        "best_for": [
            "Patent analysis",
            "Technology transfer",
            "Innovation tracking"
        ],
        "update_frequency": "Weekly",
        "authentication": "None required"
    }
}


def get_source_comparison() -> Dict:
    """Get comprehensive source comparison"""
    return DATA_SOURCE_COMPARISON


def calculate_data_quality(record: Dict, source: DataSource) -> DataQualityMetrics:
    """
    Calculate quality score for a specific data record
    
    Args:
        record: Data record to assess
        source: Data source
    
    Returns:
        Quality metrics for the record
    """
    # Expected fields by source
    expected_fields = {
        DataSource.GOOGLE_SCHOLAR: ["title", "authors", "year", "citations"],
        DataSource.SCOPUS: ["title", "authors", "year", "doi", "abstract", "keywords"],
        DataSource.WEB_OF_SCIENCE: ["title", "authors", "year", "doi", "citations"],
        DataSource.NIH_REPORTER: ["title", "pi", "funding_amount", "abstract"],
        DataSource.NSF_AWARDS: ["title", "pi", "funding_amount", "start_date"],
        DataSource.USPTO: ["patent_number", "title", "inventors", "abstract"]
    }
    
    fields = expected_fields.get(source, [])
    
    # Calculate completeness
    populated = sum(1 for field in fields if record.get(field))
    completeness = populated / len(fields) if fields else 0
    
    # Use source baseline quality + record-specific adjustments
    baseline = DATA_SOURCE_COMPARISON[source]["data_quality"]
    
    return DataQualityMetrics(
        completeness=completeness,
        accuracy=baseline.accuracy,
        timeliness=baseline.timeliness,
        consistency=baseline.consistency,
        coverage=baseline.coverage
    )


def recommend_source(use_case: str) -> List[DataSource]:
    """
    Recommend data sources for a specific use case
    
    Args:
        use_case: Description of use case
    
    Returns:
        Ranked list of recommended sources
    """
    use_case_lower = use_case.lower()
    
    recommendations = []
    
    if "citation" in use_case_lower or "impact" in use_case_lower:
        recommendations = [
            DataSource.WEB_OF_SCIENCE,
            DataSource.SCOPUS,
            DataSource.GOOGLE_SCHOLAR
        ]
    elif "grant" in use_case_lower or "funding" in use_case_lower:
        recommendations = [
            DataSource.NIH_REPORTER,
            DataSource.NSF_AWARDS
        ]
    elif "patent" in use_case_lower or "innovation" in use_case_lower:
        recommendations = [
            DataSource.USPTO
        ]
    elif "comprehensive" in use_case_lower or "exploratory" in use_case_lower:
        recommendations = [
            DataSource.GOOGLE_SCHOLAR,
            DataSource.SCOPUS
        ]
    elif "evaluation" in use_case_lower or "tenure" in use_case_lower:
        recommendations = [
            DataSource.WEB_OF_SCIENCE,
            DataSource.SCOPUS
        ]
    else:
        # Default: broad coverage
        recommendations = [
            DataSource.SCOPUS,
            DataSource.GOOGLE_SCHOLAR,
            DataSource.WEB_OF_SCIENCE
        ]
    
    return recommendations


def get_cost_benefit_analysis() -> Dict:
    """
    Get cost-benefit analysis for scaling to multiple institutions
    
    Returns:
        Analysis by institution scale
    """
    return {
        "single_institution": {
            "recommendation": "Google Scholar + Free APIs (NIH, NSF, USPTO)",
            "estimated_cost": "$0-50/month",
            "rationale": "Sufficient coverage for proof-of-concept, minimal cost"
        },
        "5_institutions": {
            "recommendation": "Scopus (institutional) + Google Scholar + Free APIs",
            "estimated_cost": "$5,000/year + $600/year SerpAPI",
            "rationale": "Better data quality needed for multi-institution comparison"
        },
        "20+_institutions": {
            "recommendation": "Scopus + Web of Science (if budget allows)",
            "estimated_cost": "$15,000-30,000/year",
            "rationale": "Rigorous evaluation requires highest quality data"
        },
        "national_scale": {
            "recommendation": "All three (Scholar, Scopus, WoS) + consolidation",
            "estimated_cost": "$50,000-100,000/year",
            "rationale": "Multiple sources for validation and comprehensive coverage"
        }
    }
