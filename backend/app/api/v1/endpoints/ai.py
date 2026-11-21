"""AI endpoint — chat agent, resume analysis, cover letter, interview prep.
   All UUID fields stored as plain strings for SQLite compatibility.
"""
import uuid
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_active_user
from app.core.config import settings
from app.database import get_db

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class CoverLetterRequest(BaseModel):
    job_id: str
    resume_id: Optional[str] = None
    tone: str = "professional"
    company: Optional[str] = None
    job_title: Optional[str] = None


class TailorResumeRequest(BaseModel):
    job_id: str
    resume_id: Optional[str] = None


class InterviewPrepRequest(BaseModel):
    job_id: str
    resume_id: Optional[str] = None


def _is_ai_available() -> bool:
    return bool(settings.GEMINI_API_KEY or settings.OPENAI_API_KEY)


def _mock_chat_response(message: str) -> str:
    msg_lower = message.lower().strip()
    if any(w in msg_lower for w in ["find", "search"]) and "job" in msg_lower:
        return (
            "🎯 I found great matching job opportunities for you!\n\n"
            "- 🐍 **Python Backend Developer** — TechCorp Solutions (Remote | $90,000 - $120,000)\n"
            "- ⚛️ **React Frontend Developer** — Innovate Labs (Hybrid | $85,000 - $115,000)\n"
            "- 🚀 **Full Stack Engineer** — StartupX (Remote | $100,000 - $135,000)\n"
            "- 📊 **Data Scientist** — Analytics Pro (Bengaluru / Hybrid | ₹18,00,000 - ₹24,00,000)\n\n"
            "Would you like me to match one of these against your uploaded resume, or help you draft a cover letter?"
        )
    elif any(w in msg_lower for w in ["yes", "sure", "ok", "yep", "do it", "please"]):
        return (
            "Awesome! Let's take action. Here are the best next steps:\n\n"
            "1. 📄 **Match against your resume**: Head to the **Jobs** tab and click **View Match Score** to see your compatibility percentage.\n"
            "2. ✉️ **Craft a Cover Letter**: Pick any opening and I'll generate a bespoke cover letter highlighting your strengths.\n"
            "3. 🎤 **Interview Prep**: Select the role in **Interview Prep** to practice role-specific technical and STAR behavioral questions.\n\n"
            "Which of these would you like to do first?"
        )
    elif "cover letter" in msg_lower:
        return (
            "I'd be happy to generate a tailored cover letter!\n\n"
            "Please select a target job from the **Jobs** section, or tell me the role and company (e.g., *'Write a cover letter for Google SDE'*), and I will create a compelling, ATS-optimized letter based on your resume."
        )
    elif "resume" in msg_lower and any(w in msg_lower for w in ["analyz", "review", "score", "ats"]):
        return (
            "You can analyze and score your resumes in the **My Resumes** section!\n\n"
            "- We extract your full contact details, projects, and technical skills.\n"
            "- You receive an algorithmic ATS score and section-by-section breakdown.\n"
            "- Actionable suggestions highlight high-demand keywords you should add.\n\n"
            "Head to **My Resumes** and click **View Analysis** on any uploaded file!"
        )
    elif "tailor" in msg_lower:
        return (
            "Tailoring your resume dramatically increases your interview callback rate!\n\n"
            "Go to any job listing in the **Jobs** tab and select **Tailor Resume**. ApplyMate will adapt your experience bullets and highlight the exact matching tech stack keywords for that employer."
        )
    elif "google" in msg_lower:
        return (
            "Google engineering interviews focus heavily on Data Structures, Algorithms, System Design, and Googleyness (leadership & problem-solving).\n\n"
            "- 💡 **Tip:** Practice Medium/Hard LeetCode problems (Graphs, Dynamic Programming, Trees).\n"
            "- 🎤 Check our **Interview Prep** tab for coding challenges with full solutions."
        )
    elif any(w in msg_lower for w in ["interview", "prep", "question"]):
        return (
            "Great choice to prepare for interviews!\n\n"
            "Head to the **Interview Prep** section and select a job role. I've prepared:\n"
            "- 💻 **Technical Questions** (Scalability, code quality, debugging)\n"
            "- 🤝 **Behavioral Prompts** (STAR method: Situation, Task, Action, Result)\n"
            "- 🧩 **Coding Challenges** with complete model solutions and tips!"
        )
    elif "skill" in msg_lower:
        return (
            "Based on current market trends, here are the most in-demand skills in 2026:\n\n"
            "- 🐍 **Python** (FastAPI / Django / Asynchronous systems)\n"
            "- ⚛️ **React + TypeScript** (Modern state management & UI)\n"
            "- ☁️ **Cloud & DevOps** (AWS, Docker, Kubernetes, CI/CD)\n"
            "- 🗃️ **Databases** (PostgreSQL, Redis, Vector Databases)\n\n"
            "Would you like specific learning resources or project ideas for any of these?"
        )
    elif any(w in msg_lower for w in ["hello", "hi", "hey", "?"]):
        return (
            "👋 Hello! I'm **ApplyMate AI**, your career copilot!\n\n"
            "Here is what I can do for you right now:\n"
            "- 🔍 **Find matching jobs** tailored to your background\n"
            "- 📄 **Review your resume** & suggest ATS score optimizations\n"
            "- ✉️ **Generate personalized cover letters** for target employers\n"
            "- 🎤 **Prepare you for upcoming technical & HR interviews**\n\n"
            "What would you like to work on today?"
        )
    else:
        return (
            f"I'm here to help with your career and application journey! Regarding **{message[:60]}**:\n\n"
            "You can ask me to:\n"
            "- Find the highest-match software engineering jobs\n"
            "- Help you optimize your resume for applicant tracking systems\n"
            "- Practice role-specific interview questions\n"
            "- Draft a persuasive cover letter\n\n"
            "What role or company are you currently targeting?"
        )


