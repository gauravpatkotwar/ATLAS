import logging
from typing import List, Optional
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from atlas.database.session import get_db
from atlas.database.models import User, Post, Comment
from atlas.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Pydantic Schemas ---
class PostCreate(BaseModel):
    title: str
    content: str
    is_anonymous: bool = True
    post_type: str = "discussion"  # "discussion" or "whistleblower"

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    is_anonymous: bool
    post_type: str
    author_name: Optional[str]
    votes: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class VoteRequest(BaseModel):
    direction: str  # "up" or "down"

class CommentCreate(BaseModel):
    content: str
    is_anonymous: bool = True

class CommentResponse(BaseModel):
    id: int
    post_id: int
    content: str
    is_anonymous: bool
    author_name: Optional[str]
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# --- API Routes ---

@router.get("/posts", response_model=List[PostResponse])
async def list_posts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves all community posts within the user's tenant organization context."""
    stmt = select(Post).where(Post.tenant_id == current_user.tenant_id).order_by(Post.created_at.desc())
    result = await db.execute(stmt)
    posts = result.scalars().all()

    response = []
    for post in posts:
        # Mask author details if posted anonymously
        display_name = "Anonymous User" if post.is_anonymous else (post.author_name or "Anonymous User")
        response.append(PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            is_anonymous=post.is_anonymous,
            post_type=post.post_type or "discussion",
            author_name=display_name,
            votes=post.votes,
            created_at=post.created_at
        ))
    return response


@router.post("/posts", response_model=PostResponse)
async def create_post(
    payload: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new post (anonymously or showing identity)."""
    # Whistleblower posts MUST be anonymous
    is_anon = True if payload.post_type == "whistleblower" else payload.is_anonymous

    post = Post(
        tenant_id=current_user.tenant_id,
        title=payload.title,
        content=payload.content,
        author_id=current_user.id,
        author_name=current_user.email,
        is_anonymous=is_anon,
        post_type=payload.post_type,
        votes=0
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)

    display_name = "Anonymous User" if post.is_anonymous else (post.author_name or "Anonymous User")
    return PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        is_anonymous=post.is_anonymous,
        post_type=post.post_type,
        author_name=display_name,
        votes=post.votes,
        created_at=post.created_at
    )


@router.post("/posts/{post_id}/vote")
async def vote_post(
    post_id: int,
    payload: VoteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Performs an upvote or downvote calculation on a community post."""
    stmt = select(Post).where(Post.id == post_id, Post.tenant_id == current_user.tenant_id)
    result = await db.execute(stmt)
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found."
        )

    if payload.direction.lower() == "up":
        post.votes += 1
    elif payload.direction.lower() == "down":
        post.votes -= 1
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid voting direction. Must be 'up' or 'down'."
        )

    db.add(post)
    await db.commit()
    await db.refresh(post)
    return {"status": "success", "votes": post.votes}


@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
async def list_comments(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists all comments associated with a specific post."""
    # Verify post belongs to the tenant
    post_stmt = select(Post).where(Post.id == post_id, Post.tenant_id == current_user.tenant_id)
    post_res = await db.execute(post_stmt)
    if not post_res.scalars().first():
         raise HTTPException(status_code=404, detail="Post not found.")

    stmt = select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at.asc())
    result = await db.execute(stmt)
    comments = result.scalars().all()

    response = []
    for comment in comments:
        display_name = "Anonymous User" if comment.is_anonymous else (comment.author_name or "Anonymous User")
        response.append(CommentResponse(
            id=comment.id,
            post_id=comment.post_id,
            content=comment.content,
            is_anonymous=comment.is_anonymous,
            author_name=display_name,
            created_at=comment.created_at
        ))
    return response


@router.post("/posts/{post_id}/comments", response_model=CommentResponse)
async def create_comment(
    post_id: int,
    payload: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submits a new reply comment to a post (anonymously or with identity)."""
    # Verify post belongs to the tenant
    post_stmt = select(Post).where(Post.id == post_id, Post.tenant_id == current_user.tenant_id)
    post_res = await db.execute(post_stmt)
    if not post_res.scalars().first():
         raise HTTPException(status_code=404, detail="Post not found.")

    comment = Comment(
        post_id=post_id,
        content=payload.content,
        author_id=current_user.id,
        author_name=current_user.email,
        is_anonymous=payload.is_anonymous
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    display_name = "Anonymous User" if comment.is_anonymous else (comment.author_name or "Anonymous User")
    return CommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        content=comment.content,
        is_anonymous=comment.is_anonymous,
        author_name=display_name,
        created_at=comment.created_at
    )
