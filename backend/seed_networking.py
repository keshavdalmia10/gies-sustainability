import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import async_engine, Base, get_db
from app import models, models_networking, models_extended
from sqlalchemy.future import select

async def seed_data():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Check if data exists - REMOVED check to force seed
        # result = await session.execute(select(models_networking.Student))
        # if result.scalars().first():
        #     print("Data already exists. Skipping seed.")
        #     return

        print("Seeding data...")

        # Skills
        skills = [
            "Python", "React", "Data Analysis", "Machine Learning", 
            "Sustainability", "Project Management", "Public Speaking",
            "Java", "C++", "SQL", "Figma", "UI/UX Design"
        ]
        
        skill_objs = {}
        for s_name in skills:
            # Check if exists
            result = await session.execute(select(models_networking.Skill).where(models_networking.Skill.name == s_name))
            existing = result.scalars().first()
            if existing:
                skill_objs[s_name] = existing
            else:
                skill = models_networking.Skill(name=s_name)
                session.add(skill)
                skill_objs[s_name] = skill
        
        # Interests
        interests = [
            "Climate Change", "Renewable Energy", "Social Impact", 
            "EdTech", "FinTech", "Healthcare"
        ]
        
        interest_objs = {}
        for i_name in interests:
            # Check if exists
            result = await session.execute(select(models_networking.Interest).where(models_networking.Interest.name == i_name))
            existing = result.scalars().first()
            if existing:
                interest_objs[i_name] = existing
            else:
                interest = models_networking.Interest(name=i_name)
                session.add(interest)
                interest_objs[i_name] = interest
            
        await session.commit()

        # Students
        students = [
            {
                "name": "Alice Chen",
                "email": "alice@illinois.edu",
                "major": "Computer Science",
                "year": "Junior",
                "bio": "Passionate about using tech for social good.",
                "skills": ["Python", "React", "UI/UX Design"],
                "interests": ["EdTech", "Social Impact"]
            },
            {
                "name": "Bob Smith",
                "email": "bob@illinois.edu",
                "major": "Business",
                "year": "Senior",
                "bio": "Looking for technical co-founders.",
                "skills": ["Project Management", "Public Speaking", "Data Analysis"],
                "interests": ["FinTech", "Climate Change"]
            },
            {
                "name": "Charlie Kim",
                "email": "charlie@illinois.edu",
                "major": "Data Science",
                "year": "Sophomore",
                "bio": "Love crunching numbers.",
                "skills": ["Python", "SQL", "Machine Learning", "Data Analysis"],
                "interests": ["Healthcare", "Social Impact"]
            }
        ]

        for s_data in students:
            student = models_networking.Student(
                name=s_data["name"],
                email=s_data["email"],
                major=s_data["major"],
                year=s_data["year"],
                bio=s_data["bio"]
            )
            
            for sk in s_data["skills"]:
                if sk in skill_objs:
                    student.skills.append(skill_objs[sk])
            
            for i in s_data["interests"]:
                if i in interest_objs:
                    student.interests.append(interest_objs[i])
            
            session.add(student)

        # Faculty (Mocking existing faculty UUIDs or creating new ones if needed)
        # For this seed, we'll create new Faculty entries if they don't exist in the main Faculty table
        # But since we don't have easy access to existing Faculty UUIDs without querying, 
        # let's just create a few dummy Faculty entries in the main table first if possible, 
        # or just assume we can add them to the networking tables.
        # Actually, models_networking.Faculty is a relationship to models.Faculty? 
        # No, looking at previous context, we added relationships to models.Faculty.
        
        # Let's create some Faculty in the main table first
        faculty_members = [
            {
                "name": "Dr. Emily White",
                "email": "emily@illinois.edu",
                "department": "Computer Science",
                "skills": ["Machine Learning", "Python", "AI"],
                "interests": ["Climate Change"]
            },
            {
                "name": "Prof. David Brown",
                "email": "david@illinois.edu",
                "department": "Business",
                "skills": ["Sustainability", "Project Management"],
                "interests": ["Renewable Energy"]
            }
        ]
        
        for f_data in faculty_members:
            # Create Faculty
            faculty = models.Faculty(
                name=f_data["name"],
                email=f_data["email"],
                department=f_data["department"]
            )
            session.add(faculty)
            
            # Add Skills/Interests
            for sk in f_data["skills"]:
                if sk in skill_objs:
                    faculty.skills.append(skill_objs[sk])
            
            for i in f_data["interests"]:
                if i in interest_objs:
                    faculty.interests.append(interest_objs[i])

        await session.commit()
        print("Seed completed!")

if __name__ == "__main__":
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    asyncio.run(seed_data())