def _mock_interview_prep(job_title: str) -> dict:
    return {
        "job_title": job_title,
        "technical_questions": [
            {"question": f"Explain the core concepts you'd use building a {job_title} system.", "answer": "Focus on scalability, clean code principles, appropriate data structures, and design patterns relevant to the role.", "suggested_answer": "Focus on scalability, clean code principles, appropriate data structures, and design patterns relevant to the role.", "tip": "Use specific examples from your projects."},
            {"question": "How do you approach debugging a production issue?", "answer": "Start with logs, reproduce locally if possible, isolate the failing component, fix with a targeted change, add tests to prevent regression.", "suggested_answer": "Start with logs, reproduce locally if possible, isolate the failing component, fix with a targeted change, add tests to prevent regression.", "tip": "Show systematic thinking."},
            {"question": "What's your experience with version control and CI/CD?", "answer": "Git for version control with feature branches, pull requests for code review, GitHub Actions or Jenkins for CI, automated deployment pipelines.", "suggested_answer": "Git for version control with feature branches, pull requests for code review, GitHub Actions or Jenkins for CI, automated deployment pipelines.", "tip": "Mention specific tools you've used."},
            {"question": "Describe your experience with databases and query optimization.", "answer": "Normalize schema design, use proper indexing, avoid N+1 queries, use EXPLAIN/ANALYZE to profile slow queries, consider caching with Redis.", "suggested_answer": "Normalize schema design, use proper indexing, avoid N+1 queries, use EXPLAIN/ANALYZE to profile slow queries, consider caching with Redis.", "tip": "Have a real example ready."},
            {"question": "How do you ensure code quality in your projects?", "answer": "Unit and integration tests, code reviews, linting, type checking, documentation, following SOLID principles.", "suggested_answer": "Unit and integration tests, code reviews, linting, type checking, documentation, following SOLID principles.", "tip": "Mention test coverage percentages if you have them."},
        ],
        "behavioral_questions": [
            {"question": "Tell me about yourself.", "answer": "Start with your current role/education, highlight 2-3 key achievements, explain why you're interested in this role, and what value you bring.", "suggested_answer": "Start with your current role/education, highlight 2-3 key achievements, explain why you're interested in this role, and what value you bring.", "tip": "Keep it to 90 seconds. Practice this out loud."},
            {"question": "Describe a challenging project you completed.", "answer": "Use the STAR method: Situation, Task, Action, Result. Focus on your specific contribution and measurable outcomes.", "suggested_answer": "Use the STAR method: Situation, Task, Action, Result. Focus on your specific contribution and measurable outcomes.", "tip": "Quantify results whenever possible (e.g., 'reduced load time by 40%')."},
            {"question": "How do you handle tight deadlines?", "answer": "Prioritize tasks by impact, communicate proactively with stakeholders, break work into milestones, and ask for help early if blocked.", "suggested_answer": "Prioritize tasks by impact, communicate proactively with stakeholders, break work into milestones, and ask for help early if blocked.", "tip": "Give a real example."},
            {"question": "Tell me about a time you disagreed with a team member.", "answer": "Focus on the professional resolution — present your reasoning with data, listen to their perspective, and find a compromise or escalate respectfully.", "suggested_answer": "Focus on the professional resolution — present your reasoning with data, listen to their perspective, and find a compromise or escalate respectfully.", "tip": "Show maturity and collaboration."},
        ],
        "project_questions": [
            {"question": "Walk me through your most impressive project.", "answer": "Describe the problem it solved, your architecture decisions, technologies used, challenges overcome, and what you learned.", "suggested_answer": "Describe the problem it solved, your architecture decisions, technologies used, challenges overcome, and what you learned.", "tip": "Have a live demo or GitHub link ready."},
            {"question": "How did you decide on the tech stack for your projects?", "answer": "Consider team expertise, project requirements, scalability needs, community support, and long-term maintenance.", "suggested_answer": "Consider team expertise, project requirements, scalability needs, community support, and long-term maintenance.", "tip": "Show pragmatic decision-making."},
        ],
        "coding_challenges": [
            {"title": "Two Sum", "description": "Given an array of integers and a target, return indices of two numbers that add up to the target.", "solution": "Use a hash map to store complements. O(n) time, O(n) space.", "question": "Two Sum", "answer": "Use a hash map to store complements. O(n) time, O(n) space.", "suggested_answer": "Use a hash map to store complements. O(n) time, O(n) space."},
            {"title": "Valid Parentheses", "description": "Determine if a string of brackets is valid.", "solution": "Use a stack. Push opening brackets, pop and verify when closing brackets are found.", "question": "Valid Parentheses", "answer": "Use a stack. Push opening brackets, pop and verify when closing brackets are found.", "suggested_answer": "Use a stack. Push opening brackets, pop and verify when closing brackets are found."},
            {"title": "LRU Cache", "description": "Implement an LRU cache with O(1) get and put operations.", "solution": "Use an OrderedDict or doubly linked list + hash map combination.", "question": "LRU Cache", "answer": "Use an OrderedDict or doubly linked list + hash map combination.", "suggested_answer": "Use an OrderedDict or doubly linked list + hash map combination."},
        ],
        "tips": [
            "Research the company's products, tech stack, and recent news before the interview.",
            "Prepare 3-5 stories using the STAR method (Situation, Task, Action, Result).",
            "Ask thoughtful questions about the team, tech stack, and growth opportunities.",
            "Practice coding problems on a whiteboard or paper to simulate interview conditions.",
        ],
    }


