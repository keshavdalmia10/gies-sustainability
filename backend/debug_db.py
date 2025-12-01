import asyncio
from sqlalchemy import select, func
from app.database import AsyncSessionLocal
from app.models import Faculty, Publication
import app.models_extended  # Register extended models
import app.models_networking  # Register networking models

from sqlalchemy import desc, case

async def check_data():
    async with AsyncSessionLocal() as db:
        print("Running Analytics Query...")
        query = (
            select(
                Faculty.department,
                func.count(Publication.article_uuid).label("count"),
                func.sum(case((Publication.is_sustain == True, 1), else_=0)).label("sustain_count"),
                func.sum(case((Publication.journal_title.is_not(None), 1), else_=0)).label("top_journal_count")
            )
            .join(Publication, Faculty.person_uuid == Publication.person_uuid)
            .where(Faculty.department.is_not(None))
            .group_by(Faculty.department)
            .order_by(desc("count"))
            .limit(5)
        )
        
        try:
            result = await db.execute(query)
            departments = result.fetchall()
            print(f"Result count: {len(departments)}")
            for row in departments:
                print(f"Row: {row}")
                try:
                    print(f"Count attr: {row.count}")
                except Exception as e:
                    print(f"Error accessing row.count: {e}")
        except Exception as e:
            print(f"Query failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_data())
