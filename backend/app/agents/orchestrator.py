"""Agent Orchestrator for multi-turn career planning and autonomous execution."""
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.ai.base import AIProvider
from app.models.agent_task import AgentTask
from app.models.ai_conversation import AIConversation
from app.models.ai_conversation_message import AIConversationMessage
from .tools import (
    application_tracking_tool,
    cover_letter_tool,
    interview_prep_tool,
    job_matching_tool,
    job_search_tool,
    resume_analysis_tool,
    resume_tailoring_tool,
    save_job_tool,
)

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


class AgentResponse:
    """Standardized response from the agent orchestrator."""

    def __init__(
        self,
        content: str,
        tool: Optional[str] = None,
        tool_result: Optional[dict] = None,
        task_id: Optional[str] = None,
        requires_approval: bool = False,
        status: str = "completed",
    ):
        self.content = content
        self.tool = tool
        self.tool_result = tool_result
        self.task_id = task_id
        self.requires_approval = requires_approval
        self.status = status

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "tool": self.tool,
            "tool_result": self.tool_result,
            "task_id": self.task_id,
            "requires_approval": self.requires_approval,
            "status": self.status,
        }


class AgentOrchestrator:
    """Manages conversation state, intent classification, and tool invocation."""

    def __init__(self, ai_provider: AIProvider, db: AsyncSession, user_id: str):
        self.ai = ai_provider
        self.db = db
        self.user_id = str(user_id)
        self.tools = {
            "resume_analysis": resume_analysis_tool,
            "job_search": job_search_tool,
            "job_match": job_matching_tool,
            "save_job": save_job_tool,
            "track_application": application_tracking_tool,
            "tailor_resume": resume_tailoring_tool,
            "cover_letter": cover_letter_tool,
            "interview_prep": interview_prep_tool,
        }

    async def process_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> AgentResponse:
        """Process incoming user prompt, invoke appropriate tools, and record session history."""
        u_id = _to_uuid(self.user_id)

        # 1. Ensure conversation exists
        conv = None
        if conversation_id:
            c_id = _to_uuid(conversation_id)
            conv = (await self.db.execute(
                select(AIConversation).where(AIConversation.id == c_id, AIConversation.user_id == u_id)
            )).scalar_one_or_none()

        if not conv:
            conv = AIConversation(
                user_id=u_id,
                title=(message[:35] + "...") if len(message) > 35 else message,
            )
            self.db.add(conv)
            await self.db.commit()
            await self.db.refresh(conv)

        # 2. Record User Message
        user_msg = AIConversationMessage(
            conversation_id=conv.id,
            user_id=u_id,
            role="user",
            content=message,
        )
        self.db.add(user_msg)
        await self.db.commit()

        # 3. Fetch recent history
        hist_stmt = (
            select(AIConversationMessage)
            .where(AIConversationMessage.conversation_id == conv.id)
            .order_by(desc(AIConversationMessage.created_at))
            .limit(10)
        )
        raw_msgs = (await self.db.execute(hist_stmt)).scalars().all()
        history = [
            {"role": m.role, "content": m.content}
            for m in reversed(raw_msgs)
        ]

        # 4. Understand intent & select tool
        intent = await self._understand_intent(message, history)
        tool_name = intent.get("tool", "general_chat")
        parameters = intent.get("parameters", {})
        requires_approval = intent.get("requires_approval", False)
        friendly_resp = intent.get("friendly_response", "")

        # Sensitive actions check (submitting apps, external emails)
        if requires_approval:
            task = AgentTask(
                user_id=u_id,
                conversation_id=conv.id,
                task_type=tool_name,
                status="awaiting_approval",
                input_data=parameters,
                requires_approval=True,
            )
            self.db.add(task)
            await self.db.commit()
            await self.db.refresh(task)

            approval_msg = (
                f"{friendly_resp}\n\n⚠️ **Action Requires Your Approval:**\n"
                f"Action `{tool_name}` with parameters: `{json.dumps(parameters)}`.\n"
                f"Would you like me to proceed with this action?"
            )

            asst_msg = AIConversationMessage(
                conversation_id=conv.id,
                user_id=u_id,
                role="assistant",
                content=approval_msg,
                msg_metadata={"task_id": str(task.id), "status": "awaiting_approval"},
            )
            self.db.add(asst_msg)
            await self.db.commit()

            return AgentResponse(
                content=approval_msg,
                tool=tool_name,
                task_id=str(task.id),
                requires_approval=True,
                status="awaiting_approval",
            )

        # 5. Execute tool if designated
        tool_output = None
        final_text = friendly_resp

        if tool_name in self.tools:
            try:
                tool_output = await self._execute_tool(tool_name, parameters)
                if not final_text or tool_name != "general_chat":
                    # Generate a natural language summary with the AI provider
                    final_text = self._format_tool_response(tool_name, tool_output, friendly_resp)
            except Exception as e:
                logger.error("Error executing tool %s: %s", tool_name, e)
                final_text = f"I attempted to execute {tool_name}, but encountered an error: {str(e)}"
                tool_output = {"error": str(e)}
        else:
            # Fallback to chat completion if general_chat or unrecognized tool
            if not final_text:
                final_text = self.ai.chat(history, context=context or {})

        # 6. Save assistant message
        asst_msg = AIConversationMessage(
            conversation_id=conv.id,
            user_id=u_id,
            role="assistant",
            content=final_text,
            msg_metadata={"tool": tool_name, "tool_result": tool_output},
        )
        self.db.add(asst_msg)
        await self.db.commit()

        return AgentResponse(
            content=final_text,
            tool=tool_name if tool_name != "general_chat" else None,
            tool_result=tool_output,
            status="completed",
        )

    async def _understand_intent(self, message: str, history: list) -> dict:
        """Classify user intent into one of the specialized agent tools."""
        system_prompt = (
            "You are an AI career assistant. Analyze the user message and determine:\n"
            "1. Which tool to use: job_search, job_match, resume_analysis, save_job, track_application, "
            "tailor_resume, cover_letter, interview_prep, general_chat\n"
            "2. Extract parameters\n"
            "3. Whether this requires user approval (true only for: submitting applications, sharing data, sending external emails)\n"
            "Return JSON: {tool, parameters, requires_approval, friendly_response}"
        )

        user_content = f"Recent History:\n{json.dumps(history[-4:], indent=2)}\n\nNew Message: {message}"

        # Heuristic fast-path for demo / offline reliability
        msg_l = message.lower()
        if "tailor resume" in msg_l or "optimize resume" in msg_l:
            return {
                "tool": "tailor_resume",
                "parameters": {},
                "requires_approval": False,
                "friendly_response": "I'll optimize and tailor your resume for this target job.",
            }
        elif "cover letter" in msg_l or "write a cover letter" in msg_l:
            tone = "enthusiastic" if "enthusiastic" in msg_l else ("concise" if "concise" in msg_l else "professional")
            return {
                "tool": "cover_letter",
                "parameters": {"tone": tone},
                "requires_approval": False,
                "friendly_response": f"Generating a personalized {tone} cover letter based on your credentials.",
            }
        elif "interview prep" in msg_l or "interview questions" in msg_l:
            return {
                "tool": "interview_prep",
                "parameters": {},
                "requires_approval": False,
                "friendly_response": "Preparing comprehensive technical and behavioral interview practice questions.",
            }
        elif "submit application" in msg_l or "send application" in msg_l or "apply for me" in msg_l:
            return {
                "tool": "track_application",
                "parameters": {"action": "create", "status": "Applied"},
                "requires_approval": True,
                "friendly_response": "I have drafted the application submission.",
            }
        elif "find jobs" in msg_l or "search jobs" in msg_l or "job search" in msg_l:
            return {
                "tool": "job_search",
                "parameters": {"query": "", "location": ""},
                "requires_approval": False,
                "friendly_response": "Searching for high-match opportunities in our database.",
            }

        # Model-based classification if available
        try:
            raw = self.ai.chat(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                context={},
            )
            # Clean JSON
            clean = raw.strip()
            if clean.startswith("```"):
                clean = re.sub(r"^```(?:json)?\s*", "", clean, flags=re.IGNORECASE)
                clean = re.sub(r"\s*```$", "", clean)
            return json.loads(clean)
        except Exception:
            return {
                "tool": "general_chat",
                "parameters": {},
                "requires_approval": False,
                "friendly_response": "",
            }

    async def _execute_tool(self, tool_name: str, params: dict) -> dict:
        """Call mapped tool function with appropriate arguments."""
        tool_fn = self.tools.get(tool_name)
        if not tool_fn:
            raise ValueError(f"Unknown tool: {tool_name}")

        if tool_name == "resume_analysis":
            r_id = params.get("resume_id")
            return await tool_fn(user_id=self.user_id, resume_id=r_id, db=self.db)
        elif tool_name == "job_search":
            return await tool_fn(
                query=params.get("query", ""),
                location=params.get("location", ""),
                filters=params.get("filters", {}),
                user_id=self.user_id,
                db=self.db,
            )
        elif tool_name == "job_match":
            return await tool_fn(
                user_id=self.user_id,
                job_id=params.get("job_id"),
                resume_id=params.get("resume_id"),
                db=self.db,
            )
        elif tool_name == "save_job":
            return await tool_fn(
                user_id=self.user_id,
                job_id=params.get("job_id"),
                notes=params.get("notes", ""),
                db=self.db,
            )
        elif tool_name == "track_application":
            return await tool_fn(
                user_id=self.user_id,
                action=params.get("action", "list"),
                application_id=params.get("application_id"),
                data=params.get("data", {}),
                db=self.db,
            )
        elif tool_name == "tailor_resume":
            return await tool_fn(
                user_id=self.user_id,
                job_id=params.get("job_id"),
                resume_id=params.get("resume_id"),
                db=self.db,
            )
        elif tool_name == "cover_letter":
            return await tool_fn(
                user_id=self.user_id,
                job_id=params.get("job_id"),
                resume_id=params.get("resume_id"),
                tone=params.get("tone", "professional"),
                db=self.db,
            )
        elif tool_name == "interview_prep":
            return await tool_fn(
                user_id=self.user_id,
                job_id=params.get("job_id"),
                db=self.db,
            )

        raise ValueError(f"Unhandled tool execution: {tool_name}")

    def _format_tool_response(self, tool_name: str, tool_output: dict, initial_resp: str) -> str:
        """Format tool output into a friendly response."""
        prefix = f"{initial_resp}\n\n" if initial_resp else ""
        if tool_name == "job_search":
            count = len(tool_output) if isinstance(tool_output, list) else 0
            return f"{prefix}🔍 Found **{count} matching jobs**. Here are the top opportunities aligned with your profile."
        elif tool_name == "job_match":
            score = tool_output.get("overall_score", 0)
            explanation = tool_output.get("explanation", "")
            return f"{prefix}🎯 Match Analysis: **{score}% Overall Fit**\n\n{explanation}"
        elif tool_name == "cover_letter":
            content = tool_output.get("content", "")
            return f"{prefix}📄 **Generated Cover Letter:**\n\n{content}"
        elif tool_name == "tailor_resume":
            return f"{prefix}✨ **Resume Tailored!** Highlighted your most relevant technical accomplishments and integrated targeted industry keywords."
        elif tool_name == "interview_prep":
            prep = tool_output.get("prep_data", {})
            tech_q = prep.get("technical_questions", [])[:2]
            return f"{prefix}🎙️ **Interview Prep Ready!**\nKey questions to review:\n" + "\n".join(f"- {q}" for q in tech_q)
        elif tool_name == "save_job":
            return f"{prefix}💾 Job saved to your tracker!"
        elif tool_name == "resume_analysis":
            overall = tool_output.get("score", {}).get("overall_score", 80)
            return f"{prefix}📊 Resume analysis complete! Overall score: **{overall}/100**."
        return f"{prefix}{json.dumps(tool_output, indent=2)}"

    async def approve_action(self, task_id: str) -> dict:
        """Execute a previously pending task after the user grants explicit approval."""
        t_id = _to_uuid(task_id)
        u_id = _to_uuid(self.user_id)

        stmt = select(AgentTask).where(
            AgentTask.id == t_id,
            AgentTask.user_id == u_id,
            AgentTask.status == "awaiting_approval",
        )
        task = (await self.db.execute(stmt)).scalar_one_or_none()

        if not task:
            return {"error": f"Task {task_id} not found or not awaiting approval."}

        task.status = "running"
        await self.db.commit()

        try:
            result = await self._execute_tool(task.task_type, task.input_data)
            task.status = "completed"
            task.output_data = result if isinstance(result, dict) else {"result": result}
            task.approved_at = datetime.now(timezone.utc)
            await self.db.commit()
            return {"success": True, "status": "completed", "result": result}
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            await self.db.commit()
            return {"success": False, "status": "failed", "error": str(e)}
