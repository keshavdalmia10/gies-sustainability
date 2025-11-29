#!/usr/bin/env python3
"""
Test Impact Card Generator

Simple script to test impact card generation for a specific faculty and SDG
"""

import asyncio
import sys
from pathlib import Path
from uuid import UUID

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.services.impact_card_generator import get_impact_card_generator
from sqlalchemy import select
from app.models import Faculty, Publication
import os


async def test_card_generation(faculty_uuid: str = None, sdg: int = 7):
    """
    Test impact card generation
    
    Args:
        faculty_uuid: Faculty UUID (optional, will find one if not provided)
        sdg: SDG number (default 7)
    """
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set in environment")
        print("Please add it to your .env file")
        return
    
    async with AsyncSessionLocal() as session:
        
        # Get faculty UUID if not provided
        if not faculty_uuid:
            print(f"Finding faculty with SDG {sdg} publications...")
            
            result = await session.execute(
                select(Faculty.person_uuid, Faculty.name)
                .join(Publication, Publication.person_uuid == Faculty.person_uuid)
                .where(Publication.sdg_top1 == sdg)
                .limit(1)
            )
            
            row = result.first()
            
            if not row:
                print(f"❌ No faculty found with SDG {sdg} publications")
                print("Load data first: python scripts/load_data.py ../data.csv")
                return
            
            faculty_uuid, faculty_name = row
            print(f"✅ Found faculty: {faculty_name}")
        else:
            faculty_uuid = UUID(faculty_uuid)
        
        print(f"\n{'=' * 70}")
        print(f"GENERATING IMPACT CARD")
        print(f"{'=' * 70}")
        print(f"Faculty UUID: {faculty_uuid}")
        print(f"SDG: {sdg}")
        print()
        
        # Preview data
        print("📊 Previewing available data...")
        
        generator = get_impact_card_generator()
        
        try:
            data = await generator.aggregate_faculty_sdg_data(
                session=session,
                faculty_uuid=faculty_uuid,
                sdg=sdg
            )
            
            faculty = data["faculty"]
            
            print(f"\nFaculty: {faculty.name}")
            print(f"Department: {faculty.department}")
            print(f"Publications: {len(data['publications'])}")
            print(f"Grants: {len(data['grants'])}")
            print(f"Patents: {len(data['patents'])}")
            print(f"Policies: {len(data['policies'])}")
            print()
            
            if len(data['publications']) == 0 and len(data['grants']) == 0:
                print("⚠️ Warning: No publications or grants found.")
                print("Impact card will be generic. Add more data for better cards.")
                print()
            
            # Generate card
            print("🤖 Generating narrative with GPT-4...")
            print("(This may take 10-30 seconds)")
            print()
            
            card = await generator.generate_impact_card(
                session=session,
                faculty_uuid=faculty_uuid,
                sdg=sdg,
                auto_save=True  # Save to database
            )
            
            # Display results
            print(f"{'=' * 70}")
            print("✅ IMPACT CARD GENERATED")
            print(f"{'=' * 70}")
            print()
            print(f"Card ID: {card.get('card_id')}")
            print(f"Title: {card['title']}")
            print()
            print("NARRATIVE:")
            print("-" * 70)
            print(card['narrative'])
            print()
            print("KEY OUTCOMES:")
            print("-" * 70)
            for outcome in card['key_outcomes']:
                print(f"  • {outcome}")
            print()
            print("METRICS:")
            print("-" * 70)
            print(f"  Total Funding: ${card['total_funding']:,.2f}")
            print(f"  Funding Gap: ${card['funding_gap']:,.2f}")
            print(f"  Communities Reached: {card.get('communities_reached', 0):,}")
            print(f"  Time Period: {card.get('start_year', 'N/A')} - {card.get('end_year', 'Present')}")
            print()
            print(f"Status: {card['status']}")
            print()
            print("=" * 70)
            print()
            print("✅ Card saved to database!")
            print(f"View at: http://localhost:8000/api/v1/impact-cards/{card.get('card_id')}")
            
        except ValueError as e:
            print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ Error generating card: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test impact card generation")
    parser.add_argument("--faculty-uuid", help="Faculty UUID (optional)")
    parser.add_argument("--sdg", type=int, default=7, help="SDG number (default: 7)")
    
    args = parser.parse_args()
    
    asyncio.run(test_card_generation(
        faculty_uuid=args.faculty_uuid,
        sdg=args.sdg
    ))
