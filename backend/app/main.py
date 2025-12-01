"""
FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.database import init_db, close_db
from app.routers import faculty, publications, impacts, impact_cards, evaluation, feedback, decision_support, ml, card_generator, extended_data, data_sources, verification, networking

load_dotenv()

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=os.getenv("APP_NAME", "Gies Sustainability Impact API"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="API for the Gies College Sustainability Impact Dashboard",
    lifespan=lifespan
)

# CORS middleware
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
app.include_router(data_sources.router, prefix="/api/v1/data-sources", tags=["Data Sources"])
app.include_router(verification.router, prefix="/api/v1/verification", tags=["Faculty Verification"])
app.include_router(networking.router, prefix="/api/v1/networking", tags=["Networking"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Gies Sustainability Impact API",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
