import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import async_engine, Base
from app import models, models_networking
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

async def inspect_data():
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        print("--- Skills ---")
        result = await session.execute(select(models_networking.Skill))
        skills = result.scalars().all()
        for s in skills:
            print(f"- {s.name}")

        print("\n--- Students ---")
        result = await session.execute(
            select(models_networking.Student)
            .options(selectinload(models_networking.Student.skills))
        )
        students = result.scalars().all()
        for s in students:
            skill_names = [sk.name for sk in s.skills]
            print(f"- {s.name}: {skill_names}")

if __name__ == "__main__":
    asyncio.run(inspect_data())
