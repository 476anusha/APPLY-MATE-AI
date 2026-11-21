"""Gemini AI Provider implementation for ApplyMate AI."""
import json
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional

from .base import AIProvider

logger = logging.getLogger(__name__)

# Try importing google.generativeai safely
try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig
    HAS_GENAI = True
except ImportError:
    genai = None
    GenerationConfig = None
    HAS_GENAI = False


def _clean_json_response(raw_text: str) -> str:
    """Extract and sanitize JSON from model output (strips markdown fences)."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


class GeminiProvider(AIProvider):
    """Google Gemini AI implementation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-3.5-flash",
        pro_model_name: str = "gemini-pro-latest",
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name
        self.pro_model_name = pro_model_name
        self._last_call_timestamp: float = 0.0
        self._min_call_interval: float = 0.5  # Rate limiting: min 500ms between calls

        if HAS_GENAI and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
            except Exception as e:
                logger.warning("Failed to configure genai: %s", e)

    def _rate_limit(self):
        """Simple rate limiting to prevent hitting Gemini RPM limits."""
        elapsed = time.time() - self._last_call_timestamp
        if elapsed < self._min_call_interval:
            time.sleep(self._min_call_interval - elapsed)
        self._last_call_timestamp = time.time()

    def _call_gemini(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        is_json: bool = False,
        use_pro: bool = False,
        retries: int = 2,
    ) -> str:
        """Execute a call to Gemini model with retry and error handling."""
        if not HAS_GENAI or not self.api_key:
            raise RuntimeError("Gemini API key is not configured or google-generativeai is missing.")

        chosen_model = self.pro_model_name if use_pro else self.model_name
        self._rate_limit()

        kwargs: Dict[str, Any] = {}
        if system_instruction:
            kwargs["system_instruction"] = system_instruction

        model = genai.GenerativeModel(chosen_model, **kwargs)

        generation_config = {}
        if is_json:
            generation_config["response_mime_type"] = "application/json"

        last_err = None
        for attempt in range(retries + 1):
            try:
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config if generation_config else None,
                )
                if response and response.text:
                    return response.text
                return "{}" if is_json else ""
            except Exception as e:
                last_err = e
                logger.warning(
                    "Gemini API attempt %d failed: %s. Retrying...", attempt + 1, e
                )
                time.sleep(1.0 * (attempt + 1))

        raise RuntimeError(f"Gemini API call failed after retries: {last_err}")

    # ------------------------------------------------------------------
    # 1. Resume Parsing
    # ------------------------------------------------------------------
    def analyze_resume(self, text: str) -> dict:
        """Parse raw resume text and extract structured JSON."""
        system_instruction = (
            "You are an expert resume parser. Extract all information in valid JSON format. "
            "NEVER make up information — only extract what is truthfully present in the input text. "
            "If a field is missing, provide an empty string or empty list as appropriate."
        )

        prompt = f"""Extract all details from the following resume text into this exact JSON schema:
{{
  "full_name": "Full Name",
  "email": "email@example.com",
  "phone": "+1-555-0199",
  "summary": "Professional summary or objective",
  "education": [
    {{
      "institution": "University Name",
      "degree": "Degree and Major",
      "field_of_study": "Field",
      "start_date": "YYYY",
      "end_date": "YYYY or Present",
      "gpa": "GPA if mentioned"
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
      "bullets": ["Bullet 1", "Bullet 2"]
    }}
  ],
  "projects": [
    {{
      "title": "Project Name",
      "description": "Short description",
      "technologies": ["Tech 1", "Tech 2"],
      "link": "URL if available"
    }}
  ],
  "technical_skills": ["Skill 1", "Skill 2"],
  "soft_skills": ["Skill 1", "Skill 2"],
  "certifications": ["Cert 1", "Cert 2"],
  "achievements": ["Achievement 1"]
}}

Resume text:
\"\"\"
{text}
\"\"\"
"""
        raw_res = self._call_gemini(prompt, system_instruction=system_instruction, is_json=True)
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
        """Score resume across ATS readability, completeness, impact, and sections."""
        system_instruction = (
            "You are an ATS and resume quality expert. Analyze this resume data and return scores, "
            "strengths, weaknesses, suggestions, and missing keywords in valid JSON format."
        )

        prompt = f"""Analyze this parsed resume data and provide evaluation scores (0 to 100) and actionable advice:
{json.dumps(extracted_data, indent=2)}

Return your evaluation matching this JSON schema:
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
  "strengths": [
    "Clear quantifiable impact in experience bullets",
    "Strong technical skills section"
  ],
  "weaknesses": [
    "Summary is slightly generic",
    "Few metrics in older project descriptions"
  ],
  "suggestions": [
    "Add more metrics and outcome numbers (e.g. % improvement, revenue)",
    "Include links to live demo or GitHub repositories for personal projects"
  ],
  "missing_keywords": ["CI/CD", "Docker", "Unit Testing", "Agile"],
  "disclaimer": "This is an estimated optimization score, not an actual employer ATS result."
}}
"""
        raw_res = self._call_gemini(prompt, system_instruction=system_instruction, is_json=True)
        try:
            data = json.loads(_clean_json_response(raw_res))
            data["disclaimer"] = "This is an estimated optimization score, not an actual employer ATS result."
            return data
        except Exception:
            return {
                "overall_score": 72,
                "ats_score": 75,
                "section_scores": {
                    "summary": 70,
                    "education": 80,
                    "experience": 70,
                    "projects": 65,
                    "skills": 80,
                    "formatting": 75,
                },
                "strengths": ["Clear structure", "Relevant skills list"],
                "weaknesses": ["Could use more measurable outcomes"],
                "suggestions": ["Add quantifiable metrics to experience bullet points"],
                "missing_keywords": ["Agile", "Cloud", "Testing"],
                "disclaimer": "This is an estimated optimization score, not an actual employer ATS result.",
            }

    # ------------------------------------------------------------------
    # 3. Job Match (Algorithmic first, Gemini explanation)
    # ------------------------------------------------------------------
    def match_job(self, resume_data: dict, job_description: str) -> dict:
        """Calculate numerical match score algorithmically, then use Gemini for explanation."""
        # 1. Algorithmic scoring
        # Extract skills from resume
        resume_skills = set(
            s.lower().strip()
            for s in (resume_data.get("technical_skills", []) + resume_data.get("soft_skills", []))
            if isinstance(s, str)
        )

        jd_lower = job_description.lower()

        # Identify skills and keywords mentioned in job description
        matched = []
        missing = []
        for skill in resume_skills:
            if skill and skill in jd_lower:
                matched.append(skill)

        # Common tech keywords to check if missing
        common_keywords = [
            "python", "javascript", "typescript", "react", "fastapi", "django", "node.js",
            "docker", "kubernetes", "aws", "gcp", "azure", "sql", "postgresql", "mongodb",
            "redis", "git", "ci/cd", "rest api", "graphql", "agile", "scrum", "microservices"
        ]
        jd_keywords = [kw for kw in common_keywords if kw in jd_lower]

        for kw in jd_keywords:
            if kw not in resume_skills:
                missing.append(kw)

        # Matched skills score (40% weight)
        req_count = max(len(matched) + len(missing), 1)
        skill_score = min(100.0, round((len(matched) / req_count) * 100.0, 1))

        # Experience score (25% weight)
        exp_entries = resume_data.get("experience", [])
        num_exps = len(exp_entries)
        if "senior" in jd_lower or "lead" in jd_lower:
            exp_score = 90.0 if num_exps >= 3 else (65.0 if num_exps >= 1 else 40.0)
        elif "mid" in jd_lower:
            exp_score = 90.0 if num_exps >= 2 else (70.0 if num_exps >= 1 else 50.0)
        else:
            exp_score = 90.0 if num_exps >= 1 else 60.0

        # Education score (15% weight)
        edu_entries = resume_data.get("education", [])
        edu_text = " ".join(
            str(e.get("degree", "")) + " " + str(e.get("field_of_study", ""))
            for e in edu_entries if isinstance(e, dict)
        ).lower()
        if "degree" in jd_lower or "bachelor" in jd_lower or "master" in jd_lower:
            edu_score = 95.0 if ("bachelor" in edu_text or "master" in edu_text or "bs" in edu_text or "computer" in edu_text or "engineering" in edu_text) else 65.0
        else:
            edu_score = 85.0

        # Keyword overlap score (20% weight)
        resume_full_text = json.dumps(resume_data).lower()
        jd_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", jd_lower))
        resume_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", resume_full_text))
        overlap = jd_words.intersection(resume_words)
        keyword_score = min(100.0, round((len(overlap) / max(len(jd_words), 1)) * 100.0 * 2.5, 1))

        # Weighted average
        overall = round(
            (0.40 * skill_score)
            + (0.25 * exp_score)
            + (0.15 * edu_score)
            + (0.20 * keyword_score),
            1,
        )

        # 2. Call Gemini for explanation and recommendations
        prompt = (
            f"Given this resume summary and job description, explain the match in 2-3 sentences "
            f"and provide 2-3 clear recommendations for the applicant.\n\n"
            f"Resume summary: {resume_data.get('summary', '')}\n"
            f"Matched skills: {matched}\n"
            f"Missing keywords: {missing[:5]}\n\n"
            f"Job Description:\n{job_description[:1500]}\n\n"
            f"Return JSON: {{\"explanation\": \"string\", \"recommendations\": [\"rec1\", \"rec2\"]}}"
        )

        explanation = f"Your resume matches {overall}% of this job profile. You have strong alignment on core technical capabilities with room to highlight missing domain tools."
        recommendations = ["Highlight matching projects prominently", "Incorporate missing keywords in your summary"]

        try:
            raw_res = self._call_gemini(
                prompt,
                system_instruction="You are a career consultant providing concise candidate feedback.",
                is_json=True,
            )
            parsed = json.loads(_clean_json_response(raw_res))
            if "explanation" in parsed:
                explanation = parsed["explanation"]
            if "recommendations" in parsed and isinstance(parsed["recommendations"], list):
                recommendations = parsed["recommendations"]
        except Exception as e:
            logger.warning("Gemini explanation generation failed: %s", e)

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
    # 4. Cover Letter Generation
    # ------------------------------------------------------------------
    def generate_cover_letter(
        self,
        resume_data: dict,
        job_data: dict,
        tone: str = "professional",
    ) -> str:
        """Generate personalized cover letter using ONLY information provided in the resume."""
        system_instruction = (
            "You are an expert career coach. Generate a personalized cover letter using ONLY the "
            "information provided in the resume. Do not invent experience, skills, or achievements. "
            "Return the cover letter as plain text, properly formatted."
        )

        prompt = f"""Generate a {tone} cover letter for the following job using ONLY the provided resume details:

Job Title: {job_data.get('title', 'Target Role')}
Company: {job_data.get('company', 'Target Company')}
Job Description:
{job_data.get('description', '')[:1200]}

Candidate Resume:
{json.dumps(resume_data, indent=2)}

Tone required: {tone} (professional, enthusiastic, concise, or creative).
Return only the formatted letter text. Do not output JSON or markdown code block markers.
"""
        return self._call_gemini(prompt, system_instruction=system_instruction, is_json=False)

    # ------------------------------------------------------------------
    # 5. Resume Tailoring
    # ------------------------------------------------------------------
    def tailor_resume(self, resume_data: dict, job_description: str) -> dict:
        """Optimize resume sections for a job description without inventing anything."""
        system_instruction = (
            "You are an expert resume writer. Optimize this resume for the job description. "
            "CRITICAL RULES:\n"
            "1. NEVER invent work experience, projects, degrees, or skills.\n"
            "2. Only rephrase, reorder, and emphasize existing information.\n"
            "3. Add relevant keywords from the job description where they truthfully apply.\n"
            "4. Suggest improvements but mark any invented content as '[ADD IF TRUE: ...]'.\n"
            "Return valid JSON matching the requested structure."
        )

        prompt = f"""Tailor this resume for the target job:

Job Description:
\"\"\"
{job_description[:2000]}
\"\"\"

Resume Data:
{json.dumps(resume_data, indent=2)}

Return JSON with this schema:
{{
  "updated_sections": {{
    "summary": "Optimized professional summary",
    "experience": [
      {{
        "company": "Company Name",
        "title": "Title",
        "bullets": ["Optimized bullet 1", "Optimized bullet 2"]
      }}
    ],
    "skills": ["Skill 1", "Skill 2"]
  }},
  "keyword_additions": ["Keyword 1", "Keyword 2"],
  "optimization_notes": [
    "Emphasized React and API architecture in most recent role",
    "Placed cloud infrastructure skills closer to top"
  ]
}}
"""
        raw_res = self._call_gemini(prompt, system_instruction=system_instruction, is_json=True)
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
                "optimization_notes": ["Parsed fallback: retained original resume sections."],
            }

    # ------------------------------------------------------------------
    # 6. Interview Preparation
    # ------------------------------------------------------------------
    def generate_interview_questions(self, job_data: dict, resume_data: dict) -> dict:
        """Generate tailored interview questions and suggested answers."""
        system_instruction = (
            "You are a senior hiring manager and tech interviewer. "
            "Generate comprehensive interview preparation material."
        )

        prompt = f"""Generate tailored interview prep material for this role and candidate:

Job Role: {job_data.get('title', '')} at {job_data.get('company', '')}
Job Description: {job_data.get('description', '')[:1000]}
Candidate Skills & Experience:
{json.dumps({'skills': resume_data.get('technical_skills', []), 'experience': resume_data.get('experience', [])}, indent=2)}

Return valid JSON with this schema:
{{
  "technical_questions": [
    "Question 1",
    "Question 2"
  ],
  "hr_questions": [
    "Tell me about a time you resolved a team conflict.",
    "Why do you want to work at this company?"
  ],
  "behavioral_questions": [
    "Describe a challenging project and how you handled unexpected roadblocks."
  ],
  "coding_challenges": [
    "Implement an LRU cache or explain your indexing strategy for high-throughput Postgres tables."
  ],
  "suggested_answers": {{
    "Why do you want to work at this company?": "Frame around alignment with their mission and using your stack experience to solve their scaling challenges.",
    "Tell me about a time you resolved a team conflict.": "Use STAR method: explain context, action taken, and measurable resolution."
  }},
  "tips": [
    "Review system design trade-offs",
    "Have 2-3 questions ready to ask the interviewer about team roadmap"
  ]
}}
"""
        raw_res = self._call_gemini(prompt, system_instruction=system_instruction, is_json=True)
        try:
            return json.loads(_clean_json_response(raw_res))
        except Exception:
            return {
                "technical_questions": [
                    "Can you explain your approach to scalable backend architecture?",
                    "How do you handle schema migrations and zero-downtime deployments?",
                ],
                "hr_questions": [
                    "Why are you interested in this position?",
                    "What work environment allows you to do your best work?",
                ],
                "behavioral_questions": [
                    "Tell me about a difficult bug you tracked down in production.",
                ],
                "coding_challenges": [
                    "Design an API rate limiter with sliding window counter.",
                ],
                "suggested_answers": {
                    "Why are you interested in this position?": "Highlight enthusiasm for the mission, product domain, and collaborative culture."
                },
                "tips": [
                    "Use the STAR method for behavioral questions",
                    "Ask clarifying questions before coding",
                ],
            }

    # ------------------------------------------------------------------
    # 7. Agent / Multi-turn Chat
    # ------------------------------------------------------------------
    def chat(self, messages: list, context: dict) -> str:
        """Conversational chat helper."""
        system_instruction = (
            "You are ApplyMate AI, an intelligent, empathetic, and highly capable AI career assistant. "
            "You assist job seekers with resume reviews, job discovery, application tracking, "
            "interview prep, and career strategy. Be concise, actionable, and encouraging."
        )

        context_str = ""
        if context:
            context_str = f"\nCurrent User Context:\n{json.dumps(context, indent=2)}\n"

        # Format history
        history_lines = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_lines.append(f"{role.capitalize()}: {content}")

        full_prompt = f"{context_str}\nConversation:\n" + "\n".join(history_lines) + "\nAssistant:"
        return self._call_gemini(full_prompt, system_instruction=system_instruction, is_json=False)

    # ------------------------------------------------------------------
    # 8. Weekly Career Report
    # ------------------------------------------------------------------
    def generate_weekly_report(self, user_stats: dict) -> str:
        """Generate formatted weekly career progress report."""
        system_instruction = (
            "You are an encouraging executive career coach. Summarize weekly job search progress, "
            "celebrate wins, identify bottlenecks, and give 3 high-impact action steps for next week."
        )

        prompt = f"""Generate a weekly career progress report based on these stats:
{json.dumps(user_stats, indent=2)}

Format with markdown headings, bullet points, and an encouraging closing tone.
"""
        return self._call_gemini(prompt, system_instruction=system_instruction, is_json=False)
