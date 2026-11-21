"""Analytics endpoints — all string IDs for SQLite compatibility."""
from typing import Any
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_active_user
from app.database import get_db

router = APIRouter()


@router.get("/dashboard")
async def dashboard_stats(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from app.models.application import Application
    from app.models.saved_job import SavedJob
    result = await db.execute(
        select(Application).where(Application.user_id == str(current_user.id))
    )
    apps = result.scalars().all()
    saved_result = await db.execute(
        select(SavedJob).where(SavedJob.user_id == str(current_user.id))
    )
    saved = saved_result.scalars().all()
    interviews = sum(1 for a in apps if "Interview" in (a.status or ""))
    offers = sum(1 for a in apps if a.status == "Offer Received")
    return {
        "total_applications": len(apps),
        "total_saved": len(saved),
        "total_interviews": interviews,
        "total_offers": offers,
        "total_rejections": sum(1 for a in apps if a.status == "Rejected"),
        "pending_applications": sum(1 for a in apps if a.status in ("Applied", "Assessment")),
        "conversion_rate": round(interviews / max(len(apps), 1) * 100, 1),
    }


# Frontend calls /analytics/timeline
@router.get("/timeline")
async def application_timeline(
    days: int = 30,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from app.models.application import Application
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(Application).where(
            Application.user_id == str(current_user.id),
        )
    )
    apps = result.scalars().all()
    by_date: dict = {}
    for a in apps:
        try:
            d = a.created_at.strftime("%Y-%m-%d") if a.created_at else "unknown"
        except Exception:
            d = str(a.created_at)[:10] if a.created_at else "unknown"
        by_date[d] = by_date.get(d, 0) + 1
    timeline = []
    for i in range(days):
        d = (datetime.now(timezone.utc) - timedelta(days=days - i - 1)).strftime("%Y-%m-%d")
        timeline.append({"date": d, "count": by_date.get(d, 0)})
    return timeline


# Keep old route for backward compat
@router.get("/applications")
async def application_timeline_legacy(
    days: int = 30,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await application_timeline(days, current_user, db)


# Frontend calls /analytics/by-status
@router.get("/by-status")
async def applications_by_status(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from app.models.application import Application
    result = await db.execute(
        select(Application).where(Application.user_id == str(current_user.id))
    )
    apps = result.scalars().all()
    status_counts: dict = {}
    for a in apps:
        s = a.status or "Applied"
        status_counts[s] = status_counts.get(s, 0) + 1
    if not status_counts:
        # Return demo structure so charts don't break
        return [
            {"status": "Applied", "count": 0},
            {"status": "Interview", "count": 0},
            {"status": "Offer", "count": 0},
            {"status": "Rejected", "count": 0},
        ]
    return [{"status": k, "count": v} for k, v in status_counts.items()]


@router.get("/skills")
async def skills_analytics(
    current_user=Depends(get_current_active_user),
) -> Any:
    return [
        {"skill": "Python", "demand": 85},
        {"skill": "React", "demand": 78},
        {"skill": "AWS", "demand": 72},
        {"skill": "Docker", "demand": 68},
        {"skill": "TypeScript", "demand": 65},
        {"skill": "PostgreSQL", "demand": 60},
        {"skill": "Kubernetes", "demand": 55},
        {"skill": "Machine Learning", "demand": 50},
    ]


@router.get("/weekly-report")
async def weekly_report(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from app.models.application import Application
    since = datetime.now(timezone.utc) - timedelta(days=7)
    result = await db.execute(
        select(Application).where(Application.user_id == str(current_user.id))
    )
    apps = result.scalars().all()
    count = len(apps)
    if count == 0:
        report = (
            "Start your job search journey! Upload your resume and browse 10+ curated job listings. "
            "The AI Agent can help you generate cover letters and prepare for interviews. "
            "Tip: Add your Gemini API key to unlock full AI capabilities."
        )
    else:
        report = (
            f"Great work! You have {count} application{'s' if count != 1 else ''} tracked. "
            "Consider following up on applications older than 5 days. "
            "Use the AI Agent to generate tailored cover letters for your top opportunities."
        )
    return {"report": report, "highlights": ["Keep applying consistently", "Tailor each resume", "Follow up after 5 days"]}
