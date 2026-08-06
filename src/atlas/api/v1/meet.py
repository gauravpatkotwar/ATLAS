import logging
import random
import time
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from atlas.database.models import User
from atlas.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory store for meeting rooms
# room_code -> { "participants": { id: {"name": str, "last_seen": float} }, "queues": { id: [signals] } }
MEETINGS: Dict[str, Dict[str, Any]] = {}

class JoinRequest(BaseModel):
    participant_id: str
    name: str

class SignalRequest(BaseModel):
    sender_id: str
    target_id: str
    type: str
    data: Any


def _norm_code(code: str) -> str:
    return code.lower().strip()


def _clean_stale_participants(room: Dict[str, Any]):
    now = time.time()
    stale_ids = []
    for pid, pdata in list(room["participants"].items()):
        last_seen = pdata.get("last_seen", now) if isinstance(pdata, dict) else now
        if now - last_seen > 25:  # 25 seconds inactive
            stale_ids.append(pid)
    for pid in stale_ids:
        room["participants"].pop(pid, None)
        room["queues"].pop(pid, None)


@router.post("/create")
def create_room(current_user: User = Depends(get_current_user)):
    """Generates a random unique room code for a video meeting."""
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
    logger.info(f"Created meeting room: {room_code}")
    return {"room_code": room_code}


@router.post("/join/{room_code}")
def join_room(room_code: str, payload: JoinRequest):
    """Enters a participant into a meeting room and returns other members."""
    code = _norm_code(room_code)
    if code not in MEETINGS:
        MEETINGS[code] = {
            "participants": {},
            "queues": {},
        }

    room = MEETINGS[code]
    _clean_stale_participants(room)

    p_id = payload.participant_id
    p_name = payload.name

    # Add/Update participant with timestamp
    room["participants"][p_id] = {"name": p_name, "last_seen": time.time()}
    if p_id not in room["queues"]:
        room["queues"][p_id] = []

    # Find other active members
    others = [
        {"id": k, "name": v["name"] if isinstance(v, dict) else v}
        for k, v in room["participants"].items()
        if k != p_id
    ]

    logger.info(f"User {p_name} ({p_id}) joined room {code}. Active others: {len(others)}")
    return {"status": "success", "other_participants": others}


@router.post("/signal/{room_code}")
def send_signal(room_code: str, payload: SignalRequest):
    """Forwards SDP offers/answers and ICE candidates to a specific peer."""
    code = _norm_code(room_code)
    if code not in MEETINGS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting room not found."
        )

    room = MEETINGS[code]
    target = payload.target_id

    if target not in room["queues"]:
        room["queues"][target] = []

    # Append signal to target queue
    room["queues"][target].append({
        "sender_id": payload.sender_id,
        "type": payload.type,
        "data": payload.data
    })

    return {"status": "success"}


@router.get("/poll/{room_code}/{participant_id}")
def poll_room(room_code: str, participant_id: str):
    """Fetches any pending signaling payloads and active participant list."""
    code = _norm_code(room_code)
    if code not in MEETINGS:
        # Auto-create if lost
        MEETINGS[code] = {"participants": {}, "queues": {}}

    room = MEETINGS[code]
    _clean_stale_participants(room)

    # Keepalive update
    if participant_id in room["participants"]:
        if isinstance(room["participants"][participant_id], dict):
            room["participants"][participant_id]["last_seen"] = time.time()
        else:
            room["participants"][participant_id] = {"name": str(room["participants"][participant_id]), "last_seen": time.time()}
    
    if participant_id not in room["queues"]:
        room["queues"][participant_id] = []

    # Retrieve & clear queued signals
    signals = list(room["queues"][participant_id])
    room["queues"][participant_id].clear()

    # Get list of all active participants
    participants = [
        {"id": k, "name": v["name"] if isinstance(v, dict) else v}
        for k, v in room["participants"].items()
    ]

    return {
        "signals": signals,
        "participants": participants
    }


@router.post("/leave/{room_code}/{participant_id}")
def leave_room(room_code: str, participant_id: str):
    """Removes a participant and cleans up their message queue."""
    code = _norm_code(room_code)
    if code in MEETINGS:
        room = MEETINGS[code]
        room["participants"].pop(participant_id, None)
        room["queues"].pop(participant_id, None)
        
        if not room["participants"]:
            del MEETINGS[code]
            logger.info(f"Cleaned up empty room: {code}")
            
    return {"status": "success"}
