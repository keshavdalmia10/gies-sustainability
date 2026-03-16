from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models, models_extended, models_networking  # noqa: F401
from app.database import close_db, init_db, ping_db
from app.routers import analytics, donors, faculty, gamification, impact_cards, networking, news
from app.settings import get_settings

settings = get_settings(
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_init_db:
        await init_db()
    else:
        await ping_db()
    yield
    await close_db()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Lean runtime API for the Gies Sustainability Impact Dashboard",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router, prefix, tag in [
    (impact_cards.router, "impact-cards", "Impact Cards"),
    (networking.router, "networking", "Networking"),
    (news.router, "news", "News"),
    (analytics.router, "analytics", "Analytics"),
    (gamification.router, "gamification", "Gamification"),
    (donors.router, "donors", "Donors"),
    (faculty.router, "faculty", "Faculty"),
]:
    app.include_router(router, prefix=f"/api/v1/{prefix}", tags=[tag])
    app.include_router(router, prefix=f"/v1/{prefix}", tags=[tag])


@app.get("/")
async def root():
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health")
@app.get("/api/health", include_in_schema=False)
async def health_check():
    return {"status": "healthy", "environment": settings.app_env}
