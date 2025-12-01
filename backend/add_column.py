import asyncio
from sqlalchemy import text
from app.database import async_engine

async def add_column():
    async with async_engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE faculty ADD COLUMN current_work TEXT"))
            print("Successfully added 'current_work' column to 'faculty' table.")
        except Exception as e:
            print(f"Error adding column (might already exist): {e}")

if __name__ == "__main__":
    asyncio.run(add_column())
