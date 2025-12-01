import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import async_engine, Base
from app.models_networking import Student
from app.models import ImpactCard, ImpactValidation
from sqlalchemy import select
import uuid

@pytest.mark.asyncio
async def test_gamification_flow():
    # Setup: Ensure tables exist
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Create a Student
        student_id = uuid.uuid4()
        student_data = {
            "name": "Gamification Tester",
            "email": f"test.game.{student_id}@example.com",
            "major": "Data Science",
            "year": "Junior",
            "bio": "Testing points",
            "skills": [],
            "interests": []
        }
        # We need to manually insert because the student endpoint might not return the ID or allow setting it easily for this test
        # But let's try the endpoint first if it exists, otherwise direct DB
        # Actually, let's just use the networking endpoint if available
        
        # Direct DB insertion for control
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            student = Student(
                student_id=student_id,
                name=student_data["name"],
                email=student_data["email"],
                major=student_data["major"],
                impact_points=0
            )
            db.add(student)
            
            # Create an Impact Card to validate
            card_id = uuid.uuid4()
            card = ImpactCard(
                card_id=card_id,
                title="Test Card",
                summary="Summary",
                sdg=1,
                status="published"
            )
            db.add(card)
            await db.commit()
            
        # 2. Validate the card as this student
        validation_data = {
            "visitor_id": str(student_id),
            "status": "approved"
        }
        response = await ac.post(f"/api/v1/impact-cards/{card_id}/validate", json=validation_data)
        assert response.status_code == 200
        data = response.json()
        assert data["points_awarded"] == 10
        
        # 3. Check Leaderboard
        response = await ac.get("/api/v1/gamification/leaderboard")
        assert response.status_code == 200
        leaderboard = response.json()
        
        # Find our student
        found = False
        for entry in leaderboard:
            if entry["name"] == "Gamification Tester":
                assert entry["points"] == 10
                found = True
                break
        assert found
