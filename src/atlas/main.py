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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing database tables...")
    from sqlalchemy import text
    async with engine.begin() as conn:
        # Dynamic schema migration patches
        await conn.execute(text("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS billing_customer_id VARCHAR(255) NULL"))
        await conn.execute(text("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS billing_subscription_id VARCHAR(255) NULL"))
        await conn.execute(text("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS billing_provider VARCHAR(255) NULL"))
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified.")
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


@app.get("/health")
def health_check():
    return {"status": "healthy", "project": settings.PROJECT_NAME}
