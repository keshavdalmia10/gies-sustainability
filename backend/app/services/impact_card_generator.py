"""
Impact Card Generator Service

Generates compelling impact card narratives using LLM (OpenAI GPT-4)
Aggregates faculty publications and impacts into donor-ready format
"""

from typing import List, Dict, Optional
from uuid import UUID
from decimal import Decimal
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
from datetime import datetime

from app.models import (
    Faculty, Publication, Impact, Grant, Patent, Policy,
    ImpactCard as ImpactCardModel, SDGGoal,
    PublicationImpactLink
)


class ImpactCardGenerator:
    """
    Generate rich impact cards with LLM-powered narratives
    """
    
    def __init__(self, openai_api_key: str = None):
        """
        Initialize impact card generator
        
        Args:
            openai_api_key: OpenAI API key (optional, uses env if not provided)
        """
        self.openai_client = AsyncOpenAI(
            api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    async def aggregate_faculty_sdg_data(
        self,
        session: AsyncSession,
        faculty_uuid: UUID,
        sdg: int
    ) -> Dict:
        """
        Aggregate all data for a faculty member and SDG
        
        Args:
            session: Database session
            faculty_uuid: Faculty UUID
            sdg: SDG number (1-17)
        
        Returns:
            Dictionary with aggregated data
        """
        # Get faculty
        faculty_result = await session.execute(
            select(Faculty).where(Faculty.person_uuid == faculty_uuid)
        )
        faculty = faculty_result.scalar_one_or_none()
        
        if not faculty:
            raise ValueError(f"Faculty not found: {faculty_uuid}")
        
        # Get SDG info
        sdg_result = await session.execute(
            select(SDGGoal).where(SDGGoal.sdg_number == sdg)
        )
        sdg_goal = sdg_result.scalar_one_or_none()
        
        # Get publications for this SDG
        pub_result = await session.execute(
            select(Publication).where(
                Publication.person_uuid == faculty_uuid,
                Publication.sdg_top1 == sdg
            ).order_by(Publication.publication_year.desc())
        )
        publications = pub_result.scalars().all()
        
        # Get linked impacts
        impact_ids = set()
        for pub in publications:
            link_result = await session.execute(
                select(PublicationImpactLink).where(
                    PublicationImpactLink.publication_uuid == pub.article_uuid,
                    PublicationImpactLink.confidence_score >= 0.75
                )
            )
            links = link_result.scalars().all()
            impact_ids.update(link.impact_id for link in links)
        
        # Get impact details
        impacts = []
        grants = []
        patents = []
        policies = []
        
        if impact_ids:
            impact_result = await session.execute(
                select(Impact).where(Impact.impact_id.in_(impact_ids))
            )
            impacts = impact_result.scalars().all()
            
            # Categorize by type
            for impact in impacts:
                if impact.impact_type == 'grant':
                    grant_result = await session.execute(
                        select(Grant).where(Grant.grant_id == impact.impact_id)
                    )
                    grant = grant_result.scalar_one_or_none()
                    if grant:
                        grants.append((impact, grant))
                
                elif impact.impact_type == 'patent':
                    patent_result = await session.execute(
                        select(Patent).where(Patent.patent_id == impact.impact_id)
                    )
                    patent = patent_result.scalar_one_or_none()
                    if patent:
                        patents.append((impact, patent))
                
                elif impact.impact_type == 'policy':
                    policy_result = await session.execute(
                        select(Policy).where(Policy.policy_id == impact.impact_id)
                    )
                    policy = policy_result.scalar_one_or_none()
                    if policy:
                        policies.append((impact, policy))
        
        return {
            "faculty": faculty,
            "sdg": sdg_goal,
            "publications": publications,
            "impacts": impacts,
            "grants": grants,
            "patents": patents,
            "policies": policies
        }
    
    async def generate_narrative(
        self,
        faculty_name: str,
        department: str,
        sdg: int,
        sdg_title: str,
        publications: List[Dict],
        grants: List[Dict],
        patents: List[Dict],
        outcomes: List[str] = None
    ) -> str:
        """
        Generate compelling narrative using GPT-4
        
        Args:
            faculty_name: Professor's name
            department: Department
            sdg: SDG number
            sdg_title: SDG title
            publications: List of publication summaries
            grants: List of grant summaries
            patents: List of patent summaries
            outcomes: Optional list of key outcomes
        
        Returns:
            Generated narrative text (2-3 paragraphs)
        """
        # Construct prompt
        prompt = f"""Create a compelling 2-3 paragraph narrative for an impact card showcasing a faculty member's sustainability research and real-world impact.

Faculty: Professor {faculty_name}
Department: {department}
Focus Area: UN SDG {sdg} - {sdg_title}

Research Publications ({len(publications)}):
{self._format_publications(publications)}

Funded Projects ({len(grants)}):
{self._format_grants(grants)}

Patents & Innovations ({len(patents)}):
{self._format_patents(patents)}

{f'Key Outcomes: {", ".join(outcomes)}' if outcomes else ''}

Write a narrative that:
1. Opens with the problem/challenge being addressed
2. Describes the innovative research approach and methodology
3. Highlights tangible real-world impacts and outcomes
4. Emphasizes community benefits and scalability
5. Uses compelling, donor-friendly language (avoid jargon)
6. Ends with future potential and funding opportunities

Tone: Professional, inspiring, impact-focused. Target audience: Donors and decision-makers.
Length: 250-350 words (2-3 paragraphs)."""

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert grant writer and impact storyteller for university sustainability initiatives. You excel at translating complex research into compelling narratives that inspire donors and decision-makers."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            narrative = response.choices[0].message.content.strip()
            return narrative
            
        except Exception as e:
            print(f"Error generating narrative: {e}")
            # Return fallback narrative
            return self._generate_fallback_narrative(
                faculty_name, sdg_title, len(publications), len(grants)
            )
    
    def _format_publications(self, publications: List[Dict]) -> str:
        """Format publications for prompt"""
        if not publications:
            return "None listed"
        
        lines = []
        for i, pub in enumerate(publications[:5], 1):  # Top 5
            lines.append(f"  {i}. \"{pub['title']}\" ({pub['year']})")
        
        if len(publications) > 5:
            lines.append(f"  ... and {len(publications) - 5} more")
        
        return "\n".join(lines)
    
    def _format_grants(self, grants: List[Dict]) -> str:
        """Format grants for prompt"""
        if not grants:
            return "None listed"
        
        lines = []
        for i, grant in enumerate(grants[:3], 1):  # Top 3
            amount = f"${grant['amount']:,.0f}" if grant.get('amount') else "N/A"
            lines.append(f"  {i}. {grant['title']} ({grant['funder']}, {amount})")
        
        return "\n".join(lines)
    
    def _format_patents(self, patents: List[Dict]) -> str:
        """Format patents for prompt"""
        if not patents:
            return "None listed"
        
        lines = []
        for i, patent in enumerate(patents[:3], 1):
            lines.append(f"  {i}. {patent['title']} (Patent #{patent['number']})")
        
        return "\n".join(lines)
    
    def _generate_fallback_narrative(
        self,
        faculty_name: str,
        sdg_title: str,
        pub_count: int,
        grant_count: int
    ) -> str:
        """Generate simple fallback narrative if LLM fails"""
        return f"""Professor {faculty_name}'s research addresses critical challenges in {sdg_title}. Through {pub_count} peer-reviewed publications and {grant_count} funded projects, this work demonstrates significant contributions to sustainable development.

The research combines innovative methodologies with practical applications to create measurable impact in communities. By bridging academic excellence with real-world implementation, this portfolio showcases the transformative potential of university research in addressing global sustainability challenges.

Continued investment in this research area offers opportunities to scale these solutions and amplify their impact across broader communities and geographies."""
    
    async def calculate_funding_metrics(
        self,
        grants: List[tuple]
    ) -> Dict[str, Decimal]:
        """
        Calculate funding metrics
        
        Args:
            grants: List of (Impact, Grant) tuples
        
        Returns:
            Dictionary with total_funding and funding_gap estimates
        """
        total_funding = Decimal(0)
        
        for impact, grant in grants:
            if impact.funding_amount:
                total_funding += impact.funding_amount
        
        # Estimate funding gap (30% of total for continued work)
        funding_gap = total_funding * Decimal("0.3")
        
        return {
            "total_funding": total_funding,
            "funding_gap": funding_gap if total_funding > 0 else Decimal(100000)
        }
    
    def extract_key_outcomes(
        self,
        impacts: List[Impact],
        grants: List[tuple],
        patents: List[tuple]
    ) -> List[str]:
        """
        Extract key outcomes from impacts
        
        Args:
            impacts: List of Impact objects
            grants: List of (Impact, Grant) tuples
            patents: List of (Impact, Patent) tuples
        
        Returns:
            List of outcome strings
        """
        outcomes = []
        
        # From impact outcomes
        for impact in impacts:
            if impact.outcomes:
                # Extract specific outcome metrics
                if isinstance(impact.outcomes, dict):
                    if 'jobs_created' in impact.outcomes:
                        outcomes.append(f"{impact.outcomes['jobs_created']} jobs created")
                    if 'communities_served' in impact.outcomes:
                        outcomes.append(f"{impact.outcomes['communities_served']} communities served")
                    if 'energy_generated' in impact.outcomes:
                        outcomes.append(f"{impact.outcomes['energy_generated']} of clean energy")
        
        # From beneficiaries
        total_beneficiaries = sum(
            impact.beneficiaries_count or 0 for impact in impacts
        )
        if total_beneficiaries > 0:
            outcomes.append(f"{total_beneficiaries:,} people reached")
        
        # Patent count
        if len(patents) > 0:
            outcomes.append(f"{len(patents)} patents filed")
        
        # Grant funding
        total_funding = sum(
            impact.funding_amount or 0 for impact, _ in grants
        )
        if total_funding > 0:
            outcomes.append(f"${total_funding:,.0f} in research funding")
        
        return outcomes[:5]  # Top 5 outcomes
    
    async def generate_impact_card(
        self,
        session: AsyncSession,
        faculty_uuid: UUID,
        sdg: int,
        auto_save: bool = True
    ) -> Dict:
        """
        Generate complete impact card with narrative
        
        Args:
            session: Database session
            faculty_uuid: Faculty UUID
            sdg: SDG number
            auto_save: Whether to save to database
        
        Returns:
            Complete impact card data
        """
        # Aggregate data
        data = await self.aggregate_faculty_sdg_data(session, faculty_uuid, sdg)
        
        faculty = data["faculty"]
        sdg_goal = data["sdg"]
        publications = data["publications"]
        grants = data["grants"]
        patents = data["patents"]
        
        # Prepare data for narrative
        pub_summaries = [
            {
                "title": pub.title,
                "year": pub.publication_year,
                "journal": pub.journal_title
            }
            for pub in publications
        ]
        
        grant_summaries = [
            {
                "title": impact.title,
                "funder": grant.funder,
                "amount": float(impact.funding_amount) if impact.funding_amount else None
            }
            for impact, grant in grants
        ]
        
        patent_summaries = [
            {
                "title": impact.title,
                "number": patent.patent_number
            }
            for impact, patent in patents
        ]
        
        # Extract outcomes
        key_outcomes = self.extract_key_outcomes(
            data["impacts"],
            grants,
            patents
        )
        
        # Generate narrative
        narrative = await self.generate_narrative(
            faculty_name=faculty.name,
            department=faculty.department or "Unknown",
            sdg=sdg,
            sdg_title=sdg_goal.title if sdg_goal else f"SDG {sdg}",
            publications=pub_summaries,
            grants=grant_summaries,
            patents=patent_summaries,
            outcomes=key_outcomes
        )
        
        # Calculate funding metrics
        funding_metrics = await self.calculate_funding_metrics(grants)
        
        # Determine date range
        years = [pub.publication_year for pub in publications if pub.publication_year]
        start_year = min(years) if years else None
        end_year = max(years) if years else None
        
        # Create title
        title = f"{faculty.name}: {sdg_goal.title if sdg_goal else f'SDG {sdg}'} Impact"
        
        # Create summary (first 200 chars of narrative)
        summary = narrative[:200] + "..." if len(narrative) > 200 else narrative
        
        # Build impact card
        impact_card_data = {
            "person_uuid": faculty_uuid,
            "sdg": sdg,
            "title": title,
            "summary": summary,
            "narrative": narrative,
            "publications": [pub.article_uuid for pub in publications],
            "impacts": [impact.impact_id for impact in data["impacts"]],
            "key_outcomes": key_outcomes,
            "geography": "Illinois",  # Default, can be customized
            "total_funding": funding_metrics["total_funding"],
            "communities_reached": sum(
                impact.beneficiaries_count or 0 for impact in data["impacts"]
            ),
            "start_year": start_year,
            "end_year": end_year,
            "funding_gap": funding_metrics["funding_gap"],
            "next_milestones": [
                "Scale pilot programs to additional communities",
                "Secure continued funding for impact expansion",
                "Develop partnerships for broader implementation"
            ],
            "status": "draft"
        }
        
        if auto_save:
            # Check if card already exists
            existing_result = await session.execute(
                select(ImpactCardModel).where(
                    ImpactCardModel.person_uuid == faculty_uuid,
                    ImpactCardModel.sdg == sdg
                )
            )
            existing_card = existing_result.scalar_one_or_none()
            
            if existing_card:
                # Update existing
                for key, value in impact_card_data.items():
                    if key not in ['person_uuid', 'sdg']:
                        setattr(existing_card, key, value)
                card = existing_card
            else:
                # Create new
                card = ImpactCardModel(**impact_card_data)
                session.add(card)
            
            await session.commit()
            await session.refresh(card)
            
            impact_card_data["card_id"] = card.card_id
        
        return impact_card_data


# Singleton instance
_generator_instance: Optional[ImpactCardGenerator] = None


def get_impact_card_generator() -> ImpactCardGenerator:
    """Get or create singleton impact card generator"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = ImpactCardGenerator()
    return _generator_instance
