import logging
from typing import List, Optional, Any, Dict
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from atlas.database.session import get_db
from atlas.database.models import User, WorkflowRule
from atlas.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Pydantic Schemas ---
class WorkflowRuleCreate(BaseModel):
    name: str
    trigger_event: str
    conditions: Dict[str, Any]
    action_type: str
    action_payload: Dict[str, Any]

class WorkflowRuleResponse(BaseModel):
    id: int
    name: str
    trigger_event: str
    conditions: Dict[str, Any]
    action_type: str
    action_payload: Dict[str, Any]
    is_active: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# --- API Routes ---

@router.get("/workflows", response_model=List[WorkflowRuleResponse])
async def list_workflows(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists all automated workflows configurations for the tenant."""
    stmt = select(WorkflowRule).where(WorkflowRule.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("/workflows", response_model=WorkflowRuleResponse)
async def create_workflow(
    payload: WorkflowRuleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new automated workflow rule."""
    rule = WorkflowRule(
        tenant_id=current_user.tenant_id,
        name=payload.name,
        trigger_event=payload.trigger_event,
        conditions=payload.conditions,
        action_type=payload.action_type,
        action_payload=payload.action_payload,
        is_active=True
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/workflows/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Deletes an automated workflow configuration."""
    stmt = select(WorkflowRule).where(WorkflowRule.id == id, WorkflowRule.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    rule = res.scalars().first()
    if not rule:
        raise HTTPException(status_code=404, detail="Workflow rule not found")
    
    await db.delete(rule)
    await db.commit()
    return


@router.post("/workflows/{id}/toggle", response_model=WorkflowRuleResponse)
async def toggle_workflow(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Toggles active/inactive state of a workflow rule."""
    stmt = select(WorkflowRule).where(WorkflowRule.id == id, WorkflowRule.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    rule = res.scalars().first()
    if not rule:
        raise HTTPException(status_code=404, detail="Workflow rule not found")

    rule.is_active = not rule.is_active
    await db.commit()
    await db.refresh(rule)
    return rule
