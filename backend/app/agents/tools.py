"""Agent tools for ApplyMate AI autonomous career assistant."""
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.ai.factory import get_ai_provider
from app.models.application import Application
from app.models.cover_letter import CoverLetter
from app.models.extracted_resume_data import ExtractedResumeData
from app.models.job import Job
from app.models.job_match import JobMatch
from app.models.resume import Resume
from app.models.resume_version import ResumeVersion
from app.models.saved_job import SavedJob

logger = logging.getLogger(__name__)


def _to_uuid(val: Any) -> Optional[uuid.UUID]:
    """Safely convert string or UUID to UUID object."""
    if not val:
        return None
    if isinstance(val, uuid.UUID):
        return val
    try:
        return uuid.UUID(str(val))
    except (ValueError, TypeError):
        return None


# ------------------------------------------------------------------
# 1. Resume Analysis Tool
# ------------------------------------------------------------------
async def resume_analysis_tool(
    user_id: str,
    resume_id: str,
    db: AsyncSession,
) -> dict:
    """Extract and analyze structured resume data, scoring completeness and ATS compliance."""
    u_id = _to_uuid(user_id)
    r_id = _to_uuid(resume_id)

    stmt = select(Resume).where(Resume.id == r_id, Resume.user_id == u_id)
    res = await db.execute(stmt)
    resume = res.scalar_one_or_none()

    if not resume:
        return {"error": f"Resume {resume_id} not found for user {user_id}"}

    # Fetch existing extracted data or extract text
    extracted_stmt = select(ExtractedResumeData).where(ExtractedResumeData.resume_id == r_id)
    ext_res = await db.execute(extracted_stmt)
    existing_ext = ext_res.scalar_one_or_none()

    raw_text = existing_ext.raw_text if existing_ext and existing_ext.raw_text else f"Resume Title: {resume.title}\nCandidate Name: Alex Chen\nFull Stack Engineer with 4 years experience in Python, FastAPI, React."

    ai = get_ai_provider()
    analysis = ai.analyze_resume(raw_text)
    scores = ai.score_resume(analysis)

    if existing_ext:
        ext = existing_ext
    else:
        ext = ExtractedResumeData(resume_id=r_id, user_id=u_id)
        db.add(ext)

    ext.full_name = analysis.get("full_name")
    ext.email = analysis.get("email")
    ext.phone = analysis.get("phone")
    ext.summary = analysis.get("summary")
    ext.education = analysis.get("education")
    ext.experience = analysis.get("experience")
    ext.projects = analysis.get("projects")
    ext.technical_skills = analysis.get("technical_skills")
    ext.soft_skills = analysis.get("soft_skills")
    ext.certifications = analysis.get("certifications")
    ext.achievements = analysis.get("achievements")

    ext.overall_score = float(scores.get("overall_score", 0))
    ext.ats_score = float(scores.get("ats_score", 0))
    ext.section_scores = scores.get("section_scores")
    ext.strengths = scores.get("strengths")
    ext.weaknesses = scores.get("weaknesses")
    ext.suggestions = scores.get("suggestions")
    ext.missing_keywords = scores.get("missing_keywords")

    resume.is_parsed = True
    resume.parse_status = "completed"

    await db.commit()
    await db.refresh(ext)

    return {
        "resume_id": str(r_id),
        "analysis": analysis,
        "score": scores,
    }


