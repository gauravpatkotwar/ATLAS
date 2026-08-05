import json
import logging
import datetime
from typing import List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.database.session import get_db
from atlas.database.models import User
from atlas.database.tv_models import TvVideo, TvWatchHistory, TvBookmark
from atlas.api.deps import get_current_user, get_current_admin
from atlas.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()


# ──────────────────────────────────────────────────────────────
#  Pydantic Schemas
# ──────────────────────────────────────────────────────────────


class VideoOut(BaseModel):
    id: int
    title: str
    youtube_id: str
    thumbnail: Optional[str]
    description: Optional[str]
    channel: str
    tags: Optional[str]
    company: Optional[str]
    is_sponsored: bool
    is_live: bool
    viewer_count: int
    duration_sec: int

    model_config = {"from_attributes": True}


class WatchResponse(BaseModel):
    message: str
    xp_awarded: bool
    xp_total: int


class AISummaryResponse(BaseModel):
    summary: List[str]
    skills: List[str]
    jobs_keywords: List[str]


# ──────────────────────────────────────────────────────────────
#  Channel definitions
# ──────────────────────────────────────────────────────────────

CHANNELS = [
    {"id": "all",          "name": "All",           "icon": "📺"},
    {"id": "tech",         "name": "Tech",          "icon": "💻"},
    {"id": "ai",           "name": "AI",            "icon": "🤖"},
    {"id": "careers",      "name": "Careers",       "icon": "💼"},
    {"id": "cloud",        "name": "Cloud",         "icon": "☁️"},
    {"id": "devops",       "name": "DevOps",        "icon": "⚙️"},
    {"id": "startups",     "name": "Startups",      "icon": "🚀"},
    {"id": "data_science", "name": "Data Science",  "icon": "📊"},
    {"id": "cybersecurity","name": "Cybersecurity", "icon": "🔒"},
    {"id": "marketing",    "name": "Marketing",     "icon": "📣"},
    {"id": "design",       "name": "Design",        "icon": "🎨"},
    {"id": "finance",      "name": "Finance",       "icon": "💰"},
    {"id": "sponsored",    "name": "Sponsored",     "icon": "⭐"},
]


# ──────────────────────────────────────────────────────────────
#  Seed data
# ──────────────────────────────────────────────────────────────

