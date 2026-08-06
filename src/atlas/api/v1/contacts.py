"""
Atlas Contact Diary + Messaging + Video Calling API
- Unique ATL-XXXXX numbers for every user
- Contact book (add/remove by Atlas number)  
- Direct 1:1 messaging with read receipts
- WebRTC video call signaling (offer/answer/ICE exchange)
"""
import logging
import random
import string
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from atlas.database.session import get_db
from atlas.api.deps import get_current_user
from atlas.database.models import User

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _generate_atlas_no() -> str:
    digits = ''.join(random.choices(string.digits, k=5))
    return f"ATL-{digits}"


async def _ensure_atlas_no(user: User, db: AsyncSession) -> str:
    result = await db.execute(
        text("SELECT atlas_no FROM users WHERE id = :uid"), {"uid": user.id}
    )
    row = result.fetchone()
    if row and row.atlas_no:
        return row.atlas_no
    for _ in range(20):
        candidate = _generate_atlas_no()
        check = await db.execute(
            text("SELECT id FROM users WHERE atlas_no = :no"), {"no": candidate}
        )
        if not check.fetchone():
            await db.execute(
                text("UPDATE users SET atlas_no = :no WHERE id = :uid"),
                {"no": candidate, "uid": user.id}
            )
            await db.commit()
            return candidate
    raise HTTPException(status_code=500, detail="Could not generate Atlas number")


async def _get_user_by_atlas_no(atlas_no: str, db: AsyncSession):
    result = await db.execute(
        text("SELECT id, email, role, atlas_no FROM users WHERE atlas_no = :no"),
        {"no": atlas_no.upper().strip()}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"No user found with Atlas number {atlas_no}")
    return row


# ---------------------------------------------------------------------------
# SCHEMAS
# ---------------------------------------------------------------------------

class AddContactRequest(BaseModel):
    atlas_no: str
    nickname: Optional[str] = None

class SendMessageRequest(BaseModel):
    atlas_no: str
    content: str

class SignalRequest(BaseModel):
    signal_type: str   # "offer" | "answer" | "ice"
    data: str          # JSON stringified SDP / ICE candidate


# ---------------------------------------------------------------------------
# CONTACT ROUTES
# ---------------------------------------------------------------------------

@router.get("/me")
async def get_my_atlas_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    atlas_no = await _ensure_atlas_no(current_user, db)
    saved_by = await db.execute(
        text("SELECT COUNT(*) FROM atlas_contact_book WHERE contact_user_id = :uid"),
        {"uid": current_user.id}
    )
    unread = await db.execute(
        text("SELECT COUNT(*) FROM atlas_messages WHERE receiver_user_id = :uid AND read_at IS NULL"),
        {"uid": current_user.id}
    )
    # Check for incoming call
    incoming_call = await db.execute(text("""
        SELECT ci.id, ci.room_id, u.atlas_no as caller_atlas_no, u.email as caller_email
        FROM atlas_call_invitations ci
        JOIN users u ON u.id = ci.caller_user_id
        WHERE ci.receiver_user_id = :uid AND ci.status = 'pending'
        ORDER BY ci.created_at DESC LIMIT 1
    """), {"uid": current_user.id})
    call_row = incoming_call.fetchone()

    return {
        "atlas_no": atlas_no,
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "saved_by_count": saved_by.scalar() or 0,
        "unread_messages": unread.scalar() or 0,
        "incoming_call": {
            "call_id": call_row.id,
            "room_id": call_row.room_id,
            "from_atlas_no": call_row.caller_atlas_no,
            "from_name": call_row.caller_email.split('@')[0],
        } if call_row else None,
    }


