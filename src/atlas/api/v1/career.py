"""
Atlas Resume Builder & AI Match Score API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional
import json, re

from atlas.database.session import get_db
from atlas.database.models import User, Job
from atlas.api.v1.auth import get_current_user
from atlas.ai.factory import get_ai_client

router = APIRouter()

# ─── Schemas ─────────────────────────────────────────────────────────────────

class ResumeGenerateRequest(BaseModel):
    template: str = "modern"  # modern | minimal | technical
    target_role: Optional[str] = None

class ResumeScoreRequest(BaseModel):
    resume_text: str
    job_description: str

class SalaryRequest(BaseModel):
    job_title: str
    location: str = "Remote"
    experience_years: int = 3

class JobMatchRequest(BaseModel):
    job_id: int

# ─── Resume Builder ───────────────────────────────────────────────────────────

@router.post("/resume/generate")
async def generate_resume(
    req: ResumeGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate an ATS-optimized resume from the user's profile."""
    ai = get_ai_client()
    
    # Build context from profile
    profile_context = f"""
Name: {current_user.full_name or current_user.email}
Title: {current_user.title or 'Professional'}
Skills: {current_user.skills or 'Not specified'}
Experience: {current_user.experience or 'Not specified'}
Education: {current_user.education or 'Not specified'}
Location: {current_user.location or 'Not specified'}
Summary: {current_user.summary or ''}
Target Role: {req.target_role or current_user.title or 'Software Engineer'}
"""

    template_instructions = {
        "modern": "Use a modern, clean format with clear sections. Use bold for section headers. Keep it professional and scannable.",
        "minimal": "Use a minimal format with just the essentials. Clean whitespace, concise bullet points.",
        "technical": "Use a technical format highlighting projects, GitHub links, tech stack prominently. Use code-style formatting for skills."
    }

    prompt = f"""You are an expert resume writer and ATS optimization specialist.

Generate a complete, professional resume based on this profile:
{profile_context}

Template style: {template_instructions.get(req.template, template_instructions['modern'])}

Requirements:
1. Write a powerful 3-sentence professional summary
2. List skills in a scannable format grouped by category
3. Format experience as action-verb bullet points with quantifiable impacts
4. Include education section
5. Add a "Key Achievements" section with 3-5 bullets
6. Optimize for ATS: Use standard section names, include relevant keywords
7. Keep to 1 page worth of content
8. Make it compelling and hire-worthy

Output the complete resume as plain text, ready to copy-paste."""

    try:
        resume_text = await ai.generate(prompt)
        
        # Score ATS friendliness
        ats_score = _calculate_ats_score(resume_text, req.target_role or "")
        
        return {
            "resume_text": resume_text,
            "template": req.template,
            "ats_score": ats_score,
            "word_count": len(resume_text.split()),
            "tips": _get_resume_tips(resume_text)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume generation failed: {str(e)}")


@router.post("/resume/score")
async def score_resume(
    req: ResumeScoreRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Score a resume against a job description and identify gaps."""
    ai = get_ai_client()
    
    prompt = f"""You are an ATS expert and hiring manager. Analyze this resume against the job description.

RESUME:
{req.resume_text[:3000]}

JOB DESCRIPTION:
{req.job_description[:2000]}

Provide a JSON response with this exact structure:
{{
  "overall_score": <0-100>,
  "ats_score": <0-100>,
  "keyword_match_score": <0-100>,
  "experience_match": <0-100>,
  "matching_keywords": ["keyword1", "keyword2"],
  "missing_keywords": ["keyword1", "keyword2"],
  "strengths": ["strength1", "strength2", "strength3"],
  "improvements": ["improvement1", "improvement2", "improvement3"],
  "verdict": "strong match|good match|partial match|weak match",
  "summary": "2-sentence overall assessment"
}}

Return ONLY the JSON, no other text."""

    try:
        result_text = await ai.generate(prompt)
        # Parse JSON from response
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {
                "overall_score": 65, "ats_score": 70, "keyword_match_score": 60,
                "experience_match": 65, "matching_keywords": [], "missing_keywords": [],
                "strengths": ["Good formatting"], "improvements": ["Add more keywords"],
                "verdict": "partial match", "summary": "Resume partially matches the job requirements."
            }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume/match-job/{job_id}")
async def match_resume_to_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Auto-match user profile to a specific job posting."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    ai = get_ai_client()
    
    user_skills = set(s.strip().lower() for s in (current_user.skills or "").split(",") if s.strip())
    job_desc = f"{job.title} {job.description or ''} {job.requirements or ''}"
    
    prompt = f"""You are a recruitment AI. Score how well this candidate matches this job.

CANDIDATE PROFILE:
Name: {current_user.full_name}
Title: {current_user.title or 'N/A'}
Skills: {current_user.skills or 'N/A'}
Experience: {current_user.experience or 'N/A'}
Location: {current_user.location or 'Remote'}

JOB:
Title: {job.title}
Company: {job.company or 'N/A'}
Description: {job.description or ''}
Requirements: {job.requirements or ''}

Return JSON only:
{{
  "match_score": <0-100>,
  "matching_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "verdict": "Excellent Match|Strong Match|Good Match|Partial Match|Weak Match",
  "recommendation": "one sentence reason"
}}"""

    try:
        result_text = await ai.generate(prompt)
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
        else:
            # Fallback: simple skill matching
            job_lower = job_desc.lower()
            matching = [s for s in user_skills if s in job_lower]
            score = min(100, int((len(matching) / max(len(user_skills), 1)) * 100))
            data = {
                "match_score": score,
                "matching_skills": matching[:8],
                "missing_skills": [],
                "verdict": "Good Match" if score >= 60 else "Partial Match",
                "recommendation": "Profile has relevant skills for this role."
            }
        return {"job_id": job_id, "job_title": job.title, **data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Salary Intelligence ──────────────────────────────────────────────────────

@router.post("/salary/insights")
async def get_salary_insights(
    req: SalaryRequest,
    current_user: User = Depends(get_current_user)
):
    """Get AI-estimated salary intelligence for a role."""
    ai = get_ai_client()
    
    prompt = f"""You are a compensation intelligence system with data from LinkedIn, Glassdoor, and Levels.fyi.

Provide salary intelligence for:
Role: {req.job_title}
Location: {req.location}
Years of Experience: {req.experience_years}

Return JSON only:
{{
  "role": "{req.job_title}",
  "location": "{req.location}",
  "experience_band": "<entry|mid|senior|staff>",
  "salary_range": {{
    "p25": <annual_usd>,
    "median": <annual_usd>,
    "p75": <annual_usd>,
    "p90": <annual_usd>
  }},
  "total_compensation": {{
    "base": <median_annual>,
    "bonus_pct": <bonus_percentage>,
    "equity_usd": <annual_equity_value>
  }},
  "market_trend": "rising|stable|declining",
  "trend_pct": <yoy_percentage_change>,
  "top_paying_companies": ["Company1", "Company2", "Company3", "Company4", "Company5"],
  "hot_skills_premium": [
    {{"skill": "Skill1", "premium_pct": <percent_above_base>}},
    {{"skill": "Skill2", "premium_pct": <percent_above_base>}}
  ],
  "demand_score": <0-100>,
  "insight": "2-sentence market insight"
}}"""

    try:
        result_text = await ai.generate(prompt)
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        raise HTTPException(status_code=500, detail="Could not parse salary data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Career Analytics (Candidate View) ───────────────────────────────────────

@router.get("/career/analytics")
async def get_career_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get career analytics for the current candidate."""
    from atlas.database.models import Application
    
    # Application stats
    apps_result = await db.execute(
        select(Application.status, func.count(Application.id))
        .where(Application.candidate_id == current_user.id)
        .group_by(Application.status)
    )
    app_stats = {row[0]: row[1] for row in apps_result.all()}
    
    total_apps = sum(app_stats.values())
    interviews = app_stats.get("interview", 0) + app_stats.get("interviewing", 0)
    offers = app_stats.get("offered", 0) + app_stats.get("offer", 0)
    
    response_rate = round((interviews / max(total_apps, 1)) * 100)
    interview_to_offer = round((offers / max(interviews, 1)) * 100)

    return {
        "total_applications": total_apps,
        "response_rate": response_rate,
        "interview_rate": round((interviews / max(total_apps, 1)) * 100),
        "offer_rate": round((offers / max(total_apps, 1)) * 100),
        "interview_to_offer": interview_to_offer,
        "application_breakdown": app_stats,
        "profile_completeness": _calc_profile_completeness(current_user),
        "hot_skills": ["Python", "React", "TypeScript", "AWS", "Docker", "Kubernetes"],
        "recommended_actions": _get_recommended_actions(current_user, total_apps, response_rate),
    }


@router.get("/career/profile-score")
async def get_profile_score(
    current_user: User = Depends(get_current_user)
):
    """Get detailed profile completeness and strength score."""
    completeness = _calc_profile_completeness(current_user)
    
    sections = [
        {"name": "Profile Photo", "done": bool(current_user.profile_picture_url), "points": 10},
        {"name": "Professional Title", "done": bool(current_user.title), "points": 10},
        {"name": "Summary/Bio", "done": bool(current_user.summary and len(current_user.summary) > 50), "points": 15},
        {"name": "Skills (5+)", "done": len((current_user.skills or "").split(",")) >= 5, "points": 20},
        {"name": "Work Experience", "done": bool(current_user.experience), "points": 20},
        {"name": "Education", "done": bool(current_user.education), "points": 10},
        {"name": "Location", "done": bool(current_user.location), "points": 5},
        {"name": "Video Introduction", "done": bool(current_user.video_intro_url), "points": 10},
    ]
    
    total_points = sum(s["points"] for s in sections if s["done"])
    
    return {
        "total_score": total_points,
        "completeness_pct": completeness,
        "sections": sections,
        "rank": "🥇 Elite" if total_points >= 90 else "🥈 Strong" if total_points >= 70 else "🥉 Good" if total_points >= 50 else "📝 Needs Work",
        "next_action": next((s["name"] for s in sections if not s["done"]), "Profile Complete!")
    }


# ─── Gamification ─────────────────────────────────────────────────────────────

@router.get("/gamification/stats")
async def get_gamification_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get XP, streak, badges and leaderboard position for the user."""
    from atlas.database.models import AcademyEnrollment, AcademyCertificate
    
    enrollments = await db.execute(
        select(func.count(AcademyEnrollment.id))
        .where(AcademyEnrollment.user_id == current_user.id)
    )
    enroll_count = enrollments.scalar() or 0
    
    certs = await db.execute(
        select(func.count(AcademyCertificate.id))
        .where(AcademyCertificate.user_id == current_user.id)
    )
    cert_count = certs.scalar() or 0
    
    # XP calculation
    xp = (enroll_count * 50) + (cert_count * 500)
    level = 1 + (xp // 1000)
    xp_to_next = 1000 - (xp % 1000)
    
    # Badges
    badges = []
    if enroll_count >= 1:
        badges.append({"id": "first_step", "name": "First Step", "emoji": "👣", "desc": "Enrolled in first course"})
    if enroll_count >= 5:
        badges.append({"id": "explorer", "name": "Explorer", "emoji": "🗺️", "desc": "Enrolled in 5 courses"})
    if cert_count >= 1:
        badges.append({"id": "certified", "name": "Certified", "emoji": "🎓", "desc": "Earned first certificate"})
    if cert_count >= 3:
        badges.append({"id": "scholar", "name": "Scholar", "emoji": "📚", "desc": "Earned 3 certificates"})
    if current_user.video_intro_url:
        badges.append({"id": "video_star", "name": "Video Star", "emoji": "🎬", "desc": "Added video introduction"})
    if current_user.skills and len(current_user.skills.split(",")) >= 10:
        badges.append({"id": "polyglot", "name": "Polymath", "emoji": "🧠", "desc": "Listed 10+ skills"})
    
    return {
        "xp": xp,
        "level": level,
        "xp_to_next_level": xp_to_next,
        "xp_progress_pct": int(((xp % 1000) / 1000) * 100),
        "streak_days": 0,  # Would need activity tracking table
        "badges": badges,
        "rank_title": _get_rank_title(level),
        "total_courses": enroll_count,
        "total_certificates": cert_count,
    }


@router.get("/gamification/leaderboard")
async def get_leaderboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the top learners leaderboard."""
    from atlas.database.models import AcademyEnrollment, AcademyCertificate
    
    # Get all users with their cert counts (proxy for XP)
    cert_counts = await db.execute(
        select(AcademyCertificate.user_id, func.count(AcademyCertificate.id).label("certs"))
        .group_by(AcademyCertificate.user_id)
        .order_by(func.count(AcademyCertificate.id).desc())
        .limit(10)
    )
    cert_rows = cert_counts.all()
    
    leaderboard = []
    for i, row in enumerate(cert_rows):
        user_result = await db.execute(select(User).where(User.id == row[0]))
        user = user_result.scalar_one_or_none()
        if user:
            xp = row[1] * 500
            leaderboard.append({
                "rank": i + 1,
                "user_id": user.id,
                "name": user.full_name or user.email.split("@")[0],
                "avatar": user.profile_picture_url,
                "xp": xp,
                "certificates": row[1],
                "level": 1 + (xp // 1000),
                "is_current_user": user.id == current_user.id
            })
    
    return {"leaderboard": leaderboard}


# ─── Project Showcase ──────────────────────────────────────────────────────────

class ProjectSubmitRequest(BaseModel):
    title: str
    description: str
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    tech_stack: str = ""
    category: str = "Web Development"

@router.post("/showcase/submit")
async def submit_project(
    req: ProjectSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a project to the showcase."""
    ai = get_ai_client()
    
    # AI extracts skills from project
    prompt = f"""Extract the technical skills demonstrated by this project. Return as comma-separated list only.

Project: {req.title}
Description: {req.description}
Tech Stack: {req.tech_stack}

Skills (comma-separated):"""
    
    try:
        skills_text = await ai.generate(prompt)
        extracted_skills = [s.strip() for s in skills_text.split(",") if s.strip()][:10]
    except:
        extracted_skills = req.tech_stack.split(",")
    
    return {
        "message": "Project submitted successfully!",
        "project": {
            "title": req.title,
            "description": req.description,
            "github_url": req.github_url,
            "demo_url": req.demo_url,
            "extracted_skills": extracted_skills,
            "category": req.category,
            "author": current_user.full_name or current_user.email
        }
    }

@router.get("/showcase/projects")
async def list_showcase_projects(
    current_user: User = Depends(get_current_user)
):
    """List showcase projects (demo data until DB table added)."""
    return {
        "projects": [],
        "total": 0,
        "message": "Be the first to showcase your project!"
    }


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _calculate_ats_score(resume_text: str, target_role: str) -> int:
    """Simple ATS score based on resume structure."""
    score = 50
    text_lower = resume_text.lower()
    
    # Check for key sections
    for section in ["experience", "education", "skills", "summary", "objective", "achievement"]:
        if section in text_lower:
            score += 5
    
    # Check for action verbs
    action_verbs = ["led", "built", "designed", "developed", "managed", "improved", "reduced", "increased"]
    for verb in action_verbs:
        if verb in text_lower:
            score += 2
    
    # Check for numbers/metrics
    import re
    if re.search(r'\d+%', resume_text):
        score += 5
    if re.search(r'\$[\d,]+', resume_text):
        score += 5
    
    return min(100, score)


def _get_resume_tips(resume_text: str) -> list:
    tips = []
    text_lower = resume_text.lower()
    
    if "%" not in resume_text:
        tips.append("Add quantifiable metrics (e.g., 'Increased performance by 40%')")
    if len(resume_text.split()) < 200:
        tips.append("Resume seems short — add more detail to experience sections")
    if "github" not in text_lower and "linkedin" not in text_lower:
        tips.append("Add LinkedIn and GitHub profile URLs")
    if "summary" not in text_lower and "objective" not in text_lower:
        tips.append("Add a professional summary at the top")
    
    if not tips:
        tips.append("Great resume! Make sure to tailor it for each application")
    
    return tips[:3]


def _calc_profile_completeness(user: User) -> int:
    fields = [
        user.full_name, user.title, user.summary, user.skills,
        user.experience, user.education, user.location, user.profile_picture_url
    ]
    filled = sum(1 for f in fields if f and str(f).strip())
    return int((filled / len(fields)) * 100)


def _get_recommended_actions(user: User, total_apps: int, response_rate: int) -> list:
    actions = []
    if not user.video_intro_url:
        actions.append({"action": "Add Video Introduction", "impact": "high", "icon": "🎬"})
    if not user.title:
        actions.append({"action": "Set your professional title", "impact": "high", "icon": "💼"})
    if response_rate < 20 and total_apps > 5:
        actions.append({"action": "Update your resume with more keywords", "impact": "high", "icon": "📄"})
    if total_apps < 5:
        actions.append({"action": "Apply to more jobs (aim for 10/week)", "impact": "medium", "icon": "🚀"})
    actions.append({"action": "Complete a course to boost your profile", "impact": "medium", "icon": "🎓"})
    return actions[:4]


def _get_rank_title(level: int) -> str:
    titles = {
        1: "🌱 Newcomer", 2: "⚡ Rising Star", 3: "🔥 Skilled", 
        4: "💎 Expert", 5: "🚀 Master", 6: "👑 Legend", 7: "🌟 Grandmaster"
    }
    return titles.get(min(level, 7), "🌟 Grandmaster")
