#!/usr/bin/env python3
"""
Load data from data.csv into the PostgreSQL database

This script imports faculty and publication data from the existing CSV file
into the database, creating faculty records and publications with SDG classifications.
"""

import asyncio
import pandas as pd
import sys
from pathlib import Path
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import Faculty, Publication
from app.database import DATABASE_ASYNC_URL


class DataLoader:
    """Load data from CSV into database"""
    
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.engine = create_async_engine(DATABASE_ASYNC_URL, echo=True)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def load_csv(self) -> pd.DataFrame:
        """Load and parse CSV file"""
        print(f"📂 Loading data from {self.csv_path}...")
        df = pd.read_csv(self.csv_path)
        print(f"✅ Loaded {len(df)} records")
        return df
    
    async def create_or_get_faculty(self, session: AsyncSession, row: pd.Series) -> Faculty:
        """Create faculty if not exists, or return existing"""
        person_uuid = UUID(row['person_uuid'])
        
        # Check if faculty exists
        result = await session.execute(
            select(Faculty).where(Faculty.person_uuid == person_uuid)
        )
        faculty = result.scalar_one_or_none()
        
        if faculty:
            return faculty
        
        # Create new faculty
        faculty = Faculty(
            person_uuid=person_uuid,
            name=row['name'],
            email=row['email'] if pd.notna(row['email']) else None,
            department=row['department'] if pd.notna(row['department']) else None,
            active=bool(row['active']) if pd.notna(row['active']) else True
        )
        
        session.add(faculty)
        return faculty
    
    async def create_publication(self, session: AsyncSession, row: pd.Series) -> Publication:
        """Create publication record"""
        # Parse keywords
        keywords = []
        if pd.notna(row['keywords']):
            keywords = [k.strip() for k in str(row['keywords']).split(';')]
        
        # Convert SDG fields (handle NaN)
        def safe_int(val):
            if pd.notna(val) and val != 0.0:
                return int(val)
            return None
        
        def safe_float(val):
            if pd.notna(val):
                return float(val)
            return None
        
        # Check if publication exists
        result = await session.execute(
            select(Publication).where(Publication.article_uuid == UUID(row['article_uuid']))
        )
        existing_pub = result.scalar_one_or_none()
        
        if existing_pub:
            return existing_pub

        publication = Publication(
            article_uuid=UUID(row['article_uuid']),
            person_uuid=UUID(row['person_uuid']),
            title=row['title'] if pd.notna(row['title']) else 'Untitled',
            abstract=row['abstract'] if pd.notna(row['abstract']) else None,
            publication_year=safe_int(row['publication_year']),
            doi=row['doi'] if pd.notna(row['doi']) else None,
            journal_title=row['journal_title'] if pd.notna(row['journal_title']) else None,
            journal_issn=row['journal_issn'] if pd.notna(row['journal_issn']) else None,
            keywords=keywords if keywords else None,
            is_sustain=bool(row['is_sustain']) if pd.notna(row['is_sustain']) else False,
            sdg_top1=safe_int(row['top 1']),
            sdg_top2=safe_int(row['top 2']),
            sdg_top3=safe_int(row['top 3']),
            sdg_confidence=safe_float(row.get('sdg_confidence', None)),
            source=row['source'] if pd.notna(row['source']) else 'data.csv'
        )
        
        session.add(publication)
        return publication
    
    async def load_data(self):
        """Main loading function"""
        df = await self.load_csv()
        
        async with self.async_session() as session:
            try:
                print("\n📊 Processing records...")
                
                faculty_created = 0
                publications_created = 0
                
                # Group by person to minimize faculty lookups
                for person_uuid, person_df in df.groupby('person_uuid'):
                    # Get first row for faculty info
                    first_row = person_df.iloc[0]
                    
                    # Create/get faculty
                    faculty = await self.create_or_get_faculty(session, first_row)
                    if faculty.created_at is None:  # New faculty
                        faculty_created += 1
                    
                    # Create publications
                    for _, row in person_df.iterrows():
                        await self.create_publication(session, row)
                        publications_created += 1
                    
                    # Commit every 10 faculty to avoid memory issues
                    if faculty_created % 10 == 0:
                        await session.commit()
                        print(f"  💾 Committed: {faculty_created} faculty, {publications_created} publications")
                
                # Final commit
                await session.commit()
                
                print(f"\n✅ Data loading complete!")
                print(f"  👥 Faculty created: {faculty_created}")
                print(f"  📄 Publications created: {publications_created}")
                
            except Exception as e:
                await session.rollback()
                print(f"\n❌ Error loading data: {e}")
                raise
    
    async def cleanup(self):
        """Close database connections"""
        await self.engine.dispose()


async def main():
    """Main entry point"""
    # Get CSV path from command line or use default
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "../data.csv"
    
    if not Path(csv_path).exists():
        print(f"❌ CSV file not found: {csv_path}")
        print(f"Usage: python load_data.py [path/to/data.csv]")
        sys.exit(1)
    
    loader = DataLoader(csv_path)
    
    try:
        await loader.load_data()
    finally:
        await loader.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