@router.get("/lookup/{atlas_no}")
async def lookup_by_atlas_no(
    atlas_no: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await _get_user_by_atlas_no(atlas_no, db)
    if row.id == current_user.id:
        raise HTTPException(status_code=400, detail="That's your own Atlas number!")
    existing = await db.execute(
        text("SELECT id FROM atlas_contact_book WHERE owner_user_id=:oid AND contact_user_id=:cid"),
        {"oid": current_user.id, "cid": row.id}
    )
    mutual = await db.execute(
        text("SELECT id FROM atlas_contact_book WHERE owner_user_id=:cid AND contact_user_id=:oid"),
        {"cid": row.id, "oid": current_user.id}
    )
    return {
        "user_id": row.id,
        "email": row.email,
        "display_name": row.email.split('@')[0],
        "role": row.role,
        "atlas_no": row.atlas_no,
        "already_saved": existing.fetchone() is not None,
        "is_mutual": mutual.fetchone() is not None,
    }


@router.post("/add")
async def add_contact(
    body: AddContactRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await _get_user_by_atlas_no(body.atlas_no, db)
    if row.id == current_user.id:
        raise HTTPException(status_code=400, detail="You can't add yourself!")
    existing = await db.execute(
        text("SELECT id FROM atlas_contact_book WHERE owner_user_id=:oid AND contact_user_id=:cid"),
        {"oid": current_user.id, "cid": row.id}
    )
    if existing.fetchone():
        raise HTTPException(status_code=409, detail="Contact already in your diary")
    await db.execute(
        text("INSERT INTO atlas_contact_book (owner_user_id, contact_user_id, nickname, created_at) VALUES (:oid, :cid, :nick, NOW())"),
        {"oid": current_user.id, "cid": row.id, "nick": body.nickname}
    )
    await db.commit()
    return {
        "message": f"Added {body.atlas_no.upper()} to your Contact Diary!",
        "contact": {"user_id": row.id, "email": row.email, "role": row.role, "atlas_no": row.atlas_no, "nickname": body.nickname}
    }


@router.get("/book")
async def get_contact_book(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        SELECT
            cb.id as entry_id, cb.nickname, cb.created_at,
            u.id as user_id, u.email, u.role, u.atlas_no,
            EXISTS(SELECT 1 FROM atlas_contact_book cb2 WHERE cb2.owner_user_id=u.id AND cb2.contact_user_id=:my_id) as is_mutual,
            (SELECT COUNT(*) FROM atlas_messages m WHERE m.sender_user_id=u.id AND m.receiver_user_id=:my_id AND m.read_at IS NULL) as unread_count,
            (SELECT m2.content FROM atlas_messages m2
             WHERE (m2.sender_user_id=u.id AND m2.receiver_user_id=:my_id)
                OR (m2.sender_user_id=:my_id AND m2.receiver_user_id=u.id)
             ORDER BY m2.created_at DESC LIMIT 1) as last_message
        FROM atlas_contact_book cb
        JOIN users u ON u.id=cb.contact_user_id
        WHERE cb.owner_user_id=:my_id
        ORDER BY cb.created_at DESC
    """), {"my_id": current_user.id})
    rows = result.fetchall()
    contacts = []
    for r in rows:
        contacts.append({
            "entry_id": r.entry_id,
            "nickname": r.nickname,
            "saved_at": str(r.created_at),
            "user_id": r.user_id,
            "email": r.email,
            "display_name": r.nickname or r.email.split('@')[0],
            "role": r.role,
            "atlas_no": r.atlas_no,
            "is_mutual": bool(r.is_mutual),
            "unread_count": int(r.unread_count or 0),
            "last_message": r.last_message,
        })
    return {"contacts": contacts, "total": len(contacts)}


@router.get("/saved-me")
async def who_saved_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        SELECT cb.created_at, u.id as user_id, u.email, u.role, u.atlas_no,
            EXISTS(SELECT 1 FROM atlas_contact_book cb2 WHERE cb2.owner_user_id=:my_id AND cb2.contact_user_id=u.id) as i_saved_them
        FROM atlas_contact_book cb
        JOIN users u ON u.id=cb.owner_user_id
        WHERE cb.contact_user_id=:my_id ORDER BY cb.created_at DESC
    """), {"my_id": current_user.id})
    rows = result.fetchall()
    return {"saved_by": [{"user_id": r.user_id, "email": r.email, "display_name": r.email.split('@')[0], "role": r.role, "atlas_no": r.atlas_no, "saved_at": str(r.created_at), "i_saved_them": bool(r.i_saved_them)} for r in rows], "total": len(rows)}


@router.delete("/remove/{entry_id}")
async def remove_contact(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("DELETE FROM atlas_contact_book WHERE id=:eid AND owner_user_id=:uid RETURNING id"),
        {"eid": entry_id, "uid": current_user.id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Contact not found")
    await db.commit()
    return {"message": "Contact removed from diary"}


# ---------------------------------------------------------------------------
# MESSAGING ROUTES
# ---------------------------------------------------------------------------

@router.post("/message/send")
async def send_message(
    body: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not body.content.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if len(body.content) > 2000:
        raise HTTPException(status_code=400, detail="Message too long (max 2000 chars)")
    recipient = await _get_user_by_atlas_no(body.atlas_no, db)
    if recipient.id == current_user.id:
        raise HTTPException(status_code=400, detail="You can't message yourself!")
    result = await db.execute(text("""
        INSERT INTO atlas_messages (sender_user_id, receiver_user_id, content, created_at)
        VALUES (:sid, :rid, :content, NOW()) RETURNING id, created_at
    """), {"sid": current_user.id, "rid": recipient.id, "content": body.content.strip()})
    row = result.fetchone()
    await db.commit()
    my_atlas_no = await _ensure_atlas_no(current_user, db)
    return {
        "message_id": row.id,
        "sent_at": str(row.created_at),
        "from_atlas_no": my_atlas_no,
        "to_atlas_no": body.atlas_no.upper(),
        "content": body.content.strip(),
    }


@router.get("/message/conversation/{atlas_no}")
async def get_conversation(
    atlas_no: str,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    other = await _get_user_by_atlas_no(atlas_no, db)
    await db.execute(text("""
        UPDATE atlas_messages SET read_at=NOW()
        WHERE sender_user_id=:oid AND receiver_user_id=:my_id AND read_at IS NULL
    """), {"oid": other.id, "my_id": current_user.id})
    await db.commit()
    result = await db.execute(text("""
        SELECT m.id, m.sender_user_id, m.content, m.created_at, m.read_at,
               u.atlas_no as sender_atlas_no, u.email as sender_email
        FROM atlas_messages m
        JOIN users u ON u.id=m.sender_user_id
        WHERE (m.sender_user_id=:my_id AND m.receiver_user_id=:oid)
           OR (m.sender_user_id=:oid AND m.receiver_user_id=:my_id)
        ORDER BY m.created_at ASC LIMIT :limit OFFSET :offset
    """), {"my_id": current_user.id, "oid": other.id, "limit": limit, "offset": offset})
    rows = result.fetchall()
    my_atlas = await _ensure_atlas_no(current_user, db)
    messages = [{"id": r.id, "is_mine": r.sender_user_id == current_user.id, "sender_atlas_no": r.sender_atlas_no, "sender_name": r.sender_email.split('@')[0], "content": r.content, "sent_at": str(r.created_at), "read": r.read_at is not None} for r in rows]
    return {
        "messages": messages, "total": len(messages),
        "with_user": {"atlas_no": other.atlas_no, "email": other.email, "display_name": other.email.split('@')[0], "role": other.role},
        "my_atlas_no": my_atlas,
    }


@router.get("/message/inbox")
async def get_inbox(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        WITH conversations AS (
            SELECT CASE WHEN sender_user_id=:my_id THEN receiver_user_id ELSE sender_user_id END as other_user_id,
                MAX(created_at) as last_at
            FROM atlas_messages WHERE sender_user_id=:my_id OR receiver_user_id=:my_id
            GROUP BY other_user_id
        )
        SELECT c.other_user_id, c.last_at, u.email, u.role, u.atlas_no,
            (SELECT m.content FROM atlas_messages m
             WHERE (m.sender_user_id=:my_id AND m.receiver_user_id=c.other_user_id)
                OR (m.sender_user_id=c.other_user_id AND m.receiver_user_id=:my_id)
             ORDER BY m.created_at DESC LIMIT 1) as last_message,
            (SELECT COUNT(*) FROM atlas_messages m WHERE m.sender_user_id=c.other_user_id AND m.receiver_user_id=:my_id AND m.read_at IS NULL) as unread_count
        FROM conversations c JOIN users u ON u.id=c.other_user_id ORDER BY c.last_at DESC
    """), {"my_id": current_user.id})
    rows = result.fetchall()
    conversations = [{"user_id": r.other_user_id, "email": r.email, "display_name": r.email.split('@')[0], "role": r.role, "atlas_no": r.atlas_no, "last_message": r.last_message, "last_at": str(r.last_at), "unread_count": int(r.unread_count or 0)} for r in rows]
    return {"conversations": conversations, "total_unread": sum(c["unread_count"] for c in conversations)}


# ---------------------------------------------------------------------------
# VIDEO CALL ROUTES (WebRTC Signaling)
# ---------------------------------------------------------------------------

@router.post("/calls/invite/{atlas_no}")
async def invite_video_call(
    atlas_no: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Initiate a video call to an Atlas number."""
    recipient = await _get_user_by_atlas_no(atlas_no, db)
    if recipient.id == current_user.id:
        raise HTTPException(status_code=400, detail="Can't call yourself!")

    # Cancel any existing pending call to this person
    await db.execute(text("""
        UPDATE atlas_call_invitations SET status='ended'
        WHERE caller_user_id=:cid AND receiver_user_id=:rid AND status='pending'
    """), {"cid": current_user.id, "rid": recipient.id})

    room_id = f"ATLAS-CALL-{uuid.uuid4().hex[:10].upper()}"
    result = await db.execute(text("""
        INSERT INTO atlas_call_invitations (caller_user_id, receiver_user_id, room_id, status, created_at)
        VALUES (:cid, :rid, :room_id, 'pending', NOW()) RETURNING id
    """), {"cid": current_user.id, "rid": recipient.id, "room_id": room_id})
    call_id = result.fetchone().id
    await db.commit()

    return {
        "call_id": call_id,
        "room_id": room_id,
        "calling_atlas_no": atlas_no.upper(),
        "calling_name": recipient.email.split('@')[0],
        "status": "pending",
    }


@router.get("/calls/incoming")
async def check_incoming_calls(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Poll for incoming calls."""
    result = await db.execute(text("""
        SELECT ci.id, ci.room_id, u.atlas_no as caller_atlas_no, u.email as caller_email, ci.created_at
        FROM atlas_call_invitations ci
        JOIN users u ON u.id=ci.caller_user_id
        WHERE ci.receiver_user_id=:uid AND ci.status='pending'
        ORDER BY ci.created_at DESC LIMIT 1
    """), {"uid": current_user.id})
    row = result.fetchone()
    if not row:
        return {"incoming_call": None}
    return {"incoming_call": {
        "call_id": row.id,
        "room_id": row.room_id,
        "from_atlas_no": row.caller_atlas_no,
        "from_name": row.caller_email.split('@')[0],
        "started_at": str(row.created_at),
    }}


@router.post("/calls/{call_id}/accept")
async def accept_call(
    call_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE atlas_call_invitations SET status='active'
        WHERE id=:cid AND receiver_user_id=:uid AND status='pending' RETURNING room_id
    """), {"cid": call_id, "uid": current_user.id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Call not found or already ended")
    await db.commit()
    return {"status": "active", "room_id": row.room_id}


@router.post("/calls/{call_id}/decline")
async def decline_call(
    call_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(text("""
        UPDATE atlas_call_invitations SET status='declined'
        WHERE id=:cid AND (receiver_user_id=:uid OR caller_user_id=:uid)
    """), {"cid": call_id, "uid": current_user.id})
    await db.commit()
    return {"status": "declined"}


@router.post("/calls/{call_id}/end")
async def end_call(
    call_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(text("""
        UPDATE atlas_call_invitations SET status='ended'
        WHERE id=:cid AND (receiver_user_id=:uid OR caller_user_id=:uid)
    """), {"cid": call_id, "uid": current_user.id})
    await db.commit()
    return {"status": "ended"}


@router.post("/calls/{call_id}/signal")
async def send_signal(
    call_id: int,
    body: SignalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Exchange WebRTC SDP/ICE signals."""
    await db.execute(text("""
        INSERT INTO atlas_call_signals (call_id, from_user_id, signal_type, data, created_at)
        VALUES (:call_id, :uid, :stype, :data, NOW())
    """), {"call_id": call_id, "uid": current_user.id, "stype": body.signal_type, "data": body.data})
    await db.commit()
    return {"sent": True}


@router.get("/calls/{call_id}/signals")
async def get_signals(
    call_id: int,
    after_id: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get WebRTC signals from the other peer."""
    result = await db.execute(text("""
        SELECT cs.id, cs.signal_type, cs.data, cs.created_at
        FROM atlas_call_signals cs
        WHERE cs.call_id=:cid AND cs.from_user_id != :uid AND cs.id > :after_id
        ORDER BY cs.id ASC
    """), {"cid": call_id, "uid": current_user.id, "after_id": after_id})
    rows = result.fetchall()

    # Also check call status
    status_res = await db.execute(
        text("SELECT status FROM atlas_call_invitations WHERE id=:cid"), {"cid": call_id}
    )
    call_status = status_res.fetchone()

    return {
        "signals": [{"id": r.id, "type": r.signal_type, "data": r.data} for r in rows],
        "call_status": call_status.status if call_status else "ended",
    }
