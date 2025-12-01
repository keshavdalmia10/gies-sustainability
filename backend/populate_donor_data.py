import asyncio
from sqlalchemy import select, update
from app.database import async_engine, AsyncSessionLocal
from app import models, models_extended, models_networking
import uuid

async def populate_data():
    async with AsyncSessionLocal() as session:
        # 1. Update a faculty member with current_work
        result = await session.execute(select(models.Faculty).limit(1))
        faculty = result.scalars().first()
        
        if faculty:
            print(f"Updating faculty: {faculty.name}")
            faculty.current_work = "Developing a low-cost solar water purification system for arid regions."
            faculty.research_interests = ["Renewable Energy", "Water Sanitation", "Sustainability"]
            session.add(faculty)
        else:
            print("No faculty found. Creating one.")
            faculty = models.Faculty(
                name="Dr. Sarah Green",
                email="sarah.green@university.edu",
                department="Civil Engineering",
                current_work="Developing a low-cost solar water purification system for arid regions.",
                research_interests=["Renewable Energy", "Water Sanitation"]
            )
            session.add(faculty)
            await session.flush()

        # 2. Create a Student Project
        project = models_extended.StudentProject(
            project_title="AI for Crop Disease Detection",
            description="Using computer vision to detect early signs of disease in maize crops to improve yield in developing countries.",
            project_type="Capstone",
            advisor_uuid=faculty.person_uuid,
            student_names=["Alice Smith", "Bob Jones"],
            sdg_primary=2
        )
        session.add(project)
        
        await session.commit()
        print("Dummy data populated successfully.")

if __name__ == "__main__":
    asyncio.run(populate_data())
