#!/usr/bin/env python3
"""
Demo script to test the complete MVP pipeline

1. Load data from CSV
2. Classify publications for SDGs
3. Fetch external grants
4. Match publications to impacts
5. Generate impact cards
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import async_engine, AsyncSessionLocal
from app.services.ml import get_sdg_classifier, get_impact_matcher
from app.services.external import get_nih_client, get_nsf_client
from app.services.impact_card_generator import get_impact_card_generator
from app.models import Faculty, Publication, Grant, Impact
from sqlalchemy import select, func
import os


async def demo_pipeline():
    """Run complete demo pipeline"""
    
    print("=" * 60)
    print("🚀 GIES SUSTAINABILITY IMPACT DASHBOARD - DEMO PIPELINE")
    print("=" * 60)
    print()
    
    async with AsyncSessionLocal() as session:
        
        # Step 1: Check loaded data
        print("📊 Step 1: Checking loaded data...")
        print("-" * 60)
        
        faculty_count = await session.execute(select(func.count(Faculty.person_uuid)))
        pub_count = await session.execute(select(func.count(Publication.article_uuid)))
        
        print(f"✅ Faculty in database: {faculty_count.scalar()}")
        print(f"✅ Publications in database: {pub_count.scalar()}")
        print()
        
        # Step 2: Classify a sample publication
        print("🤖 Step 2: SDG Classification Demo...")
        print("-" * 60)
        
        # Get a sample publication
        result = await session.execute(
            select(Publication).where(Publication.is_sustain == False).limit(1)
        )
        sample_pub = result.scalar_one_or_none()
        
        if sample_pub:
            classifier = get_sdg_classifier()
            
            text = sample_pub.abstract or sample_pub.title
            classification = await classifier.classify_full(
                text=text,
                title=sample_pub.title,
                top_k=3
            )
            
            print(f"Publication: {sample_pub.title[:60]}...")
            print(f"Is Sustainable: {classification['is_sustainable']}")
            print(f"Confidence: {classification['confidence']:.2f}")
            
            if classification['sdg_classifications']:
                print("Top SDGs:")
                for sdg_class in classification['sdg_classifications']:
                    print(f"  - SDG {sdg_class['sdg_number']}: {sdg_class['sdg_title']} "
                          f"(score: {sdg_class['similarity_score']:.2f})")
        else:
            print("No unclassified publications found. Load data first!")
        
        print()
        
        # Step 3: Fetch external grants (demo)
        print("🌐 Step 3: External API Demo (NIH)...")
        print("-" * 60)
        
        if os.getenv("OPENAI_API_KEY"):
            try:
                nih = get_nih_client()
                
                print("Searching NIH grants for 'solar energy'...")
                grants = await nih.search_by_keywords(
                    keywords=["solar energy"],
                    fiscal_years=[2023],
                    organization="University of Illinois"
                )
                
                print(f"Found {len(grants)} grants")
                
                if grants:
                    sample_grant = grants[0]
                    parsed = nih.parse_grant_record(sample_grant)
                    print(f"\nSample Grant:")
                    print(f"  Title: {parsed['title'][:60]}...")
                    print(f"  Funder: {parsed['funder']}")
                    print(f"  Amount: ${parsed['funding_amount']:,.0f}" if parsed['funding_amount'] else "N/A")
                
                await nih.close()
            
            except Exception as e:
                print(f"⚠️ External API error (this is okay for demo): {e}")
        else:
            print("⚠️ Skipping external API demo (no OPENAI_API_KEY)")
        
        print()
        
        # Step 4: Impact matching demo
        print("🔗 Step 4: Impact Matching Demo...")
        print("-" * 60)
        
        # Check if we have any impacts
        impact_count = await session.execute(select(func.count(Impact.impact_id)))
        
        if impact_count.scalar() > 0:
            # Get publication and impact
            pub_result = await session.execute(
                select(Publication).where(Publication.sdg_top1.isnot(None)).limit(1)
            )
            pub = pub_result.scalar_one_or_none()
            
            if pub:
                matcher = get_impact_matcher()
                
                print(f"Matching publication: {pub.title[:50]}...")
                
                matches = await matcher.match_publication_to_impacts(
                    session=session,
                    publication_uuid=pub.article_uuid,
                    threshold=0.5  # Lower threshold for demo
                )
                
                print(f"Found {len(matches)} potential matches")
                
                if matches:
                    for i, (impact_id, score) in enumerate(matches[:3], 1):
                        print(f"  {i}. Impact {str(impact_id)[:8]}... (confidence: {score:.2f})")
        else:
            print("No impacts in database yet. Add grants/patents first!")
        
        print()
        
        # Step 5: Generate impact card demo
        print("📄 Step 5: Impact Card Generation Demo...")
        print("-" * 60)
        
        # Get faculty with SDG7 publications
        result = await session.execute(
            select(Faculty.person_uuid, Faculty.name, func.count(Publication.article_uuid))
            .join(Publication, Publication.person_uuid == Faculty.person_uuid)
            .where(Publication.sdg_top1 == 7)
            .group_by(Faculty.person_uuid, Faculty.name)
            .order_by(func.count(Publication.article_uuid).desc())
            .limit(1)
        )
        
        row = result.first()
        
        if row and os.getenv("OPENAI_API_KEY"):
            faculty_uuid, faculty_name, pub_count = row
            
            print(f"Generating impact card for: {faculty_name}")
            print(f"SDG 7 (Affordable and Clean Energy)")
            print(f"Publications: {pub_count}")
            print()
            
            generator = get_impact_card_generator()
            
            try:
                # Preview first
                data = await generator.aggregate_faculty_sdg_data(
                    session=session,
                    faculty_uuid=faculty_uuid,
                    sdg=7
                )
                
                print(f"Data Available:")
                print(f"  - Publications: {len(data['publications'])}")
                print(f"  - Grants: {len(data['grants'])}")
                print(f"  - Patents: {len(data['patents'])}")
                print()
                
                # Generate card (without saving to avoid duplicates in demo)
                print("Generating narrative with GPT-4...")
                card = await generator.generate_impact_card(
                    session=session,
                    faculty_uuid=faculty_uuid,
                    sdg=7,
                    auto_save=False  # Don't save in demo
                )
                
                print()
                print("=" * 60)
                print("GENERATED IMPACT CARD")
                print("=" * 60)
                print(f"\nTitle: {card['title']}")
                print(f"\nNarrative:")
                print(card['narrative'])
                print(f"\nKey Outcomes:")
                for outcome in card['key_outcomes']:
                    print(f"  • {outcome}")
                print(f"\nTotal Funding: ${card['total_funding']:,.2f}")
                print(f"Funding Gap: ${card['funding_gap']:,.2f}")
                
            except Exception as e:
                print(f"⚠️ Error generating card: {e}")
        
        elif not os.getenv("OPENAI_API_KEY"):
            print("⚠️ Skipping card generation (no OPENAI_API_KEY)")
        else:
            print("No faculty with SDG7 publications found. Load data first!")
        
        print()
    
    print("=" * 60)
    print("✅ DEMO COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review the generated impact card above")
    print("2. Try the API endpoints at http://localhost:8000/docs")
    print("3. Generate more cards for other faculty/SDGs")
    print("4. Build the frontend dashboard!")


async def cleanup():
    """Clean up resources"""
    await async_engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(demo_pipeline())
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    finally:
        asyncio.run(cleanup())
