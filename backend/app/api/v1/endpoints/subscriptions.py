"""Subscriptions endpoint — plan listing and upgrade (demo mode)."""
from fastapi import APIRouter, Depends
from app.api.deps import get_current_active_user

router = APIRouter()

PLANS = [
    {
        "id": "free",
        "name": "Free",
        "price_monthly": 0,
        "price_yearly": 0,
        "features": ["2 resume uploads", "5 AI analyses/month", "Job discovery", "Basic application tracker"],
        "limits": {"resume_uploads": 2, "ai_analyses": 5, "cover_letters": 3, "job_matches": 10},
    },
    {
        "id": "pro",
        "name": "Pro",
        "price_monthly": 12,
        "price_yearly": 99,
        "features": ["10 resume uploads", "50 AI analyses/month", "Resume tailoring", "Cover letter generation", "Interview preparation", "Advanced analytics"],
        "limits": {"resume_uploads": 10, "ai_analyses": 50, "cover_letters": 20, "job_matches": 100},
        "recommended": True,
    },
    {
        "id": "premium",
        "name": "Premium",
        "price_monthly": 29,
        "price_yearly": 239,
        "features": ["Unlimited resume uploads", "200 AI analyses/month", "Advanced agent workflows", "Priority support", "Extended analytics", "Multiple resume versions"],
        "limits": {"resume_uploads": -1, "ai_analyses": 200, "cover_letters": -1, "job_matches": -1},
    },
]


@router.get("/plans")
async def list_plans():
    """Return all available subscription plans."""
    return PLANS


@router.get("/my-subscription")
async def my_subscription(current_user=Depends(get_current_active_user)):
    """Return the current user's active subscription (default: Free)."""
    return {
        "plan": PLANS[0],
        "status": "active",
        "usage": {"ai_analyses": 0, "resume_uploads": 0, "cover_letters": 0, "job_matches": 0},
        "period_end": None,
    }


@router.post("/upgrade")
async def upgrade_plan(current_user=Depends(get_current_active_user)):
    """Upgrade subscription — demo mode only."""
    return {
        "message": "Payment integration is in demo mode. In production this connects to Stripe/Razorpay.",
        "demo": True,
    }
