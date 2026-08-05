"""
Atlas ATS AI Scoring Pipeline
Endpoint: POST /api/v1/ats/score
"""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

import httpx
from atlas.api.deps import get_current_user
from atlas.database.models import User
from atlas.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()


# ──────────────────────────────────────────────────────────
#  Schemas
# ──────────────────────────────────────────────────────────

class ATSScoreRequest(BaseModel):
    job_description: str
    resume_text: str

class ParsedProfile(BaseModel):
    name: str = ""
    current_title: str = ""
    total_exp_years: float = 0
    top_skills: List[str] = []

class SkillsAnalysis(BaseModel):
    matched: List[str] = []
    missing: List[str] = []
    bonus: List[str] = []

class Scoring(BaseModel):
    match_score: int = 0
    tier: str = "Low Fit"
    justification: str = ""

class ATSScoreResponse(BaseModel):
    parsed_profile: ParsedProfile
    knockout_status: str = "passed"
    knockout_reasons: List[str] = []
    skills_analysis: SkillsAnalysis
    scoring: Scoring


# ──────────────────────────────────────────────────────────
#  Gemini call helper
# ──────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are the core AI intelligence engine for an advanced ATS and recruitment SaaS.
Analyze the provided Job Description (JD) and Candidate Resume Data.
Process the data according to four pillars and return a highly structured JSON response.

1. DATA PARSING & SCHEMA CONVERSION
   - Extract: name, current_title, total_exp_years (numeric), top_skills (list of strings)

2. KNOCKOUT FILTER EVALUATION
   - Check for: required certifications, legal work authorization, mandatory minimum years of experience
   - Set knockout_status to "passed" or "failed". List reasons in knockout_reasons array.

3. SEMANTIC KEYWORD MATCHING (use contextual synonyms — e.g. "MERN Stack" matches "React, Node.js, MongoDB")
   - matched: skills candidate has that JD wants
   - missing: critical skills from JD the candidate lacks
   - bonus: candidate skills that are adjacent/valuable but not required

4. SCORING & RANKING
   - match_score: 0-100 integer
   - tier: exactly one of "Top Match" (85-100), "Strong Fit" (70-84), "Potential Fit" (50-69), "Low Fit" (<50)
   - justification: exactly 2 sentences, candid and specific

Respond ONLY with valid JSON — no markdown, no extra text:
{
  "parsed_profile": { "name": "", "current_title": "", "total_exp_years": 0, "top_skills": [] },
  "knockout_status": "passed",
  "knockout_reasons": [],
  "skills_analysis": { "matched": [], "missing": [], "bonus": [] },
  "scoring": { "match_score": 0, "tier": "", "justification": "" }
}"""


def _tier_from_score(score: int) -> str:
    if score >= 85: return "Top Match"
    if score >= 70: return "Strong Fit"
    if score >= 50: return "Potential Fit"
    return "Low Fit"


async def _call_gemini(jd: str, resume: str) -> dict:
    api_key = getattr(settings, "GEMINI_API_KEY", None) or getattr(settings, "GOOGLE_API_KEY", None)
    if not api_key:
        raise HTTPException(status_code=503, detail="AI scoring not configured. Set GEMINI_API_KEY.")

    user_prompt = f"JOB DESCRIPTION:\n{jd}\n\n---\n\nCANDIDATE RESUME:\n{resume}"
    payload = {
        "system_instruction": {"parts": [{"text": _SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1200},
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=payload)
        if resp.status_code != 200:
            logger.error(f"Gemini ATS error {resp.status_code}: {resp.text[:300]}")
            raise HTTPException(status_code=502, detail="AI scoring service error.")

    raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    # Strip markdown fences if model wraps anyway
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    return json.loads(raw)


# ──────────────────────────────────────────────────────────
#  Fallback (no API key) — rule-based scorer
# ──────────────────────────────────────────────────────────

def _rule_based_score(jd: str, resume: str) -> dict:
    """Simple keyword overlap scorer used when Gemini is unavailable."""
    import re

    jd_words = set(re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.]{2,}\b', jd.lower()))
    resume_words = set(re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.]{2,}\b', resume.lower()))

    stopwords = {"the","and","for","with","that","this","have","from","your","are","will","you",
                 "they","our","can","not","has","was","been","but","all","any","its","their"}
    jd_words -= stopwords
    resume_words -= stopwords

    matched = list(jd_words & resume_words)[:15]
    missing = list(jd_words - resume_words)[:10]

    score = min(100, int(len(matched) / max(len(jd_words), 1) * 100 * 1.8))

    # Extract name (first 2 words of resume as guess)
    first_line = resume.strip().split('\n')[0].strip()
    name = first_line if len(first_line) < 40 else ""

    return {
        "parsed_profile": {
            "name": name,
            "current_title": "Not extracted",
            "total_exp_years": 0,
            "top_skills": matched[:5],
        },
        "knockout_status": "passed",
        "knockout_reasons": [],
        "skills_analysis": {
            "matched": matched,
            "missing": missing,
            "bonus": [],
        },
        "scoring": {
            "match_score": score,
            "tier": _tier_from_score(score),
            "justification": (
                f"The candidate matches {len(matched)} out of approximately {len(jd_words)} key terms "
                f"from the job description. "
                f"For a full semantic analysis, configure a Gemini API key in the system settings."
            ),
        },
    }


# ──────────────────────────────────────────────────────────
#  Route
# ──────────────────────────────────────────────────────────

@router.post("/score", response_model=ATSScoreResponse)
async def ats_score(
    payload: ATSScoreRequest,
    current_user: User = Depends(get_current_user),
):
    """
    AI-powered ATS scoring pipeline.
    Parses resume, runs knockout filters, semantic skill matching, and produces
    a 0-100 match score with tier classification.
    """
    jd = payload.job_description.strip()
    resume = payload.resume_text.strip()

    if len(jd) < 50:
        raise HTTPException(status_code=422, detail="Job description is too short.")
    if len(resume) < 50:
        raise HTTPException(status_code=422, detail="Resume text is too short.")

    api_key = getattr(settings, "GEMINI_API_KEY", None) or getattr(settings, "GOOGLE_API_KEY", None)

    if api_key:
        try:
            result = await _call_gemini(jd, resume)
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Gemini ATS scoring failed, falling back to rule-based: {e}")
            result = _rule_based_score(jd, resume)
    else:
        result = _rule_based_score(jd, resume)

    # Ensure tier is consistent with score
    score = result.get("scoring", {}).get("match_score", 0)
    result["scoring"]["tier"] = _tier_from_score(score)

    return result