SEED_VIDEOS = [
    # Tech
    {"title": "Docker in 100 Seconds", "youtube_id": "Gjnup-PuquQ", "company": "Fireship", "channel": "tech", "tags": "docker,containers,devops", "duration_sec": 102},
    {"title": "Kubernetes Explained in 100 Seconds", "youtube_id": "PziYflu8cB8", "company": "Fireship", "channel": "tech", "tags": "kubernetes,k8s,devops,containers", "duration_sec": 160},
    {"title": "Git in 100 Seconds", "youtube_id": "hwP7WQkmECE", "company": "Fireship", "channel": "tech", "tags": "git,version control,developer", "duration_sec": 102},
    {"title": "Linux in 100 Seconds", "youtube_id": "rrB13utjYV4", "company": "Fireship", "channel": "tech", "tags": "linux,terminal,developer", "duration_sec": 111},
    {"title": "TypeScript in 100 Seconds", "youtube_id": "zQnBQ4tB3ZA", "company": "Fireship", "channel": "tech", "tags": "typescript,javascript,developer", "duration_sec": 102},
    # AI
    {"title": "Intro to Large Language Models", "youtube_id": "zjkBMFhNj_g", "company": "Andrej Karpathy", "channel": "ai", "tags": "llm,ai,machine learning,gpt", "duration_sec": 3600},
    {"title": "How GPT Works in 5 Minutes", "youtube_id": "bSvTVREwSNw", "company": "ByteByteGo", "channel": "ai", "tags": "gpt,chatgpt,ai,llm", "duration_sec": 300},
    {"title": "Machine Learning for Beginners", "youtube_id": "ukzFI9rgwfU", "company": "Google", "channel": "ai", "tags": "machine learning,ai,python", "duration_sec": 1200},
    {"title": "TensorFlow in 100 Seconds", "youtube_id": "i8NETqtGHms", "company": "Fireship", "channel": "ai", "tags": "tensorflow,ai,deep learning", "duration_sec": 100},
    {"title": "Python for Data Science", "youtube_id": "_uQrJ0TkZlc", "company": "freeCodeCamp", "channel": "ai", "tags": "python,data science,pandas,numpy", "duration_sec": 7200},
    # Careers
    {"title": "How to Get a Job at Google", "youtube_id": "rhUFm9IIuxw", "company": "Google", "channel": "careers", "tags": "google,interview,career,job search", "duration_sec": 600},
    {"title": "Salary Negotiation Tips 2024", "youtube_id": "xaOTbNh8rs0", "company": "ATLAS", "channel": "careers", "tags": "salary,negotiation,career,job offer", "duration_sec": 480},
    {"title": "How to Write a Resume That Gets Interviews", "youtube_id": "Tt08KmFfIYQ", "company": "Jeff Su", "channel": "careers", "tags": "resume,cv,career,job search", "duration_sec": 720},
    {"title": "Top 10 Interview Questions Answered", "youtube_id": "HG68Ymazo18", "company": "Thomas Frank", "channel": "careers", "tags": "interview,career,job,tips", "duration_sec": 900},
    {"title": "LinkedIn Profile Tips 2024", "youtube_id": "BcfGWi8gBcM", "company": "Jeff Su", "channel": "careers", "tags": "linkedin,career,networking,profile", "duration_sec": 600},
    # Cloud
    {"title": "AWS Explained in 10 Minutes", "youtube_id": "a9__D53WsUs", "company": "AWS", "channel": "cloud", "tags": "aws,cloud,amazon,infrastructure", "duration_sec": 600},
    {"title": "Azure vs AWS vs GCP", "youtube_id": "M988_fsOSWo", "company": "Fireship", "channel": "cloud", "tags": "azure,aws,gcp,cloud", "duration_sec": 300},
    {"title": "What is Cloud Computing?", "youtube_id": "M988_fsOSWo", "company": "Microsoft", "channel": "cloud", "tags": "cloud,azure,microsoft", "duration_sec": 240},
    {"title": "Terraform in 100 Seconds", "youtube_id": "tomUWcQ0P3k", "company": "Fireship", "channel": "cloud", "tags": "terraform,infrastructure,devops,cloud", "duration_sec": 101},
    {"title": "AWS S3 Tutorial", "youtube_id": "tfU0JEZjcsg", "company": "Traversy Media", "channel": "cloud", "tags": "aws,s3,cloud,storage", "duration_sec": 1800},
    # DevOps
    {"title": "DevOps Explained", "youtube_id": "UbtB4sMaaNM", "company": "IBM", "channel": "devops", "tags": "devops,ci/cd,pipeline", "duration_sec": 480},
    {"title": "CI/CD Pipeline Tutorial", "youtube_id": "R8_veQiYBjI", "company": "TechWorld with Nana", "channel": "devops", "tags": "cicd,github actions,devops", "duration_sec": 3600},
    {"title": "GitHub Actions in 5 Minutes", "youtube_id": "R8_veQiYBjI", "company": "GitHub", "channel": "devops", "tags": "github,actions,ci/cd,automation", "duration_sec": 300},
    {"title": "What is DevOps?", "youtube_id": "UbtB4sMaaNM", "company": "Fireship", "channel": "devops", "tags": "devops,sre,platform engineering", "duration_sec": 180},
    {"title": "Docker Compose in 12 Minutes", "youtube_id": "Qw9zlE3t8Ko", "company": "TechWorld with Nana", "channel": "devops", "tags": "docker,compose,containers,devops", "duration_sec": 720},
    # Startups
    {"title": "How to Start a Startup", "youtube_id": "ZoqgAy3h4OM", "company": "Y Combinator", "channel": "startups", "tags": "startup,entrepreneurship,fundraising", "duration_sec": 3600},
    {"title": "YC Application Tips", "youtube_id": "hXP1lf6WKCY", "company": "Y Combinator", "channel": "startups", "tags": "ycombinator,startup,application", "duration_sec": 1800},
    {"title": "How Stripe Built a Billion Dollar Business", "youtube_id": "qk70XNuPP20", "company": "Stripe", "channel": "startups", "tags": "stripe,startup,payments,fintech", "duration_sec": 1200},
    {"title": "OpenAI Company Culture", "youtube_id": "L_Guz73e6fw", "company": "OpenAI", "channel": "startups", "tags": "openai,ai,culture,startup", "duration_sec": 900},
    {"title": "Elon Musk on Building Companies", "youtube_id": "MxAnMaE9fMk", "company": "Lex Fridman", "channel": "startups", "tags": "startup,elon musk,company building", "duration_sec": 3600},
    # Data Science
    {"title": "Data Science Roadmap 2024", "youtube_id": "ua-CiDNNj30", "company": "Ken Jee", "channel": "data_science", "tags": "data science,career,roadmap,python", "duration_sec": 1200},
    {"title": "SQL in 100 Seconds", "youtube_id": "zsjvFFKOm3c", "company": "Fireship", "channel": "data_science", "tags": "sql,database,data", "duration_sec": 101},
    {"title": "Pandas Tutorial for Beginners", "youtube_id": "vmEHCJofslg", "company": "freeCodeCamp", "channel": "data_science", "tags": "pandas,python,data science", "duration_sec": 3600},
    {"title": "What is Data Engineering?", "youtube_id": "qWru-b6m030", "company": "IBM", "channel": "data_science", "tags": "data engineering,etl,pipeline", "duration_sec": 360},
    {"title": "Tableau for Beginners", "youtube_id": "TPMlZxRRaBQ", "company": "Tableau", "channel": "data_science", "tags": "tableau,visualization,data analytics", "duration_sec": 3600},
    # Cybersecurity
    {"title": "Ethical Hacking in 12 Hours", "youtube_id": "3Kq1MIfTWCE", "company": "freeCodeCamp", "channel": "cybersecurity", "tags": "hacking,security,penetration testing", "duration_sec": 43200},
    {"title": "Cybersecurity Career Roadmap", "youtube_id": "DP6R9tWvuvI", "company": "NetworkChuck", "channel": "cybersecurity", "tags": "cybersecurity,career,certifications", "duration_sec": 1200},
    {"title": "What is Zero Trust Security?", "youtube_id": "YzA4mWHDDis", "company": "IBM", "channel": "cybersecurity", "tags": "zero trust,security,enterprise", "duration_sec": 360},
    {"title": "CompTIA Security+ Overview", "youtube_id": "9NE2ULQtPsQ", "company": "Professor Messer", "channel": "cybersecurity", "tags": "comptia,security+,certification", "duration_sec": 1800},
    {"title": "OWASP Top 10 Explained", "youtube_id": "KRyaAY9pMbg", "company": "Fireship", "channel": "cybersecurity", "tags": "owasp,web security,vulnerabilities", "duration_sec": 600},
    # Marketing
    {"title": "Digital Marketing Full Course", "youtube_id": "nU-IIXBWlS4", "company": "Simplilearn", "channel": "marketing", "tags": "digital marketing,seo,social media", "duration_sec": 7200},
    {"title": "SEO in 5 Minutes", "youtube_id": "-SbEf7Tofwc", "company": "Ahrefs", "channel": "marketing", "tags": "seo,marketing,google", "duration_sec": 300},
    {"title": "Facebook Ads Tutorial 2024", "youtube_id": "E_RbIJ_UrW8", "company": "Meta", "channel": "marketing", "tags": "facebook ads,meta,social media marketing", "duration_sec": 3600},
    {"title": "Content Marketing Strategy", "youtube_id": "lNdVNLFaHJo", "company": "HubSpot", "channel": "marketing", "tags": "content marketing,strategy,hubspot", "duration_sec": 1200},
    {"title": "Growth Hacking Strategies", "youtube_id": "skCOkKhU4vY", "company": "Neil Patel", "channel": "marketing", "tags": "growth hacking,startup,marketing", "duration_sec": 600},
    # Design
    {"title": "Figma Tutorial for Beginners", "youtube_id": "FTFaQWZBqQ8", "company": "Figma", "channel": "design", "tags": "figma,ui design,ux,design", "duration_sec": 3600},
    {"title": "UX Design Principles", "youtube_id": "k0D7Sjx2jKE", "company": "Google", "channel": "design", "tags": "ux,design,user experience,google", "duration_sec": 1200},
    {"title": "Tailwind CSS in 100 Seconds", "youtube_id": "mr15Xzb1Ook", "company": "Fireship", "channel": "design", "tags": "tailwind,css,design,frontend", "duration_sec": 100},
    {"title": "Design System Tutorial", "youtube_id": "dnFi7r4FsqY", "company": "Google", "channel": "design", "tags": "design system,figma,components", "duration_sec": 1800},
    {"title": "Typography for Developers", "youtube_id": "agbh1wbfJt8", "company": "Fireship", "channel": "design", "tags": "typography,design,css,frontend", "duration_sec": 600},
    # Finance
    {"title": "Personal Finance for Engineers", "youtube_id": "WEDIj9JBTC8", "company": "ATLAS", "channel": "finance", "tags": "personal finance,investing,savings", "duration_sec": 1800},
    {"title": "How to Read Financial Statements", "youtube_id": "ARXuFkIQQwU", "company": "Accounting Stuff", "channel": "finance", "tags": "finance,accounting,financial statements", "duration_sec": 1200},
    {"title": "Stock Market for Beginners", "youtube_id": "ZCFkWDdmXG8", "company": "Nerdwallet", "channel": "finance", "tags": "stocks,investing,finance", "duration_sec": 900},
    {"title": "Startup Fundraising 101", "youtube_id": "J5CY0NQUO0k", "company": "Y Combinator", "channel": "finance", "tags": "fundraising,venture capital,startup", "duration_sec": 1200},
    {"title": "Venture Capital Explained", "youtube_id": "bOstRpcP37U", "company": "Patrick Boyle", "channel": "finance", "tags": "venture capital,vc,investing,startup", "duration_sec": 1800},
    # Sponsored
    {"title": "Microsoft Azure Career Path", "youtube_id": "M988_fsOSWo", "company": "Microsoft", "channel": "sponsored", "tags": "azure,career,certification,microsoft", "is_sponsored": True, "duration_sec": 600},
    {"title": "AWS Certification Guide 2024", "youtube_id": "a9__D53WsUs", "company": "Amazon", "channel": "sponsored", "tags": "aws,certification,cloud,career", "is_sponsored": True, "duration_sec": 600},
    {"title": "Google Cloud for Developers", "youtube_id": "ukzFI9rgwfU", "company": "Google", "channel": "sponsored", "tags": "gcp,google cloud,developer,career", "is_sponsored": True, "duration_sec": 600},
]