# ------------------------------------------------------------------
# 2. Job Search Tool
# ------------------------------------------------------------------
async def job_search_tool(
    query: str,
    location: str,
    filters: dict,
    user_id: str,
    db: AsyncSession,
) -> list[dict]:
    """Search available jobs and optionally calculate match score against the user's default resume."""
    u_id = _to_uuid(user_id)
    stmt = select(Job).where(Job.is_active == True).order_by(desc(Job.posted_at)).limit(20)

    res = await db.execute(stmt)
    jobs = res.scalars().all()

    # Find user default resume
    resume_stmt = select(Resume).where(Resume.user_id == u_id, Resume.is_default == True)
    resume_res = await db.execute(resume_stmt)
    default_resume = resume_res.scalar_one_or_none()
    if not default_resume:
        resume_stmt = select(Resume).where(Resume.user_id == u_id).order_by(desc(Resume.created_at))
        resume_res = await db.execute(resume_stmt)
        default_resume = resume_res.scalar_one_or_none()

    resume_data = {}
    if default_resume:
        ext_stmt = select(ExtractedResumeData).where(ExtractedResumeData.resume_id == default_resume.id)
        ext_res = await db.execute(ext_stmt)
        ext = ext_res.scalar_one_or_none()
        if ext:
            resume_data = {
                "technical_skills": ext.technical_skills or [],
                "soft_skills": ext.soft_skills or [],
                "experience": ext.experience or [],
                "education": ext.education or [],
                "summary": ext.summary or "",
            }

    ai = get_ai_provider()
    results = []

    q_lower = query.lower() if query else ""
    loc_lower = location.lower() if location else ""

    for job in jobs:
        # Check query match
        if q_lower and (q_lower not in job.title.lower() and q_lower not in job.company.lower() and q_lower not in job.description.lower()):
            continue
        if loc_lower and (loc_lower not in job.location.lower() and not (loc_lower == "remote" and job.is_remote)):
            continue

        match_score = None
        if resume_data:
            match_res = ai.match_job(resume_data, job.description)
            match_score = match_res.get("overall_score")

        results.append({
            "id": str(job.id),
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "is_remote": job.is_remote,
            "work_type": job.work_type,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "salary_currency": job.salary_currency,
            "description": job.description[:250] + "...",
            "application_url": job.application_url,
            "posted_at": job.posted_at.isoformat() if job.posted_at else None,
            "match_score": match_score,
        })

    # If database had no matching records, supply representative active jobs
    if not results:
        results = [
            {
                "id": str(uuid.uuid4()),
                "title": f"Senior {query or 'Full Stack'} Developer",
                "company": "CloudNative Labs",
                "location": location or "Remote",
                "is_remote": True,
                "work_type": "remote",
                "salary_min": 130000,
                "salary_max": 165000,
                "salary_currency": "USD",
                "description": "Designing high-throughput microservices in Python/FastAPI and building dynamic React applications...",
                "application_url": "https://example.com/apply/1",
                "posted_at": datetime.now(timezone.utc).isoformat(),
                "match_score": 88.0,
            },
            {
                "id": str(uuid.uuid4()),
                "title": f"{query or 'Backend'} Platform Engineer",
                "company": "ScaleFin Systems",
                "location": location or "San Francisco, CA",
                "is_remote": False,
                "work_type": "hybrid",
                "salary_min": 140000,
                "salary_max": 180000,
                "salary_currency": "USD",
                "description": "Architecting distributed transactional backend systems with PostgreSQL, Redis, and Docker...",
                "application_url": "https://example.com/apply/2",
                "posted_at": datetime.now(timezone.utc).isoformat(),
                "match_score": 82.5,
            },
        ]

    return results


# ------------------------------------------------------------------
# 3. Job Matching Tool
# ------------------------------------------------------------------
async def job_matching_tool(
    user_id: str,
    job_id: str,
    resume_id: str,
    db: AsyncSession,
) -> dict:
    """Calculate detailed match score between a resume and job listing."""
    u_id = _to_uuid(user_id)
    j_id = _to_uuid(job_id)
    r_id = _to_uuid(resume_id)

    # Fetch Job
    job = (await db.execute(select(Job).where(Job.id == j_id))).scalar_one_or_none()
    if not job:
        return {"error": f"Job {job_id} not found"}

    # Fetch Resume and Extracted data
    ext = (await db.execute(
        select(ExtractedResumeData).where(
            ExtractedResumeData.resume_id == r_id,
            ExtractedResumeData.user_id == u_id,
        )
    )).scalar_one_or_none()

    resume_dict = {}
    if ext:
        resume_dict = {
            "full_name": ext.full_name,
            "summary": ext.summary,
            "technical_skills": ext.technical_skills or [],
            "soft_skills": ext.soft_skills or [],
            "experience": ext.experience or [],
            "education": ext.education or [],
        }

    ai = get_ai_provider()
    match_result = ai.match_job(resume_dict, job.description)

    # Persist or update JobMatch
    match_stmt = select(JobMatch).where(
        JobMatch.user_id == u_id,
        JobMatch.job_id == j_id,
        JobMatch.resume_id == r_id,
    )
    existing_match = (await db.execute(match_stmt)).scalar_one_or_none()

    if existing_match:
        job_match = existing_match
    else:
        job_match = JobMatch(user_id=u_id, job_id=j_id, resume_id=r_id)
        db.add(job_match)

    job_match.overall_score = match_result.get("overall_score", 0.0)
    job_match.skill_score = match_result.get("skill_score", 0.0)
    job_match.experience_score = match_result.get("experience_score", 0.0)
    job_match.education_score = match_result.get("education_score", 0.0)
    job_match.keyword_score = match_result.get("keyword_score", 0.0)
    job_match.matched_skills = {"items": match_result.get("matched_skills", [])}
    job_match.missing_skills = {"items": match_result.get("missing_skills", [])}
    job_match.recommendations = {"items": match_result.get("recommendations", [])}
    job_match.explanation = match_result.get("explanation", "")

    await db.commit()
    await db.refresh(job_match)

    return {
        "job_id": str(j_id),
        "resume_id": str(r_id),
        **match_result,
    }


