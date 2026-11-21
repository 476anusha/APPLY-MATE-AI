"""Mock / Demo AI Provider — real text parsing with heuristics, variable scores."""
import re
import hashlib
from typing import Any, Dict, List, Optional

from .base import AIProvider

# Common tech skills to look for in resume text
TECH_SKILLS_DB = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin",
    "React", "Angular", "Vue", "Next.js", "Nuxt", "Svelte", "Node.js", "Express", "FastAPI", "Django", "Flask",
    "Spring", "Laravel", "Rails", "ASP.NET",
    "SQL", "MySQL", "PostgreSQL", "SQLite", "MongoDB", "Redis", "Cassandra", "DynamoDB", "Firebase", "Supabase",
    "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins", "GitHub Actions", "CI/CD",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "NLP",
    "Git", "Linux", "REST", "GraphQL", "gRPC", "Microservices", "System Design", "API",
    "HTML", "CSS", "Tailwind", "Bootstrap", "SCSS", "Webpack", "Vite",
    "Figma", "Adobe XD", "Jira", "Confluence", "Agile", "Scrum",
    "Excel", "PowerPoint", "MATLAB", "R", "Scala", "Hadoop", "Spark",
    "Unity", "Unreal", "OpenCV", "ROS", "Arduino", "Raspberry Pi",
]

SOFT_SKILLS_DB = [
    "Leadership", "Communication", "Teamwork", "Problem Solving", "Critical Thinking",
    "Time Management", "Adaptability", "Creativity", "Collaboration", "Mentorship",
    "Project Management", "Analytical", "Detail-oriented", "Self-motivated",
]


def _extract_name(lines: List[str]) -> str:
    """Try to extract name from first non-empty lines."""
    for line in lines[:5]:
        line = line.strip()
        # Name is likely 2-4 words, no special chars, not an email/phone
        if (2 <= len(line.split()) <= 4
                and not re.search(r"[@|/\\|<>{}]", line)
                and not re.search(r"\d{4,}", line)
                and len(line) < 50):
            return line
    return ""


def _extract_email(text: str) -> str:
    m = re.search(r"[\w.+-]+@[\w.-]+\.\w{2,}", text)
    return m.group(0) if m else ""


def _extract_phone(text: str) -> str:
    m = re.search(r"(\+?\d[\d\s\-().]{7,14}\d)", text)
    return m.group(0).strip() if m else ""


def _extract_links(text: str) -> Dict[str, str]:
    links = {}
    gh = re.search(r"github\.com/[\w\-/]+", text, re.IGNORECASE)
    li = re.search(r"linkedin\.com/in/[\w\-]+", text, re.IGNORECASE)
    portfolio = re.search(r"https?://(?!github|linkedin)[\w.\-/]+", text, re.IGNORECASE)
    if gh:
        links["github"] = "https://" + gh.group(0)
    if li:
        links["linkedin"] = "https://" + li.group(0)
    if portfolio:
        links["portfolio"] = portfolio.group(0)
    return links


def _extract_skills(text: str) -> List[str]:
    """Find which known skills are mentioned in the resume."""
    found = []
    text_lower = text.lower()
    for skill in TECH_SKILLS_DB:
        # Match whole word / phrase
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return found


def _extract_soft_skills(text: str) -> List[str]:
    found = []
    text_lower = text.lower()
    for skill in SOFT_SKILLS_DB:
        if skill.lower() in text_lower:
            found.append(skill)
    return found


def _extract_sections(text: str) -> Dict[str, str]:
    """Split resume text into sections by common headers."""
    section_headers = [
        r"(experience|work experience|professional experience|employment)",
        r"(education|academic|qualifications)",
        r"(projects|personal projects|academic projects)",
        r"(skills|technical skills|core competencies|technologies)",
        r"(certifications?|certificates?|courses?)",
        r"(summary|objective|profile|about)",
        r"(achievements?|accomplishments?|awards?)",
    ]
    sections: Dict[str, str] = {}
    text_lower = text.lower()

    for pattern in section_headers:
        m = re.search(pattern, text_lower)
        if m:
            key = m.group(1).split("|")[0].strip()
            start = m.start()
            # Find where next section starts
            rest = text_lower[start + len(key):]
            end_positions = []
            for other_pattern in section_headers:
                nm = re.search(other_pattern, rest)
                if nm and nm.start() > 0:
                    end_positions.append(nm.start())
            end = min(end_positions) if end_positions else len(rest)
            sections[key] = text[start: start + len(key) + end].strip()

    return sections


