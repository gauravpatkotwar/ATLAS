import logging
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.database.session import get_db
from atlas.database.models import User
from atlas.api.deps import get_current_user
from atlas.services.candidate import CandidateService

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Response/Request Schemas ---


class CandidateResponse(BaseModel):
    id: int
    tenant_id: int
    name: str
    email: Optional[EmailStr]
    phone: Optional[str]
    location: Optional[str]
    skills: List[str]
    education: List[Any]
    experience: List[Any]
    summary: Optional[str]
    linkedin: Optional[str]
    github: Optional[str]
    portfolio: Optional[str]
    resume_path: Optional[str]
    video_path: Optional[str] = None
    ai_score: float
    recruiter_rating: float

    model_config = {"from_attributes": True}


class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    summary: Optional[str] = None
    recruiter_rating: Optional[float] = None


class CandidateQuestionnaire(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    qualification: str  # e.g., "B.Tech in Computer Science"
    skills: List[str]  # e.g., ["Python", "React", "SQL", "Docker"]
    experience_years: float = 0.0
    work_highlights: Optional[str] = None
    projects: Optional[str] = None
    desired_role: Optional[str] = None


class IntakeChatMessage(BaseModel):
    role: str
    content: str


class IntakeChatPayload(BaseModel):
    messages: List[IntakeChatMessage]


# --- Route Endpoints ---


@router.post(
    "/upload", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED
)
async def upload_candidate_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Uploads a candidate resume, verifying billing quotas and running transactional pipeline."""
    candidate_service = CandidateService(db, tenant_id=int(current_user.tenant_id))

    try:
        file_content = await file.read()
        context = await candidate_service.upload_and_parse_resume(
            filename=file.filename or "resume",
            file_content=file_content,
            current_user_id=int(current_user.id),
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error handling upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload handler failed: {e}",
        )

    if not context.data.get("success"):
        errors_summary = (
            " | ".join(context.errors) if context.errors else "Unknown parsing error."
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Upload transaction failed: {errors_summary}",
        )

    return context.data.get("candidate_obj")


@router.get("", response_model=List[CandidateResponse])
async def get_all_candidates(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves candidates list with pagination scoped to this tenant."""
    candidate_service = CandidateService(db, tenant_id=int(current_user.tenant_id))
    return await candidate_service.get_candidates(skip=skip, limit=limit)


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate_by_id(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetches candidate by ID scoped to this tenant."""
    candidate_service = CandidateService(db, tenant_id=int(current_user.tenant_id))
    candidate = await candidate_service.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found.",
        )
    return candidate


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate_by_id(
    candidate_id: int,
    payload: CandidateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Updates candidate profile fields within this tenant."""
    candidate_service = CandidateService(db, tenant_id=int(current_user.tenant_id))
    update_data = payload.model_dump(exclude_unset=True)
    try:
        return await candidate_service.update_candidate(candidate_id, update_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate_by_id(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deletes candidate within this tenant context and removes them from the FAISS vector index."""
    candidate_service = CandidateService(db, tenant_id=int(current_user.tenant_id))
    success = await candidate_service.delete_candidate(candidate_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found.",
        )
    return None


# --- WebRTC Calling Signaling endpoints ---

class CallInitiateRequest(BaseModel):
    candidate_id: int
    sdp_offer: Optional[str] = None

class CallRespondRequest(BaseModel):
    status: str  # "accepted" | "rejected" | "ended"
    sdp_answer: Optional[str] = None

ACTIVE_CALLS = {}  # candidate_id -> CallState dict

@router.post("/call/initiate")
def initiate_call(payload: CallInitiateRequest, current_user: User = Depends(get_current_user)):
    ACTIVE_CALLS[payload.candidate_id] = {
        "status": "ringing",
        "sdp_offer": payload.sdp_offer,
        "sdp_answer": None,
        "caller_name": current_user.email
    }
    return {"status": "success", "call": ACTIVE_CALLS[payload.candidate_id]}

@router.post("/call/respond/{candidate_id}")
def respond_call(candidate_id: int, payload: CallRespondRequest):
    if candidate_id in ACTIVE_CALLS:
        ACTIVE_CALLS[candidate_id]["status"] = payload.status
        if payload.sdp_answer:
            ACTIVE_CALLS[candidate_id]["sdp_answer"] = payload.sdp_answer
        return {"status": "success", "call": ACTIVE_CALLS[candidate_id]}
    raise HTTPException(status_code=404, detail="No active call found")

@router.get("/call/status/{candidate_id}")
def get_call_status(candidate_id: int):
    call = ACTIVE_CALLS.get(candidate_id)
    if call:
        return call
    return {"status": "idle"}

