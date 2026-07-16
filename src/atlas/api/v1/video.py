import logging
import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from atlas.database.session import get_db
from atlas.database.models import User, Candidate
from atlas.api.deps import get_current_user
from atlas.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/candidates/{candidate_id}/video")
async def upload_candidate_video(
    candidate_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Uploads a candidate introduction video and binds it to their profile."""
    # Ensure directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Verify candidate exists under this tenant context
    stmt = select(Candidate).where(
        Candidate.id == candidate_id,
        Candidate.tenant_id == current_user.tenant_id
    )
    result = await db.execute(stmt)
    candidate = result.scalars().first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found."
        )

    # Validate file size and type (basic validation)
    ext = os.path.splitext(file.filename or "")[1].lower() or ".mp4"
    if ext not in [".mp4", ".webm", ".mov", ".mkv"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported video format. Allowed formats: MP4, WebM, MOV."
        )

    unique_filename = f"video_candidate_{candidate_id}_{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    try:
        with open(dest_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        logger.error(f"Failed to write candidate video file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write video file: {e}"
        )

    # Save to database
    candidate.video_path = f"{settings.API_V1_STR}/uploads/{unique_filename}"
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)

    return {"status": "success", "video_path": candidate.video_path}


@router.post("/users/video")
async def upload_user_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Uploads a recruiter introduction video and binds it to their profile."""
    # Ensure directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Validate format
    ext = os.path.splitext(file.filename or "")[1].lower() or ".mp4"
    if ext not in [".mp4", ".webm", ".mov", ".mkv"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported video format. Allowed formats: MP4, WebM, MOV."
        )

    unique_filename = f"video_user_{current_user.id}_{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    try:
        with open(dest_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        logger.error(f"Failed to write user video file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write video file: {e}"
        )

    # Save to database
    stmt = select(User).where(User.id == current_user.id)
    result = await db.execute(stmt)
    user_db = result.scalars().first()
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    user_db.video_path = f"{settings.API_V1_STR}/uploads/{unique_filename}"
    db.add(user_db)
    await db.commit()
    await db.refresh(user_db)

    return {"status": "success", "video_path": user_db.video_path}