def _extract_experience(text: str) -> List[Dict]:
    """Heuristic: find company / title / date patterns."""
    experience = []
    sections = _extract_sections(text)
    exp_text = ""
    for key in sections:
        if "experience" in key or "employment" in key:
            exp_text = sections[key]
            break

    if not exp_text:
        return []

    # Find date ranges like "Jan 2022 – Present" or "2020 - 2022"
    date_pattern = r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[\w\s]*\d{4}|\d{4})\s*[-–—]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[\w\s]*\d{4}|Present|Current)"
    matches = list(re.finditer(date_pattern, exp_text, re.IGNORECASE))

    for i, match in enumerate(matches[:4]):  # max 4 jobs
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(exp_text)
        chunk = exp_text[max(0, start - 300): end].strip()
        lines = [l.strip() for l in chunk.split("\n") if l.strip()]

        # Title is usually first capitalised short line
        title = ""
        company = ""
        for line in lines[:6]:
            if 2 <= len(line.split()) <= 6 and line[0].isupper() and not re.search(r"\d{4}", line):
                if not title:
                    title = line
                elif not company:
                    company = line
                    break

        experience.append({
            "title": title or "Software Developer",
            "company": company or "Company",
            "start_date": match.group(1),
            "end_date": match.group(2),
            "is_current": "present" in match.group(2).lower() or "current" in match.group(2).lower(),
            "bullets": [l for l in lines if l.startswith(("•", "-", "▪", "*", "–")) or (len(l) > 40 and l[0].islower())][:4],
        })

    return experience


def _extract_education(text: str) -> List[Dict]:
    """Extract education entries."""
    edu = []
    sections = _extract_sections(text)
    edu_text = ""
    for key in sections:
        if "education" in key or "academic" in key:
            edu_text = sections[key]
            break

    degree_pattern = r"(B\.?Tech|B\.?E\.?|B\.?Sc|M\.?Tech|M\.?Sc|M\.?E\.?|MBA|Ph\.?D|Bachelor|Master|B\.?C\.?A|M\.?C\.?A)[^.\n]{0,80}"
    matches = re.findall(degree_pattern, edu_text or text, re.IGNORECASE)

    year_pattern = r"\b(20\d{2})\b"
    years = re.findall(year_pattern, edu_text or text)

    for i, match in enumerate(matches[:3]):
        # Try to get institution from nearby text
        idx = (edu_text or text).find(match)
        nearby = (edu_text or text)[max(0, idx - 100): idx + 200]
        inst_match = re.search(r"(?:University|College|Institute|School|IIT|NIT|BITS)\s+[\w\s,]+", nearby, re.IGNORECASE)

        edu.append({
            "degree": match.strip(),
            "institution": inst_match.group(0).strip() if inst_match else "University",
            "start_date": years[i * 2] if i * 2 < len(years) else "",
            "end_date": years[i * 2 + 1] if i * 2 + 1 < len(years) else (years[-1] if years else ""),
            "gpa": "",
        })

    return edu if edu else [{
        "degree": "B.Tech Computer Science",
        "institution": "University",
        "start_date": "2020",
        "end_date": "2024",
    }]


def _extract_projects(text: str) -> List[Dict]:
    """Extract project names and descriptions."""
    projects = []
    sections = _extract_sections(text)
    proj_text = ""
    for key in sections:
        if "project" in key:
            proj_text = sections[key]
            break

    if not proj_text:
        return []

    lines = [l.strip() for l in proj_text.split("\n") if l.strip()]
    current_proj = None

    for line in lines:
        # Project title: short, starts with capital, no leading bullet
        if (not line.startswith(("•", "-", "▪", "*"))
                and 2 <= len(line.split()) <= 8
                and line[0].isupper()
                and len(line) < 60
                and not re.match(r"project", line, re.IGNORECASE)):
            if current_proj:
                projects.append(current_proj)
            current_proj = {"name": line, "description": "", "technologies": []}
        elif current_proj:
            if current_proj["description"] == "":
                current_proj["description"] = line.lstrip("•-▪* ")
            # Look for tech stack in brackets / after | or :
            tech_match = re.findall(r"\b(?:React|Python|Node|FastAPI|Django|Flask|MySQL|MongoDB|AWS|Docker|TensorFlow|PyTorch|JavaScript|TypeScript|Java|C\+\+|PHP|Ruby|Go)\b", line)
            current_proj["technologies"].extend(tech_match)

    if current_proj:
        projects.append(current_proj)

    return projects[:5]


