"""AI Service — Core business logic layer for AI integration and agent execution."""
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import AgentOrchestrator, AgentResponse
from app.agents.tools import (
    cover_letter_tool,
    interview_prep_tool,
    job_matching_tool,
    resume_analysis_tool,
    resume_tailoring_tool,
)
from app.core.exceptions import NotFoundException, UsageLimitException
from app.integrations.ai.factory import get_ai_provider
from app.models.agent_task import AgentTask
from app.models.ai_conversation import AIConversation
from app.models.ai_conversation_message import AIConversationMessage
from app.models.subscription import SubscriptionPlan, UsageRecord, UserSubscription

logger = logging.getLogger(__name__)


def _to_uuid(val: Any) -> Optional[uuid.UUID]:
    if not val:
        return None
    if isinstance(val, uuid.UUID):
        return val
    try:
        return uuid.UUID(str(val))
    except (ValueError, TypeError):
        return None


class AIService:
    """Service handling AI operations, usage limits, and agent coordination."""

    @staticmethod
    async def check_usage_limit(
        user_id: str,
        action_type: str,
        db: AsyncSession,
        increment: bool = True,
    ) -> None:
        """Check whether the user is within their monthly subscription allowance.

        Raises UsageLimitException if over limit.
        """
        u_id = _to_uuid(user_id)
        now = datetime.now(timezone.utc)
        start_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

        # 1. Fetch user active subscription and plan
        sub_stmt = (
            select(UserSubscription)
            .where(
                UserSubscription.user_id == u_id,
                UserSubscription.status == "active",
            )
            .order_by(desc(UserSubscription.created_at))
        )
        sub = (await db.execute(sub_stmt)).scalar_one_or_none()

        plan = None
        if sub:
            plan_stmt = select(SubscriptionPlan).where(SubscriptionPlan.id == sub.plan_id)
            plan = (await db.execute(plan_stmt)).scalar_one_or_none()

        # Default limits for Free tier
        max_limit = 50  # generous default
        if action_type in ("ai_analysis", "analyze_resume"):
            max_limit = plan.max_ai_analyses_per_month if plan else 5
        elif action_type in ("cover_letter", "generate_cover_letter"):
            max_limit = plan.max_cover_letters_per_month if plan else 5
        elif action_type in ("job_match", "match"):
            max_limit = plan.max_job_matches_per_month if plan else 20
        elif action_type in ("chat", "agent"):
            max_limit = 100 if not plan else 500

        # 2. Query usage record for current period
        usage_stmt = select(UsageRecord).where(
            UsageRecord.user_id == u_id,
            UsageRecord.action_type == action_type,
            UsageRecord.period_start >= start_of_month,
        )
        usage_record = (await db.execute(usage_stmt)).scalar_one_or_none()

        current_count = usage_record.count if usage_record else 0

        if current_count >= max_limit:
            raise UsageLimitException(
                f"You have reached your monthly limit of {max_limit} for {action_type}. "
                f"Please upgrade your subscription to continue."
            )

        if increment:
            if usage_record:
                usage_record.count += 1
            else:
                end_of_month = (
                    datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
                    if now.month == 12
                    else datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
                )
                new_record = UsageRecord(
                    user_id=u_id,
                    action_type=action_type,
                    count=1,
                    period_start=start_of_month,
                    period_end=end_of_month,
                )
                db.add(new_record)
            await db.commit()

    @staticmethod
    async def process_chat(
        user_id: str,
        conversation_id: Optional[str],
        message: str,
        db: AsyncSession,
        context: Optional[dict] = None,
    ) -> AgentResponse:
        """Process agent chat message and coordinate tool execution."""
        await AIService.check_usage_limit(user_id, "chat", db, increment=True)
        provider = get_ai_provider()
        orchestrator = AgentOrchestrator(provider, db, user_id)
        return await orchestrator.process_message(
            message=message,
            conversation_id=conversation_id,
            context=context,
        )

    @staticmethod
    async def generate_cover_letter(
        user_id: str,
        job_id: str,
        resume_id: str,
        tone: str,
        db: AsyncSession,
    ) -> dict:
        """Generate and store personalized cover letter."""
        await AIService.check_usage_limit(user_id, "cover_letter", db, increment=True)
        result = await cover_letter_tool(
            user_id=user_id,
            job_id=job_id,
            resume_id=resume_id,
            tone=tone,
            db=db,
        )
        return result

    @staticmethod
    async def tailor_resume(
        user_id: str,
        job_id: str,
        resume_id: str,
        db: AsyncSession,
    ) -> dict:
        """Tailor resume sections for target job."""
        await AIService.check_usage_limit(user_id, "ai_analysis", db, increment=True)
        result = await resume_tailoring_tool(
            user_id=user_id,
            job_id=job_id,
            resume_id=resume_id,
            db=db,
        )
        return result

    @staticmethod
    async def analyze_resume(
        resume_id: str,
        user_id: str,
        db: AsyncSession,
    ) -> dict:
        """Trigger comprehensive resume parsing and ATS evaluation."""
        await AIService.check_usage_limit(user_id, "ai_analysis", db, increment=True)
        result = await resume_analysis_tool(
            user_id=user_id,
            resume_id=resume_id,
            db=db,
        )
        return result

    @staticmethod
    async def match_job(
        user_id: str,
        job_id: str,
        resume_id: str,
        db: AsyncSession,
    ) -> dict:
        """Calculate hybrid match score between resume and job."""
        await AIService.check_usage_limit(user_id, "job_match", db, increment=True)
        result = await job_matching_tool(
            user_id=user_id,
            job_id=job_id,
            resume_id=resume_id,
            db=db,
        )
        return result

    @staticmethod
    async def prepare_interview(
        user_id: str,
        job_id: str,
        db: AsyncSession,
    ) -> dict:
        """Generate interview questions and tips."""
        await AIService.check_usage_limit(user_id, "ai_analysis", db, increment=True)
        result = await interview_prep_tool(
            user_id=user_id,
            job_id=job_id,
            db=db,
        )
        return result

    @staticmethod
    async def approve_task(
        task_id: str,
        user_id: str,
        db: AsyncSession,
    ) -> dict:
        """Approve pending sensitive action."""
        provider = get_ai_provider()
        orchestrator = AgentOrchestrator(provider, db, user_id)
        return await orchestrator.approve_action(task_id)

    @staticmethod
    async def list_conversations(
        user_id: str,
        db: AsyncSession,
    ) -> list[dict]:
        """List all conversations for a user."""
        u_id = _to_uuid(user_id)
        stmt = (
            select(AIConversation)
            .where(AIConversation.user_id == u_id)
            .order_by(desc(AIConversation.updated_at))
        )
        convs = (await db.execute(stmt)).scalars().all()
        return [
            {
                "id": str(c.id),
                "title": c.title,
                "is_active": c.is_active,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            for c in convs
        ]

    @staticmethod
    async def get_conversation_messages(
        conversation_id: str,
        user_id: str,
        db: AsyncSession,
    ) -> list[dict]:
        """Fetch message history for a conversation."""
        c_id = _to_uuid(conversation_id)
        u_id = _to_uuid(user_id)

        conv = (await db.execute(
            select(AIConversation).where(AIConversation.id == c_id, AIConversation.user_id == u_id)
        )).scalar_one_or_none()

        if not conv:
            raise NotFoundException(f"Conversation {conversation_id} not found")

        stmt = (
            select(AIConversationMessage)
            .where(AIConversationMessage.conversation_id == c_id)
            .order_by(AIConversationMessage.created_at)
        )
        messages = (await db.execute(stmt)).scalars().all()

        return [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "metadata": m.msg_metadata,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ]
