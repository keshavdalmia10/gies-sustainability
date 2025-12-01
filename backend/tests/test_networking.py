import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import get_db, Base, async_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import asyncio

# Use a separate test database or mock
# For simplicity in this environment, we'll try to use the main app but be careful
# Ideally we should use a test DB.

@pytest.mark.asyncio
async def test_networking_flow():
    # Ensure tables exist
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Create Student
        student_data = {
            "name": "Test Student",
            "email": "test.student@example.com",
            "major": "Computer Science",
            "year": "Senior",
            "bio": "Interested in AI",
            "skills": ["Python", "React"],
            "interests": ["Sustainability", "AI"]
        }
        response = await ac.post("/api/v1/networking/student", json=student_data)
        assert response.status_code == 200 or response.status_code == 400 # 400 if already exists
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == "Test Student"
            assert len(data["skills"]) == 2
            
        # 2. Get Graph
        response = await ac.get("/api/v1/networking/graph")
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        
        # 3. Analyze
        analysis_data = {
            "query": "Python"
        }
        response = await ac.post("/api/v1/networking/analyze", json=analysis_data)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "suggested_connections" in data