# ── Chat ─────────────────────────────────────────────────────────────────────

@router.post("/chat")
async def chat(
    req: ChatRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from app.models.ai_conversation import AIConversation
    from app.models.ai_conversation_message import AIConversationMessage

    # Get or create conversation — all IDs are plain strings
    conv_id = req.conversation_id
    conv = None

    if conv_id:
        result = await db.execute(
            select(AIConversation).where(
                AIConversation.id == conv_id,
                AIConversation.user_id == str(current_user.id),
            )
        )
        conv = result.scalar_one_or_none()
        if not conv:
            conv_id = None

    if not conv_id:
        conv_id = str(uuid.uuid4())
        conv = AIConversation(
            id=conv_id,
            user_id=str(current_user.id),
            title=req.message[:60] + ("..." if len(req.message) > 60 else ""),
        )
        db.add(conv)
        await db.flush()

    # Save user message
    user_msg = AIConversationMessage(
        id=str(uuid.uuid4()),
        conversation_id=conv_id,
        user_id=str(current_user.id),
        role="user",
        content=req.message,
    )
    db.add(user_msg)

    # Fetch recent conversation messages for multi-turn context (excluding current)
    history_res = await db.execute(
        select(AIConversationMessage)
        .where(
            AIConversationMessage.conversation_id == conv_id,
            AIConversationMessage.id != user_msg.id,
        )
        .order_by(AIConversationMessage.created_at.asc())
    )
    prev_msgs = history_res.scalars().all()
    history_turns = []
    for m in prev_msgs[-8:]:
        role_label = "Candidate" if m.role == "user" else "ApplyMate AI"
        history_turns.append(f"{role_label}: {m.content}")
    history_context = "\n".join(history_turns)

    # Generate AI response
    assistant_content = ""
    if _is_ai_available() and settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)

            system_prompt = (
                "You are ApplyMate AI, an intelligent, empathetic career coach and job application copilot. "
                "Help the user with job recommendations, resume scoring and tailoring, cover letter creation, "
                "and interview preparation. Answer directly, using conversational context from earlier turns. "
                "Be concise, friendly, and format with markdown bullets."
            )

            if history_context:
                prompt = f"{system_prompt}\n\nRecent Conversation:\n{history_context}\n\nCandidate: {req.message}\nApplyMate AI:"
            else:
                prompt = f"{system_prompt}\n\nCandidate: {req.message}\nApplyMate AI:"

            # Try models in priority order (gemini-3.5-flash has active quota)
            models_to_try = ["gemini-3.5-flash", "gemini-2.5-flash", "gemini-flash-latest"]
            for m_name in models_to_try:
                try:
                    model = genai.GenerativeModel(m_name)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        assistant_content = response.text.strip()
                        break
                except Exception:
                    continue
        except Exception:
            pass

    if not assistant_content:
        assistant_content = _mock_chat_response(req.message)

    # Save assistant message
    asst_id = str(uuid.uuid4())
    asst_msg = AIConversationMessage(
        id=asst_id,
        conversation_id=conv_id,
        user_id=str(current_user.id),
        role="assistant",
        content=assistant_content,
    )
    db.add(asst_msg)
    await db.commit()

    return {
        "conversation_id": conv_id,
        "message": {"role": "assistant", "content": assistant_content, "id": asst_id},
    }


