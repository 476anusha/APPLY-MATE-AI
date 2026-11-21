"""Abstract AI provider base class."""
from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """Abstract base class for all AI providers.

    Every concrete provider must implement every method defined here.
    Methods must never fabricate information; they may only
    transform/extract/reformat what is supplied in the input.
    """

    # ------------------------------------------------------------------
    # Resume operations
    # ------------------------------------------------------------------

    @abstractmethod
    def analyze_resume(self, text: str) -> dict:
        """Parse raw resume text and return structured data.

        Args:
            text: Raw text extracted from a PDF/DOCX resume.

        Returns:
            {
                full_name, email, phone, summary,
                education: [],
                experience: [],
                projects: [],
                technical_skills: [],
                soft_skills: [],
                certifications: [],
                achievements: [],
            }
        """

    @abstractmethod
    def score_resume(self, extracted_data: dict) -> dict:
        """Score a parsed resume and return improvement suggestions.

        Args:
            extracted_data: Output of analyze_resume().

        Returns:
            {
                overall_score (0-100),
                ats_score (0-100),
                section_scores: {summary, education, experience, projects, skills, formatting},
                strengths: [],
                weaknesses: [],
                suggestions: [],
                missing_keywords: [],
                disclaimer: str,
            }
        """

    @abstractmethod
    def tailor_resume(self, resume_data: dict, job_description: str) -> dict:
        """Rewrite resume sections to better match a job description.

        CRITICAL: Never invent experience, degrees, or skills.

        Args:
            resume_data: Structured resume (output of analyze_resume).
            job_description: Full JD text.

        Returns:
            {
                updated_sections: {summary, experience: [], skills: []},
                keyword_additions: [],
                optimization_notes: [],
            }
        """

    # ------------------------------------------------------------------
    # Matching
    # ------------------------------------------------------------------

    @abstractmethod
    def match_job(self, resume_data: dict, job_description: str) -> dict:
        """Calculate match score between a resume and a job description.

        The numerical scores are computed algorithmically before calling
        the LLM; the LLM only explains the result.

        Args:
            resume_data: Structured resume.
            job_description: Full JD text.

        Returns:
            {
                overall_score,
                skill_score,
                experience_score,
                education_score,
                keyword_score,
                matched_skills: [],
                missing_skills: [],
                explanation: str,
                recommendations: [],
            }
        """

    # ------------------------------------------------------------------
    # Content generation
    # ------------------------------------------------------------------

    @abstractmethod
    def generate_cover_letter(
        self,
        resume_data: dict,
        job_data: dict,
        tone: str = "professional",
    ) -> str:
        """Generate a personalised cover letter.

        Args:
            resume_data: Structured resume.
            job_data: Job details dict.
            tone: 'professional' | 'enthusiastic' | 'concise' | 'creative'

        Returns:
            Cover letter as plain formatted text.
        """

    @abstractmethod
    def generate_interview_questions(
        self, job_data: dict, resume_data: dict
    ) -> dict:
        """Generate interview preparation material.

        Args:
            job_data: Job details dict.
            resume_data: Structured resume.

        Returns:
            {
                technical_questions: [],
                hr_questions: [],
                behavioral_questions: [],
                coding_challenges: [],
                suggested_answers: {question: answer},
                tips: [],
            }
        """

    # ------------------------------------------------------------------
    # Agent / chat
    # ------------------------------------------------------------------

    @abstractmethod
    def chat(self, messages: list, context: dict) -> str:
        """Multi-turn conversational chat.

        Args:
            messages: List of {role: 'user'|'assistant', content: str}.
            context: Optional extra context (user profile, resume, etc.).

        Returns:
            Assistant reply as plain text.
        """

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    @abstractmethod
    def generate_weekly_report(self, user_stats: dict) -> str:
        """Generate a human-readable weekly career progress report.

        Args:
            user_stats: Aggregated stats for the week.

        Returns:
            Formatted report as plain text / markdown.
        """
