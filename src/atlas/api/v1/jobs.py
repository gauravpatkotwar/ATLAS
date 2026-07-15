import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.database.session import get_db
from atlas.database.models import User
from atlas.api.deps import get_current_user
from atlas.services.job import JobService
from atlas.api.v1.candidates import CandidateResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Request/Response Schemas ---


class JobCreate(BaseModel):
    title: str
    description: str
    required_skills: List[str]
    salary: Optional[str] = None
    location: Optional[str] = None
    experience_years: int = 0
    employment_type: Optional[str] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    salary: Optional[str] = None
    location: Optional[str] = None
    experience_years: Optional[int] = None
    employment_type: Optional[str] = None
    is_active: Optional[bool] = None


class JobResponse(BaseModel):
    id: int
    tenant_id: int
    title: str
    description: str
    required_skills: List[str]
    salary: Optional[str]
    location: Optional[str]
    experience_years: int
    employment_type: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}


class RecommendationResponse(BaseModel):
    candidate: CandidateResponse
    similarity_score: float
    skills_match_ratio: float
    explanation: str


# --- API Routes ---


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job_opening(
    payload: JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Publishes a new job specification inside this tenant workspace, checking active limits first."""
    job_service = JobService(db, tenant_id=int(current_user.tenant_id))
    try:
        return await job_service.create_job(payload.model_dump())
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("", response_model=List[JobResponse])
async def get_all_job_openings(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists jobs published inside this tenant workspace."""
    job_service = JobService(db, tenant_id=int(current_user.tenant_id))
    return await job_service.get_jobs(skip=skip, limit=limit)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_opening_by_id(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves specific job within tenant boundaries."""
    job_service = JobService(db, tenant_id=int(current_user.tenant_id))
    job = await job_service.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found.",
        )
    return job


@router.put("/{job_id}", response_model=JobResponse)
async def update_job_opening_by_id(
    job_id: int,
    payload: JobUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Updates job specification within tenant boundaries."""
    job_service = JobService(db, tenant_id=int(current_user.tenant_id))
    update_data = payload.model_dump(exclude_unset=True)
    try:
        return await job_service.update_job(job_id, update_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_opening_by_id(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deletes job specification within tenant boundaries."""
    job_service = JobService(db, tenant_id=int(current_user.tenant_id))
    success = await job_service.delete_job(job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found.",
        )
    return None


@router.get("/{job_id}/recommendations", response_model=List[RecommendationResponse])
async def get_job_recommender(
    job_id: int,
    top_k: int = 5,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Recommends and rank candidates matching the job specifications, isolating search context by tenant."""
    job_service = JobService(db, tenant_id=int(current_user.tenant_id))
    try:
        return await job_service.get_recommendations_for_job(job_id, top_k)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


class PublicJobResponse(BaseModel):
    id: int
    title: str
    description: str
    required_skills: List[str]
    salary: Optional[str]
    location: Optional[str]
    experience_years: int
    employment_type: Optional[str]

    model_config = {"from_attributes": True}


@router.get("/{job_id}/public", response_model=PublicJobResponse)
async def get_public_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Exposes job details publicly without authentication."""
    from sqlalchemy.future import select
    from atlas.database.models import Job
    stmt = select(Job).where(Job.id == job_id, Job.is_active == True)
    result = await db.execute(stmt)
    job = result.scalars().first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or is inactive."
        )
    return job


@router.post("/{job_id}/apply", status_code=status.HTTP_201_CREATED)
async def apply_to_public_job(
    job_id: int,
    email: EmailStr = Form(...),
    name: str = Form(...),
    phone: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Enables public candidates to upload a resume and apply to a job opening directly."""
    from sqlalchemy.future import select
    from atlas.database.models import Job
    stmt = select(Job).where(Job.id == job_id, Job.is_active == True)
    result = await db.execute(stmt)
    job = result.scalars().first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or is inactive."
        )

    from atlas.services.candidate import CandidateService
    candidate_service = CandidateService(db, tenant_id=int(job.tenant_id))

    try:
        file_content = await file.read()
        context = await candidate_service.upload_and_parse_resume(
            filename=file.filename or "resume",
            file_content=file_content,
            current_user_id=None,
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error handling public application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Application submission failed: {e}",
        )

    if not context.data.get("success"):
        errors_summary = (
            " | ".join(context.errors) if context.errors else "Unknown parsing error."
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Upload transaction failed: {errors_summary}",
        )

    candidate = context.data.get("candidate_obj")
    candidate.email = email
    candidate.name = name
    if phone:
        candidate.phone = phone
    await db.commit()

    return {"message": "Application submitted successfully!", "candidate_id": candidate.id}
