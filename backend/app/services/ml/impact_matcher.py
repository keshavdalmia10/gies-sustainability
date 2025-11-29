"""
Impact Matching Engine

Links publications to impacts (grants, patents, policies) using:
- Semantic similarity (embeddings)
- Keyword overlap
- Temporal proximity
- Author matching
"""

from typing import List, Tuple, Dict, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models import Publication, Impact, Grant, Patent, Faculty
import os


class ImpactMatcher:
    """
    Multi-modal impact matching engine
    """
    
    def __init__(self, embedding_model: str = None):
        """
        Initialize impact matcher
        
        Args:
            embedding_model: Name of sentence-transformers model
        """
        self.embedding_model_name = embedding_model or os.getenv(
            "EMBEDDING_MODEL", "all-mpnet-base-v2"
        )
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        return self.embedding_model.encode([text])[0]
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
    
    def _semantic_similarity(
        self,
        pub_text: str,
        impact_text: str
    ) -> float:
        """
        Compute semantic similarity using embeddings
        
        Args:
            pub_text: Publication text (title + abstract)
            impact_text: Impact text (title + description)
        
        Returns:
            Similarity score (0-1)
        """
        pub_embedding = self._generate_embedding(pub_text)
        impact_embedding = self._generate_embedding(impact_text)
        
        return self._cosine_similarity(pub_embedding, impact_embedding)
    
    def _keyword_overlap(
        self,
        pub_keywords: List[str],
        impact_keywords: List[str]
    ) -> float:
        """
        Compute Jaccard similarity of keywords
        
        Args:
            pub_keywords: Publication keywords
            impact_keywords: Impact keywords
        
        Returns:
            Jaccard similarity (0-1)
        """
        if not pub_keywords or not impact_keywords:
            return 0.0
        
        pub_set = set(k.lower() for k in pub_keywords)
        impact_set = set(k.lower() for k in impact_keywords)
        
        intersection = len(pub_set & impact_set)
        union = len(pub_set | impact_set)
        
        return intersection / union if union > 0 else 0.0
    
    def _temporal_proximity(
        self,
        pub_year: Optional[int],
        impact_start_date: Optional[datetime],
        impact_end_date: Optional[datetime]
    ) -> float:
        """
        Compute temporal proximity score
        
        Publications should precede or coincide with impacts.
        
        Args:
            pub_year: Publication year
            impact_start_date: Impact start date
            impact_end_date: Impact end date
        
        Returns:
            Temporal score (0-1)
        """
        if not pub_year or not impact_start_date:
            return 0.5  # Neutral score if dates missing
        
        impact_start_year = impact_start_date.year
        impact_end_year = impact_end_date.year if impact_end_date else impact_start_year + 5
        
        # Publication should be before or during impact
        if pub_year <= impact_start_year:
            # Within 3 years before: high score
            year_diff = impact_start_year - pub_year
            if year_diff <= 3:
                return 1.0 - (year_diff * 0.1)  # 1.0, 0.9, 0.8, 0.7
            else:
                return 0.5  # Neutral for older pubs
        elif pub_year <= impact_end_year:
            # During impact: very high score
            return 1.0
        else:
            # After impact: low score
            return 0.2
    
    def _author_match(
        self,
        pub_author_uuid: UUID,
        impact_author_uuids: List[UUID]
    ) -> float:
        """
        Check if publication author is linked to impact
        
        Args:
            pub_author_uuid: Publication author UUID
            impact_author_uuids: Impact author/PI/inventor UUIDs
        
        Returns:
            Match score (0 or 1)
        """
        if not impact_author_uuids:
            return 0.5  # Neutral if no authors listed
        
        return 1.0 if pub_author_uuid in impact_author_uuids else 0.0
    
    async def match_publication_to_impacts(
        self,
        session: AsyncSession,
        publication_uuid: UUID,
        candidate_impact_ids: List[UUID] = None,
        threshold: float = 0.75,
        weights: Dict[str, float] = None
    ) -> List[Tuple[UUID, float]]:
        """
        Match a publication to related impacts
        
        Args:
            session: Database session
            publication_uuid: Publication to match
            candidate_impact_ids: Optional list of impact IDs to consider
            threshold: Minimum confidence score
            weights: Optional custom weights for scoring components
        
        Returns:
            List of (impact_id, confidence_score) tuples, sorted by score
        """
        # Default weights
        if weights is None:
            weights = {
                "semantic": 0.5,
                "keyword": 0.2,
                "temporal": 0.15,
                "author": 0.15
            }
        
        # Get publication
        pub_result = await session.execute(
            select(Publication).where(Publication.article_uuid == publication_uuid)
        )
        publication = pub_result.scalar_one_or_none()
        
        if not publication:
            return []
        
        # Get candidate impacts
        if candidate_impact_ids:
            impacts_result = await session.execute(
                select(Impact).where(Impact.impact_id.in_(candidate_impact_ids))
            )
        else:
            # Get all impacts with matching SDG
            impacts_result = await session.execute(
                select(Impact).where(Impact.sdg_primary == publication.sdg_top1)
            )
        
        impacts = impacts_result.scalars().all()
        
        # Score each impact
        matches = []
        
        pub_text = f"{publication.title}. {publication.abstract or ''}"
        pub_keywords = publication.keywords or []
        
        for impact in impacts:
            # Get impact-specific data (grant, patent, etc.)
            impact_keywords = []
            impact_authors = []
            
            if impact.impact_type == 'grant':
                grant_result = await session.execute(
                    select(Grant).where(Grant.grant_id == impact.impact_id)
                )
                grant = grant_result.scalar_one_or_none()
                if grant:
                    impact_keywords = grant.keywords or []
                    impact_authors = [grant.pi_uuid] if grant.pi_uuid else []
                    if grant.co_investigators:
                        impact_authors.extend(grant.co_investigators)
            
            elif impact.impact_type == 'patent':
                patent_result = await session.execute(
                    select(Patent).where(Patent.patent_id == impact.impact_id)
                )
                patent = patent_result.scalar_one_or_none()
                if patent and patent.inventors:
                    impact_authors = patent.inventors
            
            # Compute individual scores
            impact_text = f"{impact.title}. {impact.description or ''}"
            
            semantic_score = self._semantic_similarity(pub_text, impact_text)
            keyword_score = self._keyword_overlap(pub_keywords, impact_keywords)
            temporal_score = self._temporal_proximity(
                publication.publication_year,
                impact.start_date,
                impact.end_date
            )
            author_score = self._author_match(
                publication.person_uuid,
                impact_authors
            )
            
            # Weighted combination
            final_score = (
                weights["semantic"] * semantic_score +
                weights["keyword"] * keyword_score +
                weights["temporal"] * temporal_score +
                weights["author"] * author_score
            )
            
            if final_score >= threshold:
                matches.append((impact.impact_id, final_score))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    async def compute_precision_at_k(
        self,
        session: AsyncSession,
        predictions: List[Tuple[UUID, float]],
        ground_truth: List[UUID],
        k: int = 5
    ) -> float:
        """
        Compute Precision@k metric
        
        Args:
            session: Database session
            predictions: List of (impact_id, score) predictions
            ground_truth: List of true impact IDs
            k: Number of top predictions to evaluate
        
        Returns:
            Precision@k score (0-1)
        """
        top_k_ids = [pred[0] for pred in predictions[:k]]
        relevant_in_top_k = set(top_k_ids) & set(ground_truth)
        
        return len(relevant_in_top_k) / k if k > 0 else 0.0


# Singleton instance
_matcher_instance: Optional[ImpactMatcher] = None


def get_impact_matcher() -> ImpactMatcher:
    """Get or create singleton impact matcher instance"""
    global _matcher_instance
    if _matcher_instance is None:
        _matcher_instance = ImpactMatcher()
    return _matcher_instance