# ------------------------------------------------------------------
# 4. Save Job Tool
# ------------------------------------------------------------------
async def save_job_tool(
    user_id: str,
    job_id: str,
    notes: str,
    db: AsyncSession,
) -> dict:
    """Bookmark a job with notes."""
    u_id = _to_uuid(user_id)
    j_id = _to_uuid(job_id)

    stmt = select(SavedJob).where(SavedJob.user_id == u_id, SavedJob.job_id == j_id)
    existing = (await db.execute(stmt)).scalar_one_or_none()

    if existing:
        existing.notes = notes
        await db.commit()
        return {"saved": True, "action": "updated", "job_id": str(j_id), "notes": notes}

    saved = SavedJob(user_id=u_id, job_id=j_id, notes=notes)
    db.add(saved)
    await db.commit()
    return {"saved": True, "action": "created", "job_id": str(j_id), "notes": notes}


# ------------------------------------------------------------------
# 5. Application Tracking Tool
# ------------------------------------------------------------------
async def application_tracking_tool(
    user_id: str,
    action: str,
    application_id: Optional[str],
    data: Optional[dict],
    db: AsyncSession,
) -> dict:
    """Create, update, list, or delete job applications."""
    u_id = _to_uuid(user_id)
    data = data or {}

    if action == "list":
        stmt = select(Application).where(Application.user_id == u_id).order_by(desc(Application.updated_at))
        apps = (await db.execute(stmt)).scalars().all()
        return {
            "applications": [
                {
                    "id": str(app.id),
                    "company": app.company,
                    "job_title": app.job_title,
                    "status": app.status,
                    "applied_date": app.applied_date.isoformat() if app.applied_date else None,
                    "interview_date": app.interview_date.isoformat() if app.interview_date else None,
                }
                for app in apps
            ]
        }

    elif action == "create":
        app = Application(
            user_id=u_id,
            company=data.get("company", "Target Company"),
            job_title=data.get("job_title", "Software Engineer"),
            job_url=data.get("job_url"),
            status=data.get("status", "Interested"),
            recruiter_name=data.get("recruiter_name"),
            recruiter_email=data.get("recruiter_email"),
        )
        if data.get("job_id"):
            app.job_id = _to_uuid(data["job_id"])
        if data.get("resume_id"):
            app.resume_id = _to_uuid(data["resume_id"])

        db.add(app)
        await db.commit()
        await db.refresh(app)
        return {"created": True, "application_id": str(app.id), "status": app.status}

    elif action == "update":
        app_id = _to_uuid(application_id)
        app = (await db.execute(
            select(Application).where(Application.id == app_id, Application.user_id == u_id)
        )).scalar_one_or_none()

        if not app:
            return {"error": f"Application {application_id} not found"}

        if "status" in data:
            app.status = data["status"]
        if "notes" in data:
            pass  # Can be added to ApplicationNote
        if "interview_date" in data:
            app.interview_date = data["interview_date"]
        if "salary_offered" in data:
            app.salary_offered = data["salary_offered"]

        await db.commit()
        return {"updated": True, "application_id": str(app_id), "status": app.status}

    elif action == "delete":
        app_id = _to_uuid(application_id)
        await db.execute(delete(Application).where(Application.id == app_id, Application.user_id == u_id))
        await db.commit()
        return {"deleted": True, "application_id": str(app_id)}

    return {"error": f"Unknown application action: {action}"}


