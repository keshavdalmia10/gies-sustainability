"""
FastAPI Main Application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import close_db, init_db, ping_db
# Import models to ensure they are registered
from app import models
from app import models_extended
from app import models_networking
from app.routers import faculty, publications, impacts, impact_cards, evaluation, feedback, decision_support, ml, card_generator, extended_data, verification, networking, news, analytics, gamification, donors
from app.settings import get_settings

settings = get_settings("http://localhost:3000,http://127.0.0.1:3000")

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_init_db:
        await init_db()
    else:
        await ping_db()
    yield
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for the Gies College Sustainability Impact Dashboard",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(faculty.router, prefix="/api/v1/faculty", tags=["Faculty"])
app.include_router(publications.router, prefix="/api/v1/publications", tags=["Publications"])
app.include_router(impacts.router, prefix="/api/v1/impacts", tags=["Impacts"])
app.include_router(impact_cards.router, prefix="/api/v1/impact-cards", tags=["Impact Cards"])
app.include_router(evaluation.router, prefix="/api/v1/evaluation", tags=["Evaluation"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["Feedback"])
app.include_router(decision_support.router, prefix="/api/v1/decision-support", tags=["Decision Support"])
app.include_router(ml.router, prefix="/api/v1/ml", tags=["Machine Learning"])
app.include_router(card_generator.router, prefix="/api/v1/card-generator", tags=["Card Generator"])
app.include_router(extended_data.router, prefix="/api/v1/extended", tags=["Extended Data"])
app.include_router(verification.router, prefix="/api/v1/verification", tags=["Faculty Verification"])
app.include_router(networking.router, prefix="/api/v1/networking", tags=["Networking"])
app.include_router(news.router, prefix="/api/v1/news", tags=["News"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(gamification.router, prefix="/api/v1/gamification", tags=["Gamification"])
app.include_router(donors.router, prefix="/api/v1/donors", tags=["Donors"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
@app.get("/api/health", include_in_schema=False)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "environment": settings.app_env}
