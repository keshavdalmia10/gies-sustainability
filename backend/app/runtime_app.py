from contextlib import asynccontextmanager
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models, models_extended, models_networking  # noqa: F401
from app.database import close_db, init_db
from app.routers import analytics, donors, gamification, impact_cards, networking, news

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title=os.getenv("APP_NAME", "Gies Sustainability Impact API"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="Lean runtime API for the Gies Sustainability Impact Dashboard",
    lifespan=lifespan,
)

default_origins = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"
origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", default_origins).split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(impact_cards.router, prefix="/api/v1/impact-cards", tags=["Impact Cards"])
app.include_router(networking.router, prefix="/api/v1/networking", tags=["Networking"])
app.include_router(news.router, prefix="/api/v1/news", tags=["News"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(gamification.router, prefix="/api/v1/gamification", tags=["Gamification"])
app.include_router(donors.router, prefix="/api/v1/donors", tags=["Donors"])


@app.get("/")
async def root():
    return {
        "message": "Gies Sustainability Impact API",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
