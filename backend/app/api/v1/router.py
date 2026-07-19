from fastapi import APIRouter

from app.modules.auth.presentation.api import router as auth_router
from app.modules.companies.presentation.api import router as companies_router
from app.modules.users.presentation.api import router as users_router
from app.modules.candidates.presentation.api import router as candidates_router
from app.modules.jobs.presentation.api import router as jobs_router
from app.modules.matching.presentation.api import router as matching_router
from app.modules.atlas_brain.presentation.api import router as atlas_brain_router
from app.modules.atlas_one.presentation.api import router as atlas_one_router
from app.modules.communication.presentation.api import router as communication_router
from app.modules.interview_intelligence.presentation.api import router as interview_router
from app.modules.analytics.presentation.api import router as analytics_router
from app.modules.workflows.presentation.api import router as workflows_router
from app.modules.admin.presentation.api import router as admin_router
from app.modules.api_platform.presentation.api import router as api_platform_router


api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(companies_router, prefix="/companies", tags=["Companies"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(candidates_router, prefix="/candidates", tags=["Candidates"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(matching_router, prefix="/matching", tags=["Matching"])
api_router.include_router(atlas_brain_router, prefix="/atlas-brain", tags=["Atlas Brain"])
api_router.include_router(atlas_one_router, prefix="/atlas-one", tags=["Atlas One"])
api_router.include_router(communication_router, prefix="/communication", tags=["Communication"])
api_router.include_router(interview_router, prefix="/interviews", tags=["Interviews"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(workflows_router, prefix="/workflows", tags=["Workflows"])
api_router.include_router(admin_router, prefix="/admin", tags=["Administration"])
api_router.include_router(api_platform_router, prefix="/api-platform", tags=["API Platform"])