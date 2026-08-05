import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from atlas.config.settings import settings
from atlas.database.session import engine
from atlas.database.models import Base
from atlas.api.v1.auth import router as auth_router
from atlas.api.v1.candidates import router as candidates_router
from atlas.api.v1.jobs import router as jobs_router
from atlas.api.v1.search import router as search_router
from atlas.api.v1.copilot import router as copilot_router
from atlas.api.v1.billing import router as billing_router
from atlas.api.v1.video import router as video_router
from atlas.api.v1.meet import router as meet_router
from atlas.api.v1.community import router as community_router
from atlas.api.v1.marketplace import router as marketplace_router
from atlas.api.v1.sso import router as sso_router
from atlas.api.v1.developer import router as developer_router
from atlas.api.v1.automations import router as automations_router
from atlas.api.v1.integrations import router as integrations_router
from atlas.api.v1.analytics import router as analytics_router
from atlas.api.v1.academy import router as academy_router
from atlas.api.v1.career import router as career_router
from atlas.api.v1.tv import router as tv_router
from atlas.database import tv_models  # registers TV models with Base metadata  # noqa: F401
from atlas.api.v1.tv import seed_tv_videos

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing database tables...")
    from sqlalchemy import text
    async with engine.begin() as conn:
        # Create all tables first if they don't exist
        await conn.run_sync(Base.metadata.create_all)
        # Dynamic schema migration patches
        await conn.execute(text("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS billing_customer_id VARCHAR(255) NULL"))
        await conn.execute(text("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS billing_subscription_id VARCHAR(255) NULL"))
        await conn.execute(text("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS billing_provider VARCHAR(255) NULL"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS video_path VARCHAR(255) NULL"))
        await conn.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS video_path VARCHAR(255) NULL"))
        # Run column alterations after tables exist
        await conn.execute(text("ALTER TABLE posts ADD COLUMN IF NOT EXISTS post_type VARCHAR(255) DEFAULT 'discussion' NOT NULL"))
        # Atlas Academy migrations
        await conn.execute(text("CREATE TABLE IF NOT EXISTS academy_instructors (id SERIAL PRIMARY KEY)"))
        await conn.execute(text("CREATE TABLE IF NOT EXISTS academy_courses (id SERIAL PRIMARY KEY)"))
        await conn.execute(text("CREATE TABLE IF NOT EXISTS academy_modules (id SERIAL PRIMARY KEY)"))
        await conn.execute(text("CREATE TABLE IF NOT EXISTS academy_lessons (id SERIAL PRIMARY KEY)"))
        await conn.execute(text("CREATE TABLE IF NOT EXISTS academy_enrollments (id SERIAL PRIMARY KEY)"))
        await conn.execute(text("CREATE TABLE IF NOT EXISTS academy_certificates (id SERIAL PRIMARY KEY)"))
        await conn.execute(text("CREATE TABLE IF NOT EXISTS academy_reviews (id SERIAL PRIMARY KEY)"))
        await conn.execute(text("CREATE TABLE IF NOT EXISTS academy_projects (id SERIAL PRIMARY KEY)"))
        await conn.execute(text("CREATE TABLE IF NOT EXISTS academy_skill_gaps (id SERIAL PRIMARY KEY)"))
        await conn.execute(text("CREATE TABLE IF NOT EXISTS academy_learning_paths (id SERIAL PRIMARY KEY)"))
    logger.info("Database tables verified.")
    # Seed Atlas TV videos if library is empty
    from atlas.database.session import SessionLocal
    async with SessionLocal() as seed_db:
        await seed_tv_videos(seed_db)
    yield

    # Shutdown actions: Close provider HTTP sessions
    logger.info("Initiating application shutdown and cleaning up connection pools...")
    from atlas.ai.factory import AIProviderFactory

    for ai_provider in list(AIProviderFactory._ai_cache.values()):
        if hasattr(ai_provider, "close"):
            await ai_provider.close()
    for embed_provider in list(AIProviderFactory._embed_cache.values()):
        if hasattr(embed_provider, "close"):
            await embed_provider.close()
    logger.info("Shutdown lifecycle cleanup completed.")


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# CORS configuration to allow local Vite server requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route mounts
app.include_router(
    auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"]
)
app.include_router(
    candidates_router, prefix=f"{settings.API_V1_STR}/candidates", tags=["Candidates"]
)
app.include_router(jobs_router, prefix=f"{settings.API_V1_STR}/jobs", tags=["Jobs"])
app.include_router(
    search_router, prefix=f"{settings.API_V1_STR}/search", tags=["Search"]
)
app.include_router(
    copilot_router, prefix=f"{settings.API_V1_STR}/copilot", tags=["Copilot"]
)
app.include_router(
    billing_router, prefix=f"{settings.API_V1_STR}/billing", tags=["Billing"]
)
app.include_router(
    video_router, prefix=f"{settings.API_V1_STR}/video", tags=["Video"]
)
app.include_router(
    meet_router, prefix=f"{settings.API_V1_STR}/meet", tags=["Meetings"]
)
app.include_router(
    community_router, prefix=f"{settings.API_V1_STR}/community", tags=["Community"]
)
app.include_router(
    marketplace_router, prefix=f"{settings.API_V1_STR}/marketplace", tags=["Marketplace"]
)
app.include_router(
    sso_router, prefix=f"{settings.API_V1_STR}/sso", tags=["SSO"]
)
app.include_router(
    developer_router, prefix=f"{settings.API_V1_STR}/developer", tags=["Developer"]
)
app.include_router(
    automations_router, prefix=f"{settings.API_V1_STR}/automations", tags=["Automations"]
)
app.include_router(
    integrations_router, prefix=f"{settings.API_V1_STR}/integrations", tags=["Integrations"]
)
app.include_router(
    analytics_router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Analytics"]
)
app.include_router(
    academy_router, prefix=f"{settings.API_V1_STR}/academy", tags=["Academy"]
)
app.include_router(
    career_router, prefix=f"{settings.API_V1_STR}/career", tags=["Career"]
)
app.include_router(
    tv_router, prefix=f"{settings.API_V1_STR}/tv", tags=["Atlas TV"]
)

from fastapi.staticfiles import StaticFiles
app.mount(
    f"{settings.API_V1_STR}/uploads",
    StaticFiles(directory=settings.UPLOAD_DIR),
    name="uploads"
)


@app.get("/health")
def health_check():
    return {"status": "healthy", "project": settings.PROJECT_NAME}