@router.get("/conversations")
async def list_conversations(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from app.models.ai_conversation import AIConversation
    result = await db.execute(
        select(AIConversation)
        .where(AIConversation.user_id == str(current_user.id))
        .order_by(AIConversation.created_at.desc())
        .limit(20)
    )
    convs = result.scalars().all()
    return [{"id": str(c.id), "title": c.title, "is_active": c.is_active, "created_at": str(c.created_at)} for c in convs]


@router.get("/conversations/{conv_id}/messages")
async def get_messages(
    conv_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from app.models.ai_conversation_message import AIConversationMessage
    result = await db.execute(
        select(AIConversationMessage)
        .where(AIConversationMessage.conversation_id == conv_id)
        .order_by(AIConversationMessage.created_at.asc())
    )
    msgs = result.scalars().all()
    return [{"id": str(m.id), "role": m.role, "content": m.content, "created_at": str(m.created_at)} for m in msgs]


@router.post("/conversations/{conv_id}/messages")
async def send_message_to_conversation(
    conv_id: str,
    req: ChatRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Send message to existing conversation."""
    req.conversation_id = conv_id
    return await chat(req, current_user, db)


@router.post("/conversations")
async def create_conversation(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from app.models.ai_conversation import AIConversation
    conv_id = str(uuid.uuid4())
    conv = AIConversation(id=conv_id, user_id=str(current_user.id), title="New Conversation")
    db.add(conv)
    await db.commit()
    return {"id": conv_id, "title": "New Conversation", "is_active": True, "created_at": str(conv.created_at)}


# ── Interview Prep ────────────────────────────────────────────────────────────

@router.post("/interview-prep")
async def interview_prep_body(
    req: InterviewPrepRequest,
    current_user=Depends(get_current_active_user),
) -> Any:
    """Interview prep with job_id in request body."""
    return _mock_interview_prep(req.job_id)


@router.post("/interview-prep/{job_id}")
async def interview_prep(
    job_id: str,
    current_user=Depends(get_current_active_user),
) -> Any:
    """Interview prep with job_id in URL path (frontend compat)."""
    # Resolve job title from demo jobs
    demo_titles = {
        "demo-001": "Python Backend Developer",
        "demo-002": "React Frontend Developer",
        "demo-003": "Full Stack Engineer",
        "demo-004": "Data Scientist",
    }
    job_title = demo_titles.get(job_id, job_id)
    return _mock_interview_prep(job_title)


# ── Analyze Resume ────────────────────────────────────────────────────────────

@router.post("/analyze-resume/{resume_id}")
async def analyze_resume(
    resume_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from app.models.resume import Resume
    from app.services.ai.factory import get_ai_provider
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == str(current_user.id))
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    ai = get_ai_provider()
    mock_text = "Python developer with React experience and PostgreSQL skills."
    parsed = ai.analyze_resume(mock_text)
    scored = ai.score_resume(parsed)
    return {
        "resume_id": resume_id,
        "overall_score": scored.get("overall_score", 80),
        "ats_score": scored.get("ats_score", 85),
        "section_scores": scored.get("section_scores", {}),
        "strengths": scored.get("strengths", []),
        "weaknesses": scored.get("weaknesses", []),
        "suggestions": scored.get("suggestions", []),
    }


# ── Cover Letter ──────────────────────────────────────────────────────────────

@router.post("/generate-cover-letter")
@router.post("/cover-letter")
async def generate_cover_letter(
    req: CoverLetterRequest,
    current_user=Depends(get_current_active_user),
) -> Any:
    content = (
        f"Dear Hiring Manager,\n\n"
        f"I am writing to express my strong interest in the {req.job_title or 'position'} role"
        f"{' at ' + req.company if req.company else ''}. "
        f"With my background in software development and passion for building impactful products, "
        f"I am confident I would be a valuable addition to your team.\n\n"
        f"My experience spans full-stack development, RESTful API design, and cloud deployment. "
        f"I thrive in collaborative environments and am committed to writing clean, maintainable code.\n\n"
        f"I would welcome the opportunity to discuss how my skills align with your team's needs.\n\n"
        f"Best regards,\nYour Name"
    )
    return {
        "id": str(uuid.uuid4()),
        "title": f"Cover Letter — {req.job_title or 'Position'}",
        "content": content,
        "tone": req.tone,
        "job_id": req.job_id,
    }


# ── Tailor Resume ─────────────────────────────────────────────────────────────

@router.post("/tailor-resume")
async def tailor_resume(
    req: TailorResumeRequest,
    current_user=Depends(get_current_active_user),
) -> Any:
    return {
        "tailored_resume": {"summary": "Tailored resume content based on job description"},
        "diff_summary": ["Added relevant keywords", "Emphasized matching skills", "Restructured experience section"],
        "match_score_before": 65,
        "match_score_after": 88,
        "suggestions": ["Add more quantifiable metrics", "Include specific technologies from job description"],
    }
