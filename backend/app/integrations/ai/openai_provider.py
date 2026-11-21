"""OpenAI AI Provider implementation for ApplyMate AI."""
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

from .base import AIProvider

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    OpenAI = None
    HAS_OPENAI = False


def _clean_json_response(raw_text: str) -> str:
    """Extract and sanitize JSON from model output."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


class OpenAIProvider(AIProvider):
    """OpenAI API implementation (fallback/secondary provider)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gpt-4o-mini",
        pro_model_name: str = "gpt-4o",
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model_name = model_name
        self.pro_model_name = pro_model_name
        self.client = None

        if HAS_OPENAI and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning("Failed to initialize OpenAI client: %s", e)

    def _call_openai(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        is_json: bool = False,
        use_pro: bool = False,
    ) -> str:
        """Helper to invoke OpenAI chat completion."""
        if not HAS_OPENAI or not self.client:
            raise RuntimeError("OpenAI is not configured or openai package is missing.")

        model = self.pro_model_name if use_pro else self.model_name
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": 0.2,
        }
        if is_json:
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        return choice.message.content or ("{}" if is_json else "")

    # ------------------------------------------------------------------
    # 1. Resume Parsing
    # ------------------------------------------------------------------
    def analyze_resume(self, text: str) -> dict:
        system_instruction = (
            "You are an expert resume parser. Extract all information in valid JSON format. "
            "NEVER make up information — only extract what is truthfully present in the input text."
        )
        prompt = f"""Extract all details from the resume into this exact JSON schema:
{{
  "full_name": "Full Name",
  "email": "email@example.com",
  "phone": "+1-555-0199",
  "summary": "Professional summary",
  "education": [
    {{
      "institution": "University Name",
      "degree": "Degree and Major",
      "field_of_study": "Field",
      "start_date": "YYYY",
      "end_date": "YYYY or Present",
      "gpa": ""
    }}
  ],
  "experience": [
    {{
      "company": "Company Name",
      "title": "Job Title",
      "location": "Location",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or Present",
      "is_current": false,
      "bullets": ["Bullet 1"]
    }}
  ],
  "projects": [
    {{
      "title": "Project Name",
      "description": "Short description",
      "technologies": ["Tech 1"],
      "link": ""
    }}
  ],
  "technical_skills": ["Skill 1"],
  "soft_skills": ["Skill 1"],
  "certifications": [],
  "achievements": []
}}

Resume text:
\"\"\"
{text}
\"\"\"
"""
        raw_res = self._call_openai(prompt, system_instruction=system_instruction, is_json=True)
        try:
            return json.loads(_clean_json_response(raw_res))
        except Exception:
            return {
                "full_name": "Extracted Candidate",
                "email": "",
                "phone": "",
                "summary": text[:200],
                "education": [],
                "experience": [],
                "projects": [],
                "technical_skills": [],
                "soft_skills": [],
                "certifications": [],
                "achievements": [],
            }

    # ------------------------------------------------------------------
    # 2. Resume Scoring
    # ------------------------------------------------------------------
    def score_resume(self, extracted_data: dict) -> dict:
        system_instruction = (
            "You are an ATS and resume quality expert. Analyze this resume data and return scores, "
            "strengths, weaknesses, suggestions, and missing keywords in valid JSON format."
        )
        prompt = f"""Analyze this parsed resume and return scores (0-100) and suggestions:
{json.dumps(extracted_data, indent=2)}

Format:
{{
  "overall_score": 75,
  "ats_score": 78,
  "section_scores": {{
    "summary": 70,
    "education": 80,
    "experience": 75,
    "projects": 70,
    "skills": 85,
    "formatting": 80
  }},
  "strengths": ["Clear impact"],
  "weaknesses": ["Generic summary"],
  "suggestions": ["Add measurable metrics"],
  "missing_keywords": ["CI/CD", "Docker"],
  "disclaimer": "This is an estimated optimization score, not an actual employer ATS result."
}}
"""
        raw_res = self._call_openai(prompt, system_instruction=system_instruction, is_json=True)
        try:
            data = json.loads(_clean_json_response(raw_res))
            data["disclaimer"] = "This is an estimated optimization score, not an actual employer ATS result."
            return data
        except Exception:
            return {
                "overall_score": 70,
                "ats_score": 72,
                "section_scores": {
                    "summary": 70,
                    "education": 80,
                    "experience": 70,
                    "projects": 65,
                    "skills": 80,
                    "formatting": 75,
                },
                "strengths": ["Well structured"],
                "weaknesses": ["Needs metrics"],
                "suggestions": ["Include quantifiable results"],
                "missing_keywords": ["Cloud", "Testing"],
                "disclaimer": "This is an estimated optimization score, not an actual employer ATS result.",
            }

    # ------------------------------------------------------------------
    # 3. Job Match
    # ------------------------------------------------------------------
    def match_job(self, resume_data: dict, job_description: str) -> dict:
        # Algorithmic scoring
        resume_skills = set(
            s.lower().strip()
            for s in (resume_data.get("technical_skills", []) + resume_data.get("soft_skills", []))
            if isinstance(s, str)
        )
        jd_lower = job_description.lower()
        matched = [s for s in resume_skills if s and s in jd_lower]

        common_keywords = [
            "python", "javascript", "typescript", "react", "fastapi", "django", "node.js",
            "docker", "kubernetes", "aws", "gcp", "azure", "sql", "postgresql", "mongodb",
            "redis", "git", "ci/cd", "rest api", "graphql", "agile", "scrum"
        ]
        jd_keywords = [kw for kw in common_keywords if kw in jd_lower]
        missing = [kw for kw in jd_keywords if kw not in resume_skills]

        req_count = max(len(matched) + len(missing), 1)
        skill_score = min(100.0, round((len(matched) / req_count) * 100.0, 1))

        num_exps = len(resume_data.get("experience", []))
        exp_score = 85.0 if num_exps >= 2 else (65.0 if num_exps == 1 else 45.0)
        edu_score = 85.0

        jd_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", jd_lower))
        resume_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", json.dumps(resume_data).lower()))
        overlap = jd_words.intersection(resume_words)
        keyword_score = min(100.0, round((len(overlap) / max(len(jd_words), 1)) * 100.0 * 2.5, 1))

        overall = round(
            (0.40 * skill_score)
            + (0.25 * exp_score)
            + (0.15 * edu_score)
            + (0.20 * keyword_score),
            1,
        )

        prompt = (
            f"Given this resume summary and job description, explain the match in 2-3 sentences "
            f"and provide recommendations.\nResume: {resume_data.get('summary', '')}\n"
            f"Job Description: {job_description[:1200]}\n"
            f"Return JSON: {{\"explanation\": \"...\", \"recommendations\": [\"...\"]}}"
        )

        explanation = f"Match score is {overall}%. Profile aligns well on core competencies."
        recommendations = ["Highlight matching technical accomplishments"]

        try:
            raw_res = self._call_openai(
                prompt,
                system_instruction="You are a career consultant providing match explanations.",
                is_json=True,
            )
            parsed = json.loads(_clean_json_response(raw_res))
            explanation = parsed.get("explanation", explanation)
            recommendations = parsed.get("recommendations", recommendations)
        except Exception as e:
            logger.warning("OpenAI match explanation failed: %s", e)

        return {
            "overall_score": overall,
            "skill_score": skill_score,
            "experience_score": exp_score,
            "education_score": edu_score,
            "keyword_score": keyword_score,
            "matched_skills": matched,
            "missing_skills": missing[:8],
            "explanation": explanation,
            "recommendations": recommendations,
        }

    # ------------------------------------------------------------------
    # 4. Cover Letter
    # ------------------------------------------------------------------
    def generate_cover_letter(
        self,
        resume_data: dict,
        job_data: dict,
        tone: str = "professional",
    ) -> str:
        system_instruction = (
            "You are an expert career coach. Generate a personalized cover letter using ONLY the "
            "information provided in the resume. Do not invent experience, skills, or achievements."
        )
        prompt = f"""Write a {tone} cover letter:
Job: {job_data.get('title', '')} at {job_data.get('company', '')}
Job Description: {job_data.get('description', '')[:1000]}
Resume Data: {json.dumps(resume_data, indent=2)}
Return plain text formatted letter.
"""
        return self._call_openai(prompt, system_instruction=system_instruction, is_json=False)

    # ------------------------------------------------------------------
    # 5. Tailor Resume
    # ------------------------------------------------------------------
    def tailor_resume(self, resume_data: dict, job_description: str) -> dict:
        system_instruction = (
            "You are an expert resume writer. Optimize this resume for the job description. "
            "NEVER invent work experience, projects, degrees, or skills."
        )
        prompt = f"""Tailor resume for this job:
Job Description: {job_description[:1500]}
Resume: {json.dumps(resume_data, indent=2)}
Return JSON with updated_sections, keyword_additions, optimization_notes.
"""
        raw_res = self._call_openai(prompt, system_instruction=system_instruction, is_json=True)
        try:
            return json.loads(_clean_json_response(raw_res))
        except Exception:
            return {
                "updated_sections": {
                    "summary": resume_data.get("summary", ""),
                    "experience": resume_data.get("experience", []),
                    "skills": resume_data.get("technical_skills", []),
                },
                "keyword_additions": [],
                "optimization_notes": ["Retained original resume data."],
            }

    # ------------------------------------------------------------------
    # 6. Interview Questions
    # ------------------------------------------------------------------
    def generate_interview_questions(self, job_data: dict, resume_data: dict) -> dict:
        prompt = f"""Generate interview questions for {job_data.get('title', '')}:
Resume: {json.dumps(resume_data, indent=2)}
Return JSON: technical_questions, hr_questions, behavioral_questions, coding_challenges, suggested_answers, tips.
"""
        raw_res = self._call_openai(
            prompt,
            system_instruction="You are a senior tech hiring manager.",
            is_json=True,
        )
        try:
            return json.loads(_clean_json_response(raw_res))
        except Exception:
            return {
                "technical_questions": ["Explain your system architecture experience."],
                "hr_questions": ["Why this role?"],
                "behavioral_questions": ["Describe a challenge."],
                "coding_challenges": ["Implement an API rate limiter."],
                "suggested_answers": {},
                "tips": ["Use STAR method."],
            }

    # ------------------------------------------------------------------
    # 7. Chat
    # ------------------------------------------------------------------
    def chat(self, messages: list, context: dict) -> str:
        prompt = f"Context: {json.dumps(context)}\nMessages: {json.dumps(messages)}\nProvide the next assistant response."
        return self._call_openai(
            prompt,
            system_instruction="You are ApplyMate AI career assistant.",
            is_json=False,
        )

    # ------------------------------------------------------------------
    # 8. Weekly Report
    # ------------------------------------------------------------------
    def generate_weekly_report(self, user_stats: dict) -> str:
        prompt = f"Generate weekly job search summary for stats: {json.dumps(user_stats)}"
        return self._call_openai(
            prompt,
            system_instruction="You are an executive career coach.",
            is_json=False,
        )