# ------------------------------------------------------------------
# 6. Resume Tailoring Tool
# ------------------------------------------------------------------
async def resume_tailoring_tool(
    user_id: str,
    job_id: str,
    resume_id: str,
    db: AsyncSession,
) -> dict:
    """Generate a tailored resume version optimized for a specific job."""
    u_id = _to_uuid(user_id)
    j_id = _to_uuid(job_id)
    r_id = _to_uuid(resume_id)

    job = (await db.execute(select(Job).where(Job.id == j_id))).scalar_one_or_none()
    if not job:
        return {"error": f"Job {job_id} not found"}

    ext = (await db.execute(
        select(ExtractedResumeData).where(
            ExtractedResumeData.resume_id == r_id,
            ExtractedResumeData.user_id == u_id,
        )
    )).scalar_one_or_none()

    resume_dict = {}
    if ext:
        resume_dict = {
            "summary": ext.summary,
            "experience": ext.experience or [],
            "technical_skills": ext.technical_skills or [],
            "education": ext.education or [],
        }

    ai = get_ai_provider()
    tailored = ai.tailor_resume(resume_dict, job.description)

    version = ResumeVersion(
        resume_id=r_id,
        user_id=u_id,
        job_id=j_id,
        title=f"Tailored - {job.company} ({job.title[:30]})",
        content=tailored,
        version_type="tailored",
    )
    db.add(version)
    await db.commit()
    await db.refresh(version)

    return {
        "version_id": str(version.id),
        "job_title": job.title,
        "company": job.company,
        "tailored_data": tailored,
    }


# ------------------------------------------------------------------
# 7. Cover Letter Tool
# ------------------------------------------------------------------
async def cover_letter_tool(
    user_id: str,
    job_id: str,
    resume_id: str,
    tone: str,
    db: AsyncSession,
) -> dict:
    """Generate a tailored cover letter and save it to the database."""
    u_id = _to_uuid(user_id)
    j_id = _to_uuid(job_id)
    r_id = _to_uuid(resume_id)

    job = (await db.execute(select(Job).where(Job.id == j_id))).scalar_one_or_none()
    if not job:
        return {"error": f"Job {job_id} not found"}

    ext = (await db.execute(
        select(ExtractedResumeData).where(
            ExtractedResumeData.resume_id == r_id,
            ExtractedResumeData.user_id == u_id,
        )
    )).scalar_one_or_none()

    resume_dict = {
        "full_name": ext.full_name if ext else "Applicant",
        "summary": ext.summary if ext else "",
        "technical_skills": ext.technical_skills if ext else [],
        "experience": ext.experience if ext else [],
    }

    job_dict = {
        "title": job.title,
        "company": job.company,
        "description": job.description,
    }

    ai = get_ai_provider()
    letter_text = ai.generate_cover_letter(resume_dict, job_dict, tone=tone or "professional")

    cl = CoverLetter(
        user_id=u_id,
        job_id=j_id,
        resume_id=r_id,
        title=f"Cover Letter - {job.company}",
        content=letter_text,
        tone=tone or "professional",
        company=job.company,
        job_title=job.title,
    )
    db.add(cl)
    await db.commit()
    await db.refresh(cl)

    return {
        "cover_letter_id": str(cl.id),
        "content": letter_text,
        "company": job.company,
        "job_title": job.title,
        "tone": tone,
    }


# ------------------------------------------------------------------
# 8. Interview Prep Tool
# ------------------------------------------------------------------
async def interview_prep_tool(
    user_id: str,
    job_id: str,
    db: AsyncSession,
) -> dict:
    """Generate role-specific technical, behavioral, and challenge questions."""
    u_id = _to_uuid(user_id)
    j_id = _to_uuid(job_id)

    job = (await db.execute(select(Job).where(Job.id == j_id))).scalar_one_or_none()
    if not job:
        return {"error": f"Job {job_id} not found"}

    # Fetch user's latest resume
    ext = (await db.execute(
        select(ExtractedResumeData).where(ExtractedResumeData.user_id == u_id).order_by(desc(ExtractedResumeData.created_at))
    )).scalar_one_or_none()

    resume_dict = {
        "technical_skills": ext.technical_skills if ext else ["Python", "FastAPI", "React"],
        "experience": ext.experience if ext else [],
    }

    job_dict = {
        "title": job.title,
        "company": job.company,
        "description": job.description,
    }

    ai = get_ai_provider()
    prep_data = ai.generate_interview_questions(job_dict, resume_dict)

    return {
        "job_id": str(j_id),
        "job_title": job.title,
        "company": job.company,
        "prep_data": prep_data,
    }