# ──────────────────────────────────────────────────────────────
#  Seed helper (called from lifespan)
# ──────────────────────────────────────────────────────────────


async def seed_tv_videos(db: AsyncSession) -> None:
    """Insert seed videos if the tv_videos table is empty."""
    result = await db.execute(select(func.count(TvVideo.id)))
    count = result.scalar() or 0
    if count > 0:
        logger.info(f"Atlas TV: {count} videos already in DB, skipping seed.")
        return

    logger.info("Atlas TV: seeding video library...")
    for v in SEED_VIDEOS:
        video = TvVideo(
            title=v["title"],
            youtube_id=v["youtube_id"],
            thumbnail=f"https://img.youtube.com/vi/{v['youtube_id']}/hqdefault.jpg",
            channel=v["channel"],
            tags=v.get("tags"),
            company=v.get("company"),
            is_sponsored=v.get("is_sponsored", False),
            duration_sec=v.get("duration_sec", 0),
        )
        db.add(video)
    await db.commit()
    logger.info(f"Atlas TV: seeded {len(SEED_VIDEOS)} videos.")


# ──────────────────────────────────────────────────────────────
#  Gemini AI helper
# ──────────────────────────────────────────────────────────────


async def _gemini_tv_summary(title: str, description: str, tags: str) -> dict:
    """Call Gemini to generate a structured TV video summary."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return {
            "summary": [f"Watch '{title}' to learn key concepts.", "Practical examples included.", "Great for all skill levels."],
            "skills": tags.split(",")[:3] if tags else [],
            "jobs_keywords": [],
        }

    prompt = (
        "You are a career learning assistant for Atlas TV.\n"
        f"Video title: {title}\n"
        f"Description: {description or 'N/A'}\n"
        f"Tags: {tags or 'N/A'}\n\n"
        "Return ONLY valid JSON with exactly these keys:\n"
        "- summary: list of exactly 3 concise bullet-point strings summarising the video\n"
        "- skills: list of 3-5 skill strings learnable from this video\n"
        "- jobs_keywords: list of 3-5 job role keywords relevant to this video\n"
        "No markdown fences, no extra text."
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                # Strip markdown fences if present
                if "```json" in raw:
                    raw = raw.split("```json")[1].split("```")[0].strip()
                elif "```" in raw:
                    raw = raw.split("```")[1].split("```")[0].strip()
                return json.loads(raw)
    except Exception as e:
        logger.warning(f"Atlas TV Gemini summary failed: {e}")

    # Fallback
    tag_list = [t.strip() for t in (tags or "").split(",") if t.strip()]
    return {
        "summary": [f"'{title}' covers core concepts.", "Includes practical examples.", "Suitable for learners at all levels."],
        "skills": tag_list[:5],
        "jobs_keywords": tag_list[:3],
    }


# ──────────────────────────────────────────────────────────────
#  XP helper
# ──────────────────────────────────────────────────────────────

TV_XP_PER_VIDEO = 5


async def _get_tv_xp(user_id: int, db: AsyncSession) -> int:
    """Return total TV XP earned by the user (5 per awarded watch)."""
    result = await db.execute(
        select(func.count(TvWatchHistory.id)).where(
            TvWatchHistory.user_id == user_id,
            TvWatchHistory.xp_awarded == True,  # noqa: E712
        )
    )
    awarded = result.scalar() or 0
    return awarded * TV_XP_PER_VIDEO


# ──────────────────────────────────────────────────────────────
#  Routes
# ──────────────────────────────────────────────────────────────


@router.get("/channels")
async def get_channels():
    """Return all available TV channels with icons."""
    return {"channels": CHANNELS}


@router.get("/feed")
async def get_feed(
    channel: str = Query(default="all"),
    page: int = Query(default=1, ge=1),
    db: AsyncSession = Depends(get_db),
):
    """Return paginated videos filtered by channel (20 per page)."""
    page_size = 20
    offset = (page - 1) * page_size
    q = select(TvVideo)
    count_q = select(func.count(TvVideo.id))
    if channel != "all":
        q = q.where(TvVideo.channel == channel)
        count_q = count_q.where(TvVideo.channel == channel)
    q = q.order_by(TvVideo.id.desc()).offset(offset).limit(page_size)
    result = await db.execute(q)
    total_result = await db.execute(count_q)
    total = total_result.scalar() or 0
    videos = result.scalars().all()
    return {
        "videos": [VideoOut.model_validate(v) for v in videos],
        "total": total,
        "page": page,
        "pages": max(1, (total + page_size - 1) // page_size),
    }


@router.get("/live", response_model=List[VideoOut])
async def get_live_videos(db: AsyncSession = Depends(get_db)):
    """Return all videos currently marked as live."""
    result = await db.execute(
        select(TvVideo).where(TvVideo.is_live == True)  # noqa: E712
    )
    return result.scalars().all()


@router.get("/search", response_model=List[VideoOut])
async def search_videos(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    """Full-text search across video title and tags."""
    term = f"%{q.lower()}%"
    result = await db.execute(
        select(TvVideo).where(
            or_(
                func.lower(TvVideo.title).like(term),
                func.lower(TvVideo.tags).like(term),
            )
        ).limit(50)
    )
    return result.scalars().all()


@router.get("/videos/{video_id}", response_model=VideoOut)
async def get_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Return a single video by ID."""
    result = await db.execute(select(TvVideo).where(TvVideo.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found.")
    return video


@router.post("/videos/{video_id}/watch", response_model=WatchResponse)
async def log_watch(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Log a watch event for the current user.
    Awards +5 XP the first time the user watches any video today.
    """
    # Verify video exists
    result = await db.execute(select(TvVideo).where(TvVideo.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found.")

    # Check if XP already awarded today for this user
    today_start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    existing_xp = await db.execute(
        select(TvWatchHistory).where(
            TvWatchHistory.user_id == current_user.id,
            TvWatchHistory.xp_awarded == True,  # noqa: E712
            TvWatchHistory.watched_at >= today_start,
        )
    )
    already_awarded_today = existing_xp.scalar_one_or_none() is not None

    xp_now = not already_awarded_today

    entry = TvWatchHistory(
        user_id=current_user.id,
        video_id=video_id,
        xp_awarded=xp_now,
    )
    db.add(entry)
    await db.commit()

    total_xp = await _get_tv_xp(current_user.id, db)

    return WatchResponse(
        message="Watch logged." + (" +5 XP awarded!" if xp_now else ""),
        xp_awarded=xp_now,
        xp_total=total_xp,
    )


@router.get("/bookmarks", response_model=List[VideoOut])
async def get_bookmarks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all bookmarked videos for the authenticated user."""
    result = await db.execute(
        select(TvVideo)
        .join(TvBookmark, TvBookmark.video_id == TvVideo.id)
        .where(TvBookmark.user_id == current_user.id)
        .order_by(TvBookmark.created_at.desc())
    )
    return result.scalars().all()


@router.post("/bookmarks/{video_id}", status_code=status.HTTP_201_CREATED)
async def add_bookmark(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a video to the authenticated user's bookmarks."""
    # Verify video exists
    video = await db.execute(select(TvVideo).where(TvVideo.id == video_id))
    if not video.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found.")

    # Idempotent — don't duplicate
    existing = await db.execute(
        select(TvBookmark).where(
            TvBookmark.user_id == current_user.id,
            TvBookmark.video_id == video_id,
        )
    )
    if existing.scalar_one_or_none():
        return {"message": "Already bookmarked."}

    db.add(TvBookmark(user_id=current_user.id, video_id=video_id))
    await db.commit()
    return {"message": "Bookmarked."}


@router.delete("/bookmarks/{video_id}", status_code=status.HTTP_200_OK)
async def remove_bookmark(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a video from the authenticated user's bookmarks."""
    result = await db.execute(
        select(TvBookmark).where(
            TvBookmark.user_id == current_user.id,
            TvBookmark.video_id == video_id,
        )
    )
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found.")

    await db.delete(bookmark)
    await db.commit()
    return {"message": "Bookmark removed."}


@router.post("/ai/summary/{video_id}", response_model=AISummaryResponse)
async def ai_video_summary(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate an AI-powered summary (3 bullets, skills, job keywords) for a video using Gemini."""
    result = await db.execute(select(TvVideo).where(TvVideo.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found.")

    data = await _gemini_tv_summary(
        title=video.title,
        description=video.description or "",
        tags=video.tags or "",
    )
    return AISummaryResponse(
        summary=data.get("summary", []),
        skills=data.get("skills", []),
        jobs_keywords=data.get("jobs_keywords", []),
    )


@router.get("/seed")
async def seed_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Admin endpoint: seed the TV video library if the table is empty."""
    await seed_tv_videos(db)
    result = await db.execute(select(func.count(TvVideo.id)))
    total = result.scalar() or 0
    return {"message": f"Seed complete. Total videos in DB: {total}"}