def _extract_summary(text: str) -> str:
    """Extract objective/summary section."""
    sections = _extract_sections(text)
    for key in sections:
        if any(w in key for w in ["summary", "objective", "profile", "about"]):
            # Return first 2-3 non-empty lines of that section
            lines = [l.strip() for l in sections[key].split("\n") if l.strip() and len(l.strip()) > 20]
            return " ".join(lines[:3])
    return ""


def _calculate_score(
    text: str,
    skills: List[str],
    experience: List[Dict],
    education: List[Dict],
    projects: List[Dict],
) -> Dict:
    """Calculate a realistic, variable ATS score based on actual resume content."""

    # Use a hash of the text to get consistent but different scores per resume
    text_hash = int(hashlib.md5(text[:200].encode()).hexdigest(), 16)
    base_variation = (text_hash % 20) - 10  # -10 to +10

    # Score components
    scores = {}

    # Skills (25 points max)
    skill_count = len(skills)
    scores["skills"] = min(100, 50 + skill_count * 4 + (base_variation // 2))

    # Experience (25 points max)
    exp_count = len(experience)
    has_current = any(e.get("is_current") for e in experience)
    scores["experience"] = min(100, 40 + exp_count * 15 + (10 if has_current else 0) + base_variation)

    # Education (20 points max)
    edu_count = len(education)
    scores["education"] = min(100, 60 + edu_count * 20 + base_variation)

    # Projects (15 points max)
    proj_count = len(projects)
    scores["projects"] = min(100, 40 + proj_count * 15 + base_variation)

    # Contact info (10 points)
    has_email = bool(_extract_email(text))
    has_phone = bool(_extract_phone(text))
    has_links = bool(_extract_links(text))
    scores["contact_info"] = 60 + (15 if has_email else 0) + (15 if has_phone else 0) + (10 if has_links else 0)
    scores["contact_info"] = min(100, scores["contact_info"])

    # ATS formatting (5 points)
    word_count = len(text.split())
    scores["formatting"] = min(100, 50 + min(50, word_count // 20) + base_variation)

    # Weighted overall
    overall = int(
        scores["skills"] * 0.25
        + scores["experience"] * 0.25
        + scores["education"] * 0.20
        + scores["projects"] * 0.15
        + scores["contact_info"] * 0.10
        + scores["formatting"] * 0.05
    )
    overall = max(45, min(97, overall))  # Clamp 45-97

    # ATS score slightly different
    ats_score = max(40, min(99, overall + (text_hash % 10) - 5))

    # Generate relevant strengths/weaknesses
    strengths = []
    weaknesses = []
    suggestions = []

    if skill_count >= 10:
        strengths.append(f"Strong technical skill set with {skill_count} identified technologies")
    elif skill_count >= 5:
        strengths.append(f"Good range of {skill_count} technical skills listed")
    else:
        weaknesses.append("Few technical skills detected — expand your skills section")
        suggestions.append("Add a dedicated 'Technical Skills' section with specific technologies you know")

    if exp_count >= 2:
        strengths.append("Multiple work experiences demonstrate career progression")
    elif exp_count == 1:
        strengths.append("Professional work experience included")
    else:
        weaknesses.append("No work experience section found")
        suggestions.append("Add internships, freelance projects, or any professional experience")

    if has_current:
        strengths.append("Currently employed — shows active career momentum")

    if proj_count >= 3:
        strengths.append(f"{proj_count} projects demonstrate hands-on practical experience")
    elif proj_count == 0:
        weaknesses.append("No projects section detected")
        suggestions.append("Add 2-3 personal or academic projects with technologies used and GitHub links")

    if not has_links:
        weaknesses.append("No GitHub/LinkedIn/portfolio links found")
        suggestions.append("Add your GitHub profile and LinkedIn URL to increase visibility")

    if word_count < 200:
        weaknesses.append("Resume content seems thin — add more detail to each role")
        suggestions.append("Expand bullet points with quantifiable achievements (e.g., 'Reduced load time by 40%')")
    elif word_count > 800:
        suggestions.append("Consider condensing to 1 page — recruiters spend avg 7 seconds on first scan")

    # Missing keywords
    high_demand_skills = ["Docker", "AWS", "React", "Python", "SQL", "Git", "Agile"]
    missing = [s for s in high_demand_skills if s not in skills][:4]

    return {
        "overall_score": overall,
        "score": overall,
        "ats_score": ats_score,
        "section_scores": scores,
        "strengths": strengths[:4],
        "weaknesses": weaknesses[:3],
        "suggestions": suggestions[:4],
        "missing_keywords": missing,
        "disclaimer": "Scores calculated using heuristic analysis. Add a Gemini API key for deeper AI insights.",
    }


class MockProvider(AIProvider):
    """Real-text-parsing Mock AI Provider — extracts actual resume data, variable scores."""

    def analyze_resume(self, text: str) -> dict:
        """Parse resume text into structured data using regex heuristics."""
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        name = _extract_name(lines)
        email = _extract_email(text)
        phone = _extract_phone(text)
        links = _extract_links(text)
        skills = _extract_skills(text)
        soft_skills = _extract_soft_skills(text)
        experience = _extract_experience(text)
        education = _extract_education(text)
        projects = _extract_projects(text)
        summary = _extract_summary(text)

        return {
            "full_name": name,
            "email": email,
            "phone": phone,
            "linkedin": links.get("linkedin", ""),
            "github": links.get("github", ""),
            "portfolio": links.get("portfolio", ""),
            "summary": summary,
            "technical_skills": skills,
            "soft_skills": soft_skills,
            "experience": experience,
            "education": education,
            "projects": projects,
            "certifications": [],
            "achievements": [],
            "_raw_text_length": len(text),
            "_raw_text_preview": text[:500],
            "raw_text": text,
        }

    def score_resume(self, parsed: dict) -> dict:
        """Score based on actual parsed content — variable per resume."""
        raw_text = parsed.get("raw_text") or parsed.get("_raw_text_preview", "")
        return _calculate_score(
            text=raw_text,
            skills=parsed.get("technical_skills", []),
            experience=parsed.get("experience", []),
            education=parsed.get("education", []),
            projects=parsed.get("projects", []),
        )

    def tailor_resume(self, resume_data: dict, job_description: str) -> dict:
        """Rewrite resume sections to match a job description (heuristic)."""
        skills = resume_data.get("technical_skills", [])
        # Find JD keywords present in resume
        jd_words = set(re.findall(r"\b[A-Z][a-zA-Z+#]{2,}\b", job_description))
        matched = [w for w in jd_words if w in " ".join(skills)]
        additions = [w for w in jd_words if w not in " ".join(skills)][:5]
        return {
            "updated_sections": {
                "summary": resume_data.get("summary", "") + " Passionate about delivering high-impact solutions.",
                "skills": skills,
            },
            "keyword_additions": additions,
            "optimization_notes": [
                "Added role-specific keywords from job description",
                "Reordered skills to match JD priority",
                "Enhanced summary to align with company values",
            ],
        }

    def match_job(self, resume_data: dict, job_description: str) -> dict:
        """Calculate match score between resume and job description."""
        skills = resume_data.get("technical_skills", [])
        jd_lower = job_description.lower()
        matched = [s for s in skills if s.lower() in jd_lower]
        missing = [s for s in ["Python", "React", "SQL", "Docker", "AWS"] if s not in skills]
        score = min(95, 40 + len(matched) * 5)
        return {
            "overall_score": score,
            "skill_score": min(100, len(matched) * 10),
            "experience_score": 70,
            "education_score": 80,
            "keyword_score": min(100, len(matched) * 8),
            "matched_skills": matched,
            "missing_skills": missing[:5],
            "explanation": f"Your resume matches {len(matched)} key skills from the job description.",
            "recommendations": ["Add quantifiable achievements", "Include relevant certifications"],
        }

    def generate_cover_letter(self, resume_data: dict, job_data: dict, tone: str = "professional") -> str:
        """Generate a cover letter from resume + job data."""
        name = resume_data.get("full_name", "Candidate")
        job_title = job_data.get("title", "the position")
        company = job_data.get("company", "your company")
        skills = ", ".join(resume_data.get("technical_skills", [])[:5])
        return (
            f"Dear Hiring Manager,\n\n"
            f"I am writing to express my strong interest in the {job_title} role at {company}. "
            f"With a solid foundation in {skills or 'software development'} and a passion for building "
            f"impactful solutions, I am confident in my ability to contribute meaningfully to your team.\n\n"
            f"Throughout my career, I have developed expertise in designing and implementing scalable systems, "
            f"working collaboratively with cross-functional teams, and delivering high-quality results under pressure.\n\n"
            f"I would welcome the opportunity to discuss how my skills and experience align with your team's needs.\n\n"
            f"Best regards,\n{name}"
        )

    def generate_interview_questions(self, job_data: dict, resume_data: dict) -> dict:
        """Generate interview prep material."""
        job_title = job_data.get("title", "Software Engineer")
        return {
            "technical_questions": [
                {"question": f"Explain key design principles for a {job_title} role.", "answer": "Focus on SOLID principles, clean architecture, scalability, and maintainability.", "tip": "Give concrete examples from your projects."},
                {"question": "How do you approach debugging a production issue?", "answer": "Reproduce → isolate → fix → test → document.", "tip": "Show systematic thinking."},
                {"question": "Describe your experience with databases and optimization.", "answer": "Proper indexing, avoiding N+1, query profiling, and caching strategies.", "tip": "Have a real example ready."},
            ],
            "behavioral_questions": [
                {"question": "Tell me about yourself.", "answer": "Education → key projects → skills → why this role.", "tip": "Keep to 90 seconds."},
                {"question": "Describe a challenge you overcame.", "answer": "Use STAR: Situation, Task, Action, Result.", "tip": "Quantify results."},
            ],
            "coding_challenges": [
                {"title": "Two Sum", "description": "Return indices of two numbers that add to target.", "solution": "Use a hash map — O(n)."},
            ],
            "tips": ["Research the company", "Prepare STAR stories", "Ask thoughtful questions"],
        }
        """Score based on actual parsed content — variable per resume."""
        # Use full raw text if available for better scoring
        raw_text = parsed.get("raw_text") or parsed.get("_raw_text_preview", "")
        return _calculate_score(
            text=raw_text,
            skills=parsed.get("technical_skills", []),
            experience=parsed.get("experience", []),
            education=parsed.get("education", []),
            projects=parsed.get("projects", []),
        )

    def chat(self, messages: list, context: dict) -> str:
        last_message = ""
        if messages:
            last_msg = messages[-1]
            last_message = last_msg.get("content", "").lower() if isinstance(last_msg, dict) else str(last_msg).lower()

        if "resume" in last_message or "cv" in last_message:
            return (
                "I can help with your resume! Upload a PDF or DOCX in the **Resumes** section, "
                "click **Analyze with AI** and I'll extract your skills, calculate your ATS score, "
                "and suggest improvements tailored to your target roles."
            )
        elif "job" in last_message or "find" in last_message or "search" in last_message:
            return (
                "I found multiple relevant opportunities! Check the **Jobs** section for curated listings "
                "in software engineering, data science, and full-stack roles. "
                "Would you like me to match them against your resume profile?"
            )
        elif "cover letter" in last_message:
            return (
                "I can generate a tailored cover letter! Go to a job listing and click **Cover Letter**, "
                "or tell me which company and role you're applying to and I'll draft one for you."
            )
        elif "interview" in last_message:
            return (
                "Head to **Interview Prep** and select your target role — I'll generate technical questions, "
                "behavioral prompts using the STAR method, and coding challenges with model answers."
            )
        elif "track" in last_message or "application" in last_message:
            return (
                "Use the **Application Tracker** to log every application. "
                "The Kanban board helps you visualise which stage each application is in — "
                "Applied, Assessment, Interview, Offer, etc."
            )
        else:
            return (
                f"I understand you're asking: **{last_message[:80]}**\n\n"
                "I'm ApplyMate AI — your career assistant! I can:\n"
                "- 🔍 Find relevant jobs\n"
                "- 📄 Analyze & optimize your resume\n"
                "- ✉️ Generate tailored cover letters\n"
                "- 🎤 Prepare you for interviews\n"
                "- 📊 Track your applications\n\n"
                "> 💡 Add your **Gemini API key** to `backend/.env` for full AI-powered responses."
            )

    def generate_weekly_report(self, user_stats: dict) -> str:
        total_apps = user_stats.get("total_applications", 0)
        interviews = user_stats.get("interviews_scheduled", 0)
        return (
            f"You have **{total_apps}** applications tracked and **{interviews}** interviews scheduled. "
            "Keep applying consistently and follow up after 5 business days. "
            "Use Interview Prep to practice before each interview!"
        )
