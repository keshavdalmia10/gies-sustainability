import asyncio
import random
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_engine, Base, AsyncSessionLocal
from app.models_networking import Student, Skill, Interest
from app import models, models_extended
from sqlalchemy import select

from sqlalchemy import select, text

from sqlalchemy.orm import selectinload

async def populate_data():
    async with AsyncSessionLocal() as db:
        print("Creating dummy data...")
        
        # Ensure column exists (Migration hack for MVP)
        try:
            await db.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS impact_points INTEGER DEFAULT 0"))
            await db.commit()
            print("Added impact_points column if not exists.")
        except Exception as e:
            print(f"Column migration warning: {e}")
            await db.rollback()
        
        # 1. Create Skills
        skills_list = ["Python", "React", "Data Analysis", "Sustainability", "Finance", "Marketing", "AI", "Machine Learning", "Public Speaking", "Project Management"]
        db_skills = []
        for name in skills_list:
            # Check if exists
            result = await db.execute(select(Skill).where(Skill.name == name))
            skill = result.scalar_one_or_none()
            if not skill:
                skill = Skill(name=name)
                db.add(skill)
            db_skills.append(skill)
            
        # 2. Create Interests
        interests_list = ["Climate Change", "Social Impact", "Renewable Energy", "EdTech", "FinTech", "Healthcare", "Urban Planning", "Conservation"]
        db_interests = []
        for name in interests_list:
            result = await db.execute(select(Interest).where(Interest.name == name))
            interest = result.scalar_one_or_none()
            if not interest:
                interest = Interest(name=name)
                db.add(interest)
            db_interests.append(interest)
            
        await db.commit()
        
        # Refresh to get IDs
        for s in db_skills: await db.refresh(s)
        for i in db_interests: await db.refresh(i)
        
        # 3. Create Students (Leaderboard Data)
        students_data = [
            {"name": "Alice Chen", "major": "Computer Science", "points": 150, "skills": ["Python", "Sustainability", "AI"], "interests": ["Climate Change"]},
            {"name": "Bob Smith", "major": "Finance", "points": 120, "skills": ["Finance", "Data Analysis"], "interests": ["FinTech"]},
            {"name": "Charlie Davis", "major": "Environmental Science", "points": 90, "skills": ["Sustainability", "Data Analysis"], "interests": ["Renewable Energy"]},
            {"name": "Diana Prince", "major": "Marketing", "points": 80, "skills": ["Marketing", "Public Speaking"], "interests": ["Social Impact"]},
            {"name": "Evan Wright", "major": "Business Administration", "points": 60, "skills": ["Project Management"], "interests": ["EdTech"]},
            {"name": "Fiona Gallagher", "major": "Social Work", "points": 40, "skills": ["Sustainability", "Public Speaking"], "interests": ["Social Impact"]},
            {"name": "George Miller", "major": "Economics", "points": 30, "skills": ["Data Analysis"], "interests": ["Urban Planning"]},
            {"name": "Hannah Lee", "major": "Data Science", "points": 20, "skills": ["Python", "Data Analysis", "Machine Learning"], "interests": ["Healthcare"]},
            {"name": "Ian Malcolm", "major": "Mathematics", "points": 10, "skills": ["Python"], "interests": ["Conservation"]},
            {"name": "Julia Roberts", "major": "Arts", "points": 0, "skills": ["Public Speaking"], "interests": ["Arts"]},
        ]
        
        for s_data in students_data:
            # Check if exists with relationships loaded
            result = await db.execute(
                select(Student)
                .options(selectinload(Student.skills), selectinload(Student.interests))
                .where(Student.email == f"{s_data['name'].lower().replace(' ', '.')}@example.com")
            )
            student = result.scalar_one_or_none()
            
            if not student:
                student = Student(
                    name=s_data["name"],
                    email=f"{s_data['name'].lower().replace(' ', '.')}@example.com",
                    major=s_data["major"],
                    year=random.choice(["Freshman", "Sophomore", "Junior", "Senior"]),
                    bio=f"Passionate about {random.choice(interests_list)}",
                    impact_points=s_data["points"]
                )
                db.add(student)
                
                # Assign specific skills
                for skill_name in s_data.get("skills", []):
                    # Find skill object
                    for db_skill in db_skills:
                        if db_skill.name == skill_name:
                            student.skills.append(db_skill)
                            break
                            
                # Assign specific interests
                for interest_name in s_data.get("interests", []):
                    for db_interest in db_interests:
                        if db_interest.name == interest_name:
                            student.interests.append(db_interest)
                            break
            else:
                # Update points if exists
                student.impact_points = s_data["points"]
                # Clear and re-add skills/interests to ensure match
                # Note: With selectinload, we can modify the collections directly
                student.skills.clear()
                student.interests.clear()
                
                for skill_name in s_data.get("skills", []):
                    for db_skill in db_skills:
                        if db_skill.name == skill_name:
                            student.skills.append(db_skill)
                            break
                            
                for interest_name in s_data.get("interests", []):
                    for db_interest in db_interests:
                        if db_interest.name == interest_name:
                            student.interests.append(db_interest)
                            break
                            
                db.add(student)
                
        await db.commit()
        print("Dummy data populated successfully!")

if __name__ == "__main__":
    asyncio.run(populate_data())
