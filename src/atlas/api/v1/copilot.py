import logging
from typing import List
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.database.session import get_db
from atlas.database.models import User
from atlas.api.deps import get_current_user
from atlas.services.copilot import CopilotService

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Schemas ---


class CopilotChatRequest(BaseModel):
    query: str


class CopilotChatResponse(BaseModel):
    reply: str


class ChatMessageResponse(BaseModel):
    role: str  # "user" or "assistant"
    content: str


# --- Routes ---


@router.post("/chat", response_model=CopilotChatResponse)
async def copilot_chat(
    payload: CopilotChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Processes conversational query inside tenant context, updating user chat logs."""
    copilot_service = CopilotService(db, tenant_id=int(current_user.tenant_id))
    reply = await copilot_service.answer_query(payload.query, current_user.id)
    return {"reply": reply}


@router.get("/history", response_model=List[ChatMessageResponse])
async def get_chat_history(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Retrieves chat log history for the user within this tenant workspace."""
    copilot_service = CopilotService(db, tenant_id=int(current_user.tenant_id))
    return await copilot_service.get_history(current_user.id)


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_chat_history(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Clears all chat history for this user in this tenant workspace."""
    copilot_service = CopilotService(db, tenant_id=int(current_user.tenant_id))
    await copilot_service.clear_history(current_user.id)
    return None
