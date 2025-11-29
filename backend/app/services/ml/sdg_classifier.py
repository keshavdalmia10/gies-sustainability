"""
SDG Classification Service

Two-stage AI-powered SDG classification:
1. Binary sustainability relevance detection
2. Top-K SDG goal identification using vector similarity
"""

from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()


class SDGClassifier:
    """
    AI-powered SDG classification service
    """
    
    # SDG Descriptions for vector matching
    SDG_DESCRIPTIONS = {
        1: "No Poverty: End poverty in all its forms everywhere, including economic inclusion, poverty eradication, and access to basic services.",
        2: "Zero Hunger: End hunger, achieve food security, improved nutrition, and sustainable agriculture practices.",
        3: "Good Health and Well-being: Ensure healthy lives and promote well-being for all ages, including healthcare access and disease prevention.",
        4: "Quality Education: Ensure inclusive, equitable quality education and promote lifelong learning opportunities.",
        5: "Gender Equality: Achieve gender equality and empower all women and girls through equal rights and opportunities.",
        6: "Clean Water and Sanitation: Ensure availability and sustainable management of water and sanitation for all.",
        7: "Affordable and Clean Energy: Ensure access to affordable, reliable, sustainable, and modern energy for all.",
        8: "Decent Work and Economic Growth: Promote sustained, inclusive, sustainable economic growth, full employment, and decent work.",
        9: "Industry, Innovation and Infrastructure: Build resilient infrastructure, promote sustainable industrialization and foster innovation.",
        10: "Reduced Inequality: Reduce inequality within and among countries through inclusive policies.",
        11: "Sustainable Cities and Communities: Make cities inclusive, safe, resilient, and sustainable.",
        12: "Responsible Consumption and Production: Ensure sustainable consumption and production patterns.",
        13: "Climate Action: Take urgent action to combat climate change and its impacts.",
        14: "Life Below Water: Conserve and sustainably use oceans, seas, and marine resources.",
        15: "Life on Land: Protect, restore, and promote sustainable use of terrestrial ecosystems.",
        16: "Peace, Justice and Strong Institutions: Promote peaceful, inclusive societies and strong institutions.",
        17: "Partnerships for the Goals: Strengthen global partnerships for sustainable development."
    }
    
    def __init__(
        self,
        embedding_model: str = None,
        openai_api_key: str = None
    ):
        """
        Initialize SDG classifier
        
        Args:
            embedding_model: Name of sentence-transformers model
            openai_api_key: OpenAI API key for binary classification
        """
        self.embedding_model_name = embedding_model or os.getenv(
            "EMBEDDING_MODEL", "all-mpnet-base-v2"
        )
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        
        # OpenAI client for binary classification
        self.openai_client = AsyncOpenAI(
            api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )
        
        # Pre-compute SDG embeddings
        self.sdg_embeddings = self._compute_sdg_embeddings()
    
    def _compute_sdg_embeddings(self) -> np.ndarray:
        """Pre-compute embeddings for all SDG descriptions"""
        descriptions = [self.SDG_DESCRIPTIONS[i] for i in range(1, 18)]
        embeddings = self.embedding_model.encode(
            descriptions,
            convert_to_tensor=False,
            show_progress_bar=False
        )
        return np.array(embeddings)
    
    async def classify_sustainability_relevance(
        self,
        text: str,
        title: str = None
    ) -> Tuple[bool, float]:
        """
        Stage 1: Binary classification - Is this research sustainability-related?
        
        Args:
            text: Research abstract or description
            title: Research title (optional)
        
        Returns:
            (is_sustainable, confidence_score)
        """
        # Construct prompt
        full_text = f"Title: {title}\n\n{text}" if title else text
        
        prompt = f"""Analyze the following research and determine if it is relevant to the United Nations' 17 Sustainable Development Goals (SDGs).

Research:
{full_text[:2000]}  # Limit text length

The SDGs cover: poverty, hunger, health, education, gender equality, water, energy, economic growth, infrastructure, inequality, cities, consumption, climate, oceans, land, peace, and partnerships.

Is this research relevant to ANY of the SDGs? Answer with just "YES" or "NO", followed by a confidence score from 0.0 to 1.0.

Format: YES|0.95 or NO|0.80"""

        try:
            response = await self.openai_client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in sustainability and the UN Sustainable Development Goals."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse response
            parts = result.split('|')
            is_sustainable = parts[0].upper() == 'YES'
            confidence = float(parts[1]) if len(parts) > 1 else 0.5
            
            return is_sustainable, confidence
            
        except Exception as e:
            print(f"Error in sustainability classification: {e}")
            # Fallback to embedding-based if OpenAI fails
            return await self._fallback_sustainability_check(text)
    
    async def _fallback_sustainability_check(self, text: str) -> Tuple[bool, float]:
        """Fallback method using embedding similarity"""
        text_embedding = self.embedding_model.encode([text])[0]
        
        # Check similarity with all SDG embeddings
        similarities = np.dot(self.sdg_embeddings, text_embedding)
        max_similarity = float(np.max(similarities))
        
        # Threshold for sustainability relevance
        threshold = 0.3
        is_sustainable = max_similarity > threshold
        
        return is_sustainable, max_similarity
    
    def identify_sdg_goals(
        self,
        text: str,
        title: str = None,
        top_k: int = 3
    ) -> List[Tuple[int, float]]:
        """
        Stage 2: Identify top-K SDG goals using vector similarity
        
        Args:
            text: Research abstract or description
            title: Research title (optional)
            top_k: Number of top SDGs to return
        
        Returns:
            List of (sdg_number, similarity_score) tuples
        """
        # Combine title and text for better context
        full_text = f"{title}. {text}" if title else text
        
        # Generate embedding for the research
        text_embedding = self.embedding_model.encode([full_text])[0]
        
        # Compute cosine similarities with all SDG embeddings
        similarities = np.dot(self.sdg_embeddings, text_embedding)
        
        # Get top-K indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Return SDG numbers (1-indexed) and scores
        results = [
            (int(idx + 1), float(similarities[idx]))
            for idx in top_indices
        ]
        
        return results
    
    async def classify_full(
        self,
        text: str,
        title: str = None,
        top_k: int = 3
    ) -> dict:
        """
        Full classification pipeline: Stage 1 + Stage 2
        
        Args:
            text: Research abstract or description
            title: Research title (optional)
            top_k: Number of top SDGs to return
        
        Returns:
            Dictionary with classification results
        """
        # Stage 1: Check sustainability relevance
        is_sustainable, confidence = await self.classify_sustainability_relevance(
            text, title
        )
        
        if not is_sustainable:
            return {
                "is_sustainable": False,
                "confidence": confidence,
                "sdg_classifications": []
            }
        
        # Stage 2: Identify specific SDGs
        sdg_results = self.identify_sdg_goals(text, title, top_k)
        
        return {
            "is_sustainable": True,
            "confidence": confidence,
            "sdg_classifications": [
                {
                    "sdg_number": sdg,
                    "sdg_title": self.SDG_DESCRIPTIONS[sdg].split(':')[0],
                    "similarity_score": score
                }
                for sdg, score in sdg_results
            ],
            "sdg_top1": sdg_results[0][0] if sdg_results else None,
            "sdg_top2": sdg_results[1][0] if len(sdg_results) > 1 else None,
            "sdg_top3": sdg_results[2][0] if len(sdg_results) > 2 else None
        }


# Singleton instance
_classifier_instance: Optional[SDGClassifier] = None


def get_sdg_classifier() -> SDGClassifier:
    """Get or create singleton SDG classifier instance"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = SDGClassifier()
    return _classifier_instance
