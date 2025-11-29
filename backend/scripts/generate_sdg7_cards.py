#!/usr/bin/env python3
"""
Batch generate impact cards for all faculty with SDG 7 publications

This script generates impact cards for the MVP deliverable:
"10 validated impact cards for SDG 7"
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.services.impact_card_generator import get_impact_card_generator
from sqlalchemy import select, func
from app.models import Faculty, Publication
import os


async def batch_generate_sdg7_cards(limit: int = 10):
    """
    Generate impact cards for top faculty in SDG 7
    
    Args:
        limit: Number of cards to generate (default 10 for MVP)
    """
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set")
        return
    
    async with AsyncSessionLocal() as session:
        
        print("=" * 70)
        print("BATCH IMPACT CARD GENERATION - SDG 7")
        print("=" * 70)
        print()
        
        # Get top faculty with SDG 7 publications
        print(f"Finding top {limit} faculty with SDG 7 publications...")
        
        result = await session.execute(
            select(
                Faculty.person_uuid,
                Faculty.name,
                Faculty.department,
                func.count(Publication.article_uuid).label('pub_count')
            )
            .join(Publication, Publication.person_uuid == Faculty.person_uuid)
            .where(Publication.sdg_top1 == 7)
            .group_by(Faculty.person_uuid, Faculty.name, Faculty.department)
            .order_by(func.count(Publication.article_uuid).desc())
            .limit(limit)
        )
        
        faculty_list = result.all()
        
        print(f"✅ Found {len(faculty_list)} faculty")
        print()
        
        if not faculty_list:
            print("❌ No faculty with SDG 7 publications found")
            print("Load data first: python scripts/load_data.py ../data.csv")
            return
        
        # Display list
        print("Faculty to process:")
        print("-" * 70)
        for i, (uuid, name, dept, count) in enumerate(faculty_list, 1):
            print(f"{i:2}. {name:30} ({dept or 'N/A':20}) - {count:2} pubs")
        print()
        
        # Confirm
        response = input(f"Generate {len(faculty_list)} impact cards? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
        
        print()
        print("=" * 70)
        print("GENERATING CARDS...")
        print("=" * 70)
        print()
        
        generator = get_impact_card_generator()
        
        successful = []
        failed = []
        
        for i, (faculty_uuid, faculty_name, dept, pub_count) in enumerate(faculty_list, 1):
            print(f"\n[{i}/{len(faculty_list)}] {faculty_name}")
            print("-" * 70)
            
            try:
                card = await generator.generate_impact_card(
                    session=session,
                    faculty_uuid=faculty_uuid,
                    sdg=7,
                    auto_save=True
                )
                
                print(f"✅ Generated: {card['title'][:60]}...")
                print(f"   Outcomes: {len(card['key_outcomes'])}")
                print(f"   Funding: ${card['total_funding']:,.0f}")
                print(f"   Card ID: {card.get('card_id')}")
                
                successful.append({
                    'faculty_name': faculty_name,
                    'card_id': card.get('card_id'),
                    'funding': card['total_funding']
                })
                
            except Exception as e:
                print(f"❌ Error: {e}")
                failed.append({
                    'faculty_name': faculty_name,
                    'error': str(e)
                })
        
        # Summary
        print()
        print("=" * 70)
        print("BATCH GENERATION COMPLETE")
        print("=" * 70)
        print()
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        print()
        
        if successful:
            print("Successfully Generated Cards:")
            print("-" * 70)
            total_funding = sum(card['funding'] for card in successful)
            
            for i, card in enumerate(successful, 1):
                print(f"{i:2}. {card['faculty_name']:30} (${card['funding']:,.0f})")
            
            print("-" * 70)
            print(f"Total Funding Represented: ${total_funding:,.0f}")
            print()
        
        if failed:
            print("Failed:")
            print("-" * 70)
            for fail in failed:
                print(f"  • {fail['faculty_name']}: {fail['error']}")
            print()
        
        print("View cards at: http://localhost:8000/api/v1/impact-cards?sdg=7&status=draft")
        print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch generate SDG 7 impact cards")
    parser.add_argument("--limit", type=int, default=10, help="Number of cards to generate (default: 10)")
    
    args = parser.parse_args()
    
    asyncio.run(batch_generate_sdg7_cards(limit=args.limit))
