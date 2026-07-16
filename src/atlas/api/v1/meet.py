import logging
import uuid
import random
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from atlas.database.models import User
from atlas.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory store for meeting rooms
# room_code -> { "participants": { id: name }, "queues": { id: [signals] }, "last_activity": float }
MEETINGS: Dict[str, Dict[str, Any]] = {}

# --- Pydantic Schemas ---
class JoinRequest(BaseModel):
    participant_id: str
    name: str

class SignalRequest(BaseModel):
    sender_id: str
    target_id: str
    type: str
    data: Any

@router.post("/create")
def create_room(current_user: User = Depends(get_current_user)):
    """Generates a random unique room code for a video meeting."""
    # Generate standard format abc-defg-hij
    parts = [
        "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=3)),
        "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=4)),
        "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=3))
    ]
    room_code = "-".join(parts)
    
    MEETINGS[room_code] = {
        "participants": {},
        "queues": {},
    }
    logger.info(f"Created meeting room: {room_code} (Tenant ID: {current_user.tenant_id})")
    return {"room_code": room_code}


@router.post("/join/{room_code}")
def join_room(room_code: str, payload: JoinRequest):
    """Enters a participant into a meeting room and returns other members."""
    if room_code not in MEETINGS:
        # Auto-create room for guest link joins
        MEETINGS[room_code] = {
            "participants": {},
            "queues": {},
        }

    room = MEETINGS[room_code]
    p_id = payload.participant_id
    p_name = payload.name

    # Add to room
    room["participants"][p_id] = p_name
    if p_id not in room["queues"]:
        room["queues"][p_id] = []

    # Find other active members
    others = [
        {"id": k, "name": v}
        for k, v in room["participants"].items()
        if k != p_id
    ]

    logger.info(f"User {p_name} ({p_id}) joined room {room_code}")
    return {"status": "success", "other_participants": others}


@router.post("/signal/{room_code}")
def send_signal(room_code: str, payload: SignalRequest):
    """Forwards SDP offers/answers and ICE candidates to a specific peer."""
    if room_code not in MEETINGS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting room not found."
        )

    room = MEETINGS[room_code]
    target = payload.target_id

    if target not in room["queues"]:
        # Target hasn't joined or initialized queue yet
        return {"status": "queued_fail", "reason": "Target not present"}

    # Append to target signal queue
    room["queues"][target].append({
        "sender_id": payload.sender_id,
        "type": payload.type,
        "data": payload.data
    })

    return {"status": "success"}


@router.get("/poll/{room_code}/{participant_id}")
def poll_room(room_code: str, participant_id: str):
    """Fetches any pending signaling payloads and active participant list."""
    if room_code not in MEETINGS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting room not found."
        )

    room = MEETINGS[room_code]
    
    # Keepalive/auto-register queue if needed
    if participant_id not in room["queues"]:
        room["queues"][participant_id] = []
    
    # Retrieve and clear signals
    signals = list(room["queues"][participant_id])
    room["queues"][participant_id].clear()

    # Get latest participant list
    participants = [
        {"id": k, "name": v}
        for k, v in room["participants"].items()
    ]

    return {
        "signals": signals,
        "participants": participants
    }


@router.post("/leave/{room_code}/{participant_id}")
def leave_room(room_code: str, participant_id: str):
    """Removes a participant and cleans up their message queue."""
    if room_code in MEETINGS:
        room = MEETINGS[room_code]
        if participant_id in room["participants"]:
            del room["participants"][participant_id]
        if participant_id in room["queues"]:
            del room["queues"][participant_id]
        
        # Clean up empty rooms
        if not room["participants"]:
            del MEETINGS[room_code]
            logger.info(f"Cleaned up empty room: {room_code}")
            
    return {"status": "success"}
