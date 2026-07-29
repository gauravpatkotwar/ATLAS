"""
Atlas Academy API — Learning Management System
Endpoints: courses, modules, lessons, enrollments, certificates,
           reviews, projects, skill-gap analysis, instructor portal,
           AI mentor / roadmap generator.
"""
from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from atlas.api.deps import get_current_user, get_db
from atlas.database.models import (
    AcademyCourse, AcademyModule, AcademyLesson, AcademyEnrollment,
    AcademyInstructor, AcademyCertificate, AcademyReview, AcademyProject,
    AcademySkillGap, AcademyLearningPath, User, Candidate
)
from atlas.ai.factory import AIProviderFactory
from atlas.config.settings import settings

router = APIRouter()


# ─── Pydantic Schemas ─────────────────────────────────────────────────────────

class InstructorApplyIn(BaseModel):
    display_name: str
    bio: Optional[str] = None
    expertise: List[str] = []

class CourseCreateIn(BaseModel):
    title: str
    description: str
    short_description: Optional[str] = None
    category: str
    level: str = "beginner"
    tags: List[str] = []
    skills_taught: List[str] = []
    price: float = 0.0
    is_free: bool = True

class ModuleCreateIn(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int = 0

class LessonCreateIn(BaseModel):
    title: str
    content: Optional[str] = None
    video_url: Optional[str] = None
    duration_mins: int = 10
    order_index: int = 0
    is_preview: bool = False
    quiz_data: Optional[Dict] = None

class ReviewCreateIn(BaseModel):
    rating: int
    body: Optional[str] = None

class ProjectSubmitIn(BaseModel):
    title: str
    description: Optional[str] = None
    submission_url: Optional[str] = None
    github_url: Optional[str] = None

class ProgressUpdateIn(BaseModel):
    lesson_id: int

class SkillGapIn(BaseModel):
    job_title: str
    job_skills: List[str]
    candidate_skills: Optional[List[str]] = None  # if None, fetch from profile

class RoadmapIn(BaseModel):
    goal: str


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _course_dict(c: AcademyCourse, enrolled: bool = False, progress: float = 0.0) -> Dict:
    return {
        "id": c.id,
        "title": c.title,
        "description": c.description,
        "short_description": c.short_description,
        "category": c.category,
        "level": c.level,
        "tags": c.tags,
        "skills_taught": c.skills_taught,
        "thumbnail_url": c.thumbnail_url,
        "price": c.price,
        "is_free": c.is_free,
        "is_published": c.is_published,
        "duration_hours": c.duration_hours,
        "total_lessons": c.total_lessons,
        "total_enrolled": c.total_enrolled,
        "avg_rating": c.avg_rating,
        "created_at": c.created_at.isoformat(),
        "instructor": {
            "id": c.instructor.id,
            "display_name": c.instructor.display_name,
            "verified": c.instructor.verified,
            "total_students": c.instructor.total_students,
        } if c.instructor else None,
        "enrolled": enrolled,
        "progress_pct": progress,
    }


# ─── Course Endpoints ──────────────────────────────────────────────────────────

@router.get("/courses")
async def list_courses(
    category: Optional[str] = None,
    level: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all published courses with optional filters."""
    stmt = (
        select(AcademyCourse)
        .options(selectinload(AcademyCourse.instructor))
        .where(AcademyCourse.is_published == True)
    )
    if category:
        stmt = stmt.where(AcademyCourse.category == category)
    if level:
        stmt = stmt.where(AcademyCourse.level == level)
    result = await db.execute(stmt)
    courses = result.scalars().all()

    # Get enrollments for current user
    enroll_stmt = select(AcademyEnrollment).where(AcademyEnrollment.user_id == current_user.id)
    enroll_result = await db.execute(enroll_stmt)
    enrollments = {e.course_id: e for e in enroll_result.scalars().all()}

    out = []
    for c in courses:
        if search and search.lower() not in c.title.lower() and search.lower() not in c.description.lower():
            continue
        e = enrollments.get(c.id)
        out.append(_course_dict(c, enrolled=bool(e), progress=e.progress_pct if e else 0.0))
    return out


@router.post("/courses")
async def create_course(
    data: CourseCreateIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new course (instructor only)."""
    instr_result = await db.execute(
        select(AcademyInstructor).where(AcademyInstructor.user_id == current_user.id)
    )
    instructor = instr_result.scalar_one_or_none()
    if not instructor:
        raise HTTPException(status_code=403, detail="You must be a verified instructor to create courses.")

    course = AcademyCourse(
        instructor_id=instructor.id,
        **data.model_dump(),
        is_published=False,
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return {"id": course.id, "title": course.title, "message": "Course created. Add modules and lessons, then publish."}


@router.get("/courses/{course_id}")
async def get_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get course detail with modules and lessons."""
    result = await db.execute(
        select(AcademyCourse)
        .options(
            selectinload(AcademyCourse.instructor),
            selectinload(AcademyCourse.modules).selectinload(AcademyModule.lessons),
            selectinload(AcademyCourse.reviews),
        )
        .where(AcademyCourse.id == course_id)
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    enroll_result = await db.execute(
        select(AcademyEnrollment).where(
            and_(AcademyEnrollment.user_id == current_user.id,
                 AcademyEnrollment.course_id == course_id)
        )
    )
    enrollment = enroll_result.scalar_one_or_none()

    d = _course_dict(course, enrolled=bool(enrollment), progress=enrollment.progress_pct if enrollment else 0.0)
    d["modules"] = [
        {
            "id": m.id,
            "title": m.title,
            "description": m.description,
            "order_index": m.order_index,
            "lessons": [
                {
                    "id": l.id,
                    "title": l.title,
                    "content": l.content if enrollment or l.is_preview else None,
                    "video_url": l.video_url if enrollment or l.is_preview else None,
                    "duration_mins": l.duration_mins,
                    "order_index": l.order_index,
                    "is_preview": l.is_preview,
                    "has_quiz": bool(l.quiz_data),
                    "completed": l.id in (enrollment.completed_lesson_ids if enrollment else []),
                }
                for l in m.lessons
            ],
        }
        for m in course.modules
    ]
    d["reviews"] = [
        {"rating": r.rating, "body": r.body, "created_at": r.created_at.isoformat()}
        for r in course.reviews[-5:]
    ]
    return d


@router.put("/courses/{course_id}/publish")
async def publish_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Publish a course (instructor only)."""
    instr_result = await db.execute(
        select(AcademyInstructor).where(AcademyInstructor.user_id == current_user.id)
    )
    instructor = instr_result.scalar_one_or_none()
    if not instructor:
        raise HTTPException(status_code=403, detail="Not an instructor")

    result = await db.execute(
        select(AcademyCourse).where(
            and_(AcademyCourse.id == course_id, AcademyCourse.instructor_id == instructor.id)
        )
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Count total lessons
    lesson_count_result = await db.execute(
        select(func.count(AcademyLesson.id))
        .join(AcademyModule, AcademyLesson.module_id == AcademyModule.id)
        .where(AcademyModule.course_id == course_id)
    )
    lesson_count = lesson_count_result.scalar() or 0
    course.total_lessons = lesson_count
    course.is_published = True
    await db.commit()
    return {"message": "Course published!", "total_lessons": lesson_count}


# ─── Module & Lesson Endpoints ─────────────────────────────────────────────────

@router.post("/courses/{course_id}/modules")
async def add_module(
    course_id: int,
    data: ModuleCreateIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    module = AcademyModule(course_id=course_id, **data.model_dump())
    db.add(module)
    await db.commit()
    await db.refresh(module)
    return {"id": module.id, "title": module.title}


@router.post("/modules/{module_id}/lessons")
async def add_lesson(
    module_id: int,
    data: LessonCreateIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lesson = AcademyLesson(module_id=module_id, **data.model_dump())
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    return {"id": lesson.id, "title": lesson.title}


# ─── Enrollment Endpoints ──────────────────────────────────────────────────────

@router.post("/enroll/{course_id}")
async def enroll(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Enroll the current user in a course."""
    # Check already enrolled
    existing = await db.execute(
        select(AcademyEnrollment).where(
            and_(AcademyEnrollment.user_id == current_user.id,
                 AcademyEnrollment.course_id == course_id)
        )
    )
    if existing.scalar_one_or_none():
        return {"message": "Already enrolled"}

    enrollment = AcademyEnrollment(user_id=current_user.id, course_id=course_id)
    db.add(enrollment)

    # Increment course counter
    course_result = await db.execute(select(AcademyCourse).where(AcademyCourse.id == course_id))
    course = course_result.scalar_one_or_none()
    if course:
        course.total_enrolled = (course.total_enrolled or 0) + 1

    await db.commit()
    return {"message": "Enrolled successfully!"}


@router.get("/my-enrollments")
async def my_enrollments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all enrolled courses with progress."""
    result = await db.execute(
        select(AcademyEnrollment)
        .options(selectinload(AcademyEnrollment.course).selectinload(AcademyCourse.instructor))
        .where(AcademyEnrollment.user_id == current_user.id)
    )
    enrollments = result.scalars().all()
    return [
        {
            **_course_dict(e.course, enrolled=True, progress=e.progress_pct),
            "enrolled_at": e.enrolled_at.isoformat(),
            "completed_at": e.completed_at.isoformat() if e.completed_at else None,
            "completed_lesson_ids": e.completed_lesson_ids,
            "last_lesson_id": e.last_lesson_id,
        }
        for e in enrollments if e.course
    ]


@router.post("/progress/{course_id}")
async def update_progress(
    course_id: int,
    data: ProgressUpdateIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a lesson as complete and update progress %."""
    result = await db.execute(
        select(AcademyEnrollment).where(
            and_(AcademyEnrollment.user_id == current_user.id,
                 AcademyEnrollment.course_id == course_id)
        )
    )
    enrollment = result.scalar_one_or_none()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Not enrolled in this course")

    completed = list(enrollment.completed_lesson_ids or [])
    if data.lesson_id not in completed:
        completed.append(data.lesson_id)
    enrollment.completed_lesson_ids = completed
    enrollment.last_lesson_id = data.lesson_id

    # Calculate progress
    course_result = await db.execute(select(AcademyCourse).where(AcademyCourse.id == course_id))
    course = course_result.scalar_one_or_none()
    if course and course.total_lessons > 0:
        enrollment.progress_pct = round(len(completed) / course.total_lessons * 100, 1)

    await db.commit()
    return {"progress_pct": enrollment.progress_pct, "completed_lesson_ids": completed}


# ─── Certificate Endpoints ─────────────────────────────────────────────────────

@router.post("/complete/{course_id}")
async def complete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark course complete and issue certificate."""
    import datetime as dt

    result = await db.execute(
        select(AcademyEnrollment)
        .options(selectinload(AcademyEnrollment.course).selectinload(AcademyCourse.instructor))
        .where(and_(AcademyEnrollment.user_id == current_user.id, AcademyEnrollment.course_id == course_id))
    )
    enrollment = result.scalar_one_or_none()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Not enrolled")

    enrollment.completed_at = dt.datetime.utcnow()
    enrollment.progress_pct = 100.0

    # Check for existing cert
    cert_result = await db.execute(
        select(AcademyCertificate).where(
            and_(AcademyCertificate.user_id == current_user.id,
                 AcademyCertificate.course_id == course_id)
        )
    )
    if not cert_result.scalar_one_or_none():
        cert = AcademyCertificate(
            user_id=current_user.id,
            course_id=course_id,
            credential_id=str(uuid.uuid4()),
            user_name=current_user.email.split("@")[0],
            course_title=enrollment.course.title,
            instructor_name=enrollment.course.instructor.display_name if enrollment.course.instructor else "ATLAS",
        )
        db.add(cert)
        await db.commit()
        await db.refresh(cert)
        return {"message": "🎓 Course completed! Certificate issued.", "credential_id": cert.credential_id}

    await db.commit()
    return {"message": "Course marked complete."}


@router.get("/certificates")
async def my_certificates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(AcademyCertificate).where(AcademyCertificate.user_id == current_user.id)
    )
    certs = result.scalars().all()
    return [
        {
            "id": c.id,
            "credential_id": c.credential_id,
            "course_title": c.course_title,
            "instructor_name": c.instructor_name,
            "issued_at": c.issued_at.isoformat(),
        }
        for c in certs
    ]


# ─── Review Endpoints ──────────────────────────────────────────────────────────

@router.post("/reviews/{course_id}")
async def add_review(
    course_id: int,
    data: ReviewCreateIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not 1 <= data.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be 1-5")
    review = AcademyReview(user_id=current_user.id, course_id=course_id, **data.model_dump())
    db.add(review)

    # Update avg rating
    result = await db.execute(select(AcademyCourse).where(AcademyCourse.id == course_id))
    course = result.scalar_one_or_none()
    if course:
        reviews_result = await db.execute(
            select(func.avg(AcademyReview.rating)).where(AcademyReview.course_id == course_id)
        )
        course.avg_rating = round(float(reviews_result.scalar() or data.rating), 2)

    await db.commit()
    return {"message": "Review submitted"}


# ─── Instructor Portal ─────────────────────────────────────────────────────────

@router.post("/instructor/apply")
async def apply_instructor(
    data: InstructorApplyIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = await db.execute(
        select(AcademyInstructor).where(AcademyInstructor.user_id == current_user.id)
    )
    if existing.scalar_one_or_none():
        return {"message": "Already an instructor"}
    instructor = AcademyInstructor(user_id=current_user.id, **data.model_dump())
    db.add(instructor)
    await db.commit()
    return {"message": "🎉 Welcome to Atlas Academy as an Instructor! You can now create courses."}


@router.get("/instructor/me")
async def get_instructor_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(AcademyInstructor)
        .options(selectinload(AcademyInstructor.courses))
        .where(AcademyInstructor.user_id == current_user.id)
    )
    instructor = result.scalar_one_or_none()
    if not instructor:
        return {"is_instructor": False}
    return {
        "is_instructor": True,
        "id": instructor.id,
        "display_name": instructor.display_name,
        "bio": instructor.bio,
        "expertise": instructor.expertise,
        "verified": instructor.verified,
        "total_students": instructor.total_students,
        "total_revenue": instructor.total_revenue,
        "revenue_share": instructor.revenue_share,
        "courses": [
            {
                "id": c.id, "title": c.title, "is_published": c.is_published,
                "total_enrolled": c.total_enrolled, "avg_rating": c.avg_rating,
                "category": c.category, "level": c.level,
            }
            for c in instructor.courses
        ],
    }


# ─── AI Skill Gap Engine ───────────────────────────────────────────────────────

@router.post("/skill-gap")
async def analyze_skill_gap(
    data: SkillGapIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI-powered skill gap analysis: resume vs job requirements."""
    candidate_skills = data.candidate_skills or []

    # Try to get skills from candidate profile if not provided
    if not candidate_skills:
        cand_result = await db.execute(
            select(Candidate).where(Candidate.email == current_user.email)
        )
        candidate = cand_result.scalar_one_or_none()
        if candidate:
            candidate_skills = [s.lower().strip() for s in (candidate.skills or [])]

    job_skills_lower = [s.lower().strip() for s in data.job_skills]
    cand_skills_lower = [s.lower().strip() for s in candidate_skills]

    matching = [s for s in data.job_skills if s.lower().strip() in cand_skills_lower]
    missing = [s for s in data.job_skills if s.lower().strip() not in cand_skills_lower]

    # Find recommended courses for missing skills
    recommended_courses = []
    if missing:
        courses_result = await db.execute(
            select(AcademyCourse)
            .options(selectinload(AcademyCourse.instructor))
            .where(AcademyCourse.is_published == True)
        )
        all_courses = courses_result.scalars().all()
        for course in all_courses:
            course_skills_lower = [s.lower().strip() for s in (course.skills_taught or [])]
            overlap = [m for m in missing if m.lower() in course_skills_lower or any(m.lower() in t.lower() for t in course.tags)]
            if overlap:
                recommended_courses.append({
                    "id": course.id,
                    "title": course.title,
                    "category": course.category,
                    "level": course.level,
                    "covers_skills": overlap,
                    "is_free": course.is_free,
                    "avg_rating": course.avg_rating,
                    "instructor": course.instructor.display_name if course.instructor else "ATLAS",
                })

    # AI roadmap generation
    ai_roadmap = None
    try:
        ai = await AIProviderFactory.get_provider(settings.AI_PROVIDER, settings.AI_MODEL)
        prompt = f"""You are an expert career coach at Atlas Academy.

Job Title: {data.job_title}
Required Skills: {', '.join(data.job_skills)}
Candidate Has: {', '.join(candidate_skills) or 'Not specified'}
Missing Skills: {', '.join(missing)}

Create a concise, practical learning roadmap to bridge these skill gaps.
Format as numbered months (Month 1, Month 2, etc.) with specific actions.
Keep it under 200 words. Be direct and actionable."""
        ai_roadmap = await ai.chat([{"role": "user", "content": prompt}])
    except Exception:
        ai_roadmap = f"Focus on learning: {', '.join(missing[:3])}. Start with foundational courses, then move to hands-on projects."

    # Save analysis
    gap = AcademySkillGap(
        user_id=current_user.id,
        job_title=data.job_title,
        job_required_skills=data.job_skills,
        candidate_skills=candidate_skills,
        missing_skills=missing,
        matching_skills=matching,
        recommended_course_ids=[c["id"] for c in recommended_courses],
        ai_roadmap=ai_roadmap,
    )
    db.add(gap)
    await db.commit()

    return {
        "job_title": data.job_title,
        "match_score": round(len(matching) / max(len(data.job_skills), 1) * 100, 1),
        "matching_skills": matching,
        "missing_skills": missing,
        "recommended_courses": recommended_courses,
        "ai_roadmap": ai_roadmap,
        "analysis_id": gap.id,
    }


@router.get("/skill-gap/history")
async def skill_gap_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(AcademySkillGap)
        .where(AcademySkillGap.user_id == current_user.id)
        .order_by(AcademySkillGap.created_at.desc())
        .limit(10)
    )
    gaps = result.scalars().all()
    return [
        {
            "id": g.id,
            "job_title": g.job_title,
            "missing_skills": g.missing_skills,
            "matching_skills": g.matching_skills,
            "ai_roadmap": g.ai_roadmap,
            "created_at": g.created_at.isoformat(),
        }
        for g in gaps
    ]


# ─── AI Mentor / Roadmap ───────────────────────────────────────────────────────

@router.post("/ai-mentor")
async def ai_mentor_chat(
    payload: Dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI Mentor — answers learning questions, explains concepts, generates roadmaps."""
    question = payload.get("question", "")
    if not question:
        raise HTTPException(status_code=400, detail="Question required")

    # Get user context
    cand_result = await db.execute(select(Candidate).where(Candidate.email == current_user.email))
    candidate = cand_result.scalar_one_or_none()
    skills_context = f"Learner skills: {', '.join(candidate.skills or [])}" if candidate else ""

    try:
        ai = await AIProviderFactory.get_provider(settings.AI_PROVIDER, settings.AI_MODEL)
        system = f"""You are Nova — the AI Mentor at Atlas Academy, ATLAS's learning platform.
You help learners understand concepts, prepare for tech interviews, review code, and build career skills.
Be concise, practical, and encouraging. Use examples. {skills_context}"""
        reply = await ai.chat([
            {"role": "system", "content": system},
            {"role": "user", "content": question}
        ])
        return {"reply": reply}
    except Exception as e:
        return {"reply": f"I'm here to help! Let me answer: {question}\n\n(AI service temporarily unavailable — {str(e)})"}


@router.post("/roadmap")
async def generate_roadmap(
    data: RoadmapIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a personalised AI learning roadmap for a career goal."""
    cand_result = await db.execute(select(Candidate).where(Candidate.email == current_user.email))
    candidate = cand_result.scalar_one_or_none()
    current_skills = ', '.join(candidate.skills or []) if candidate else 'Not specified'

    try:
        ai = await AIProviderFactory.get_provider(settings.AI_PROVIDER, settings.AI_MODEL)
        prompt = f"""Create a detailed monthly learning roadmap for someone who wants to: {data.goal}
Current skills: {current_skills}
Format: Month 1: [Topic] - [Actions]. Month 2: [Topic] - [Actions]. Etc.
Include: specific technologies, free resources, projects to build. Max 6 months. Keep concise."""
        roadmap = await ai.chat([{"role": "user", "content": prompt}])
    except Exception:
        roadmap = f"Month 1: Foundations for {data.goal}\nMonth 2: Core skills\nMonth 3: Advanced topics\nMonth 4: Projects\nMonth 5: Portfolio\nMonth 6: Job-ready"

    path = AcademyLearningPath(user_id=current_user.id, goal=data.goal, ai_roadmap=roadmap)
    db.add(path)
    await db.commit()
    return {"goal": data.goal, "roadmap": roadmap, "path_id": path.id}


# ─── Project Submission ────────────────────────────────────────────────────────

@router.post("/projects/{course_id}")
async def submit_project(
    course_id: int,
    data: ProjectSubmitIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = AcademyProject(user_id=current_user.id, course_id=course_id, **data.model_dump())

    # AI feedback
    try:
        ai = await AIProviderFactory.get_provider(settings.AI_PROVIDER, settings.AI_MODEL)
        prompt = f"Review this student project submission for an Atlas Academy course.\nTitle: {data.title}\nDescription: {data.description or 'N/A'}\nURL: {data.submission_url or 'N/A'}\nGitHub: {data.github_url or 'N/A'}\n\nProvide brief constructive feedback (3-4 sentences) on quality, completeness, and improvements."
        project.ai_feedback = await ai.chat([{"role": "user", "content": prompt}])
        project.score = 75.0  # base score, real scoring requires rubric
    except Exception:
        project.ai_feedback = "Project submitted! An instructor will review your work shortly."

    db.add(project)
    await db.commit()
    return {"message": "Project submitted!", "ai_feedback": project.ai_feedback}


# ─── Stats ────────────────────────────────────────────────────────────────────

@router.get("/stats")
async def academy_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Summary stats for the Academy dashboard header."""
    total_courses = (await db.execute(select(func.count(AcademyCourse.id)).where(AcademyCourse.is_published == True))).scalar() or 0
    total_instructors = (await db.execute(select(func.count(AcademyInstructor.id)))).scalar() or 0
    my_certs = (await db.execute(select(func.count(AcademyCertificate.id)).where(AcademyCertificate.user_id == current_user.id))).scalar() or 0
    my_courses = (await db.execute(select(func.count(AcademyEnrollment.id)).where(AcademyEnrollment.user_id == current_user.id))).scalar() or 0
    return {
        "total_courses": total_courses,
        "total_instructors": total_instructors,
        "my_certificates": my_certs,
        "my_enrolled_courses": my_courses,
    }
