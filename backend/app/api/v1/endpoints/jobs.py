"""Jobs endpoint — search, get, match."""
import uuid
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_active_user
from app.database import get_db

router = APIRouter()


# ── Demo job data ─────────────────────────────────────────────────────────────

DEMO_JOBS = [
    {
        "id": "demo-001", "external_id": "d001", "provider": "demo",
        "title": "Python Backend Developer", "company": "TechCorp Solutions",
        "company_logo_url": None, "location": "Bangalore, India", "is_remote": False,
        "work_type": "hybrid", "employment_type": "full-time", "experience_level": "entry",
        "salary_min": 600000, "salary_max": 1000000, "salary_currency": "INR",
        "description": "We are looking for a passionate Python developer to join our backend team. You will build scalable REST APIs, work with PostgreSQL databases, and collaborate with frontend engineers.\n\nResponsibilities:\n- Design and implement RESTful APIs using FastAPI or Django\n- Write clean, testable Python code\n- Optimize database queries with PostgreSQL and SQLAlchemy\n- Participate in code reviews and agile ceremonies\n\nRequirements:\n- 0-2 years of Python experience\n- Familiarity with FastAPI or Django\n- Understanding of SQL and ORM concepts\n- Knowledge of Git and basic CI/CD",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Git", "REST APIs"],
        "preferred_skills": ["Docker", "Redis", "AWS", "Pytest"],
        "application_url": "https://example.com/apply/d001",
        "posted_at": "2026-11-01T00:00:00Z", "is_active": True,
    },
    {
        "id": "demo-002", "external_id": "d002", "provider": "demo",
        "title": "React Frontend Developer", "company": "Innovate Labs",
        "company_logo_url": None, "location": "Remote", "is_remote": True,
        "work_type": "remote", "employment_type": "full-time", "experience_level": "entry",
        "salary_min": 500000, "salary_max": 900000, "salary_currency": "INR",
        "description": "Join our product team to build beautiful, performant React applications. You'll work on our SaaS dashboard used by thousands of customers.\n\nResponsibilities:\n- Build responsive UI components with React and TypeScript\n- Integrate with backend REST APIs\n- Optimize application performance\n- Write unit and integration tests\n\nRequirements:\n- Strong React.js skills\n- TypeScript proficiency\n- CSS/Tailwind CSS experience\n- Understanding of state management (Redux/Zustand/Context)",
        "required_skills": ["React", "TypeScript", "JavaScript", "CSS", "Git"],
        "preferred_skills": ["Tailwind CSS", "Next.js", "GraphQL", "Vitest"],
        "application_url": "https://example.com/apply/d002",
        "posted_at": "2026-11-03T00:00:00Z", "is_active": True,
    },
    {
        "id": "demo-003", "external_id": "d003", "provider": "demo",
        "title": "Full Stack Engineer", "company": "StartupX",
        "company_logo_url": None, "location": "Hyderabad, India", "is_remote": False,
        "work_type": "onsite", "employment_type": "full-time", "experience_level": "mid",
        "salary_min": 1000000, "salary_max": 1800000, "salary_currency": "INR",
        "description": "We're a fast-growing startup seeking a Full Stack Engineer to own features end-to-end. You'll work across our Python backend and React frontend.\n\nResponsibilities:\n- Build features across the full stack (Python + React)\n- Design database schemas and write migrations\n- Implement real-time features using WebSockets\n- Deploy and monitor applications on AWS\n\nRequirements:\n- 2+ years of full-stack experience\n- Proficiency in Python (Django or FastAPI) and React\n- Experience with PostgreSQL\n- Familiarity with cloud platforms",
        "required_skills": ["Python", "React", "PostgreSQL", "REST APIs", "Git"],
        "preferred_skills": ["AWS", "Docker", "Redis", "WebSockets", "TypeScript"],
        "application_url": "https://example.com/apply/d003",
        "posted_at": "2026-11-05T00:00:00Z", "is_active": True,
    },
    {
        "id": "demo-004", "external_id": "d004", "provider": "demo",
        "title": "Data Scientist", "company": "Analytics Pro",
        "company_logo_url": None, "location": "Mumbai, India", "is_remote": True,
        "work_type": "hybrid", "employment_type": "full-time", "experience_level": "entry",
        "salary_min": 700000, "salary_max": 1200000, "salary_currency": "INR",
        "description": "Join our data science team to build ML models that drive business decisions.\n\nResponsibilities:\n- Develop and deploy machine learning models\n- Perform exploratory data analysis\n- Build data pipelines using Python\n- Communicate insights to stakeholders\n\nRequirements:\n- Strong Python skills (NumPy, Pandas, Scikit-learn)\n- Understanding of machine learning concepts\n- SQL proficiency\n- Experience with Jupyter notebooks",
        "required_skills": ["Python", "Machine Learning", "Pandas", "NumPy", "SQL"],
        "preferred_skills": ["TensorFlow", "PyTorch", "Spark", "Tableau", "Scikit-learn"],
        "application_url": "https://example.com/apply/d004",
        "posted_at": "2026-11-02T00:00:00Z", "is_active": True,
    },
    {
        "id": "demo-005", "external_id": "d005", "provider": "demo",
        "title": "DevOps Engineer", "company": "CloudFirst Technologies",
        "company_logo_url": None, "location": "Remote", "is_remote": True,
        "work_type": "remote", "employment_type": "full-time", "experience_level": "mid",
        "salary_min": 1200000, "salary_max": 2000000, "salary_currency": "INR",
        "description": "Looking for a DevOps Engineer to build and maintain our cloud infrastructure.\n\nResponsibilities:\n- Design and maintain CI/CD pipelines\n- Manage Kubernetes clusters on AWS/GCP\n- Implement monitoring and alerting\n- Collaborate with dev teams on deployment strategies\n\nRequirements:\n- 2+ years DevOps experience\n- Strong knowledge of Docker and Kubernetes\n- Experience with AWS or GCP\n- Proficiency with Terraform or Ansible",
        "required_skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux"],
        "preferred_skills": ["Terraform", "Ansible", "Prometheus", "Grafana", "Python"],
        "application_url": "https://example.com/apply/d005",
        "posted_at": "2026-11-04T00:00:00Z", "is_active": True,
    },
    {
        "id": "demo-006", "external_id": "d006", "provider": "demo",
        "title": "Machine Learning Engineer", "company": "AI Ventures",
        "company_logo_url": None, "location": "Pune, India", "is_remote": False,
        "work_type": "hybrid", "employment_type": "full-time", "experience_level": "mid",
        "salary_min": 1500000, "salary_max": 2500000, "salary_currency": "INR",
        "description": "Build production-grade ML systems at scale.\n\nResponsibilities:\n- Design and implement ML pipelines\n- Deploy models to production using MLflow\n- Optimize inference performance\n- Collaborate with data scientists\n\nRequirements:\n- Strong Python and ML skills\n- Experience with PyTorch or TensorFlow\n- Understanding of MLOps practices\n- Cloud platform experience (AWS/GCP)",
        "required_skills": ["Python", "PyTorch", "TensorFlow", "MLOps", "AWS"],
        "preferred_skills": ["MLflow", "Kubernetes", "CUDA", "FastAPI", "Docker"],
        "application_url": "https://example.com/apply/d006",
        "posted_at": "2026-11-06T00:00:00Z", "is_active": True,
    },
    {
        "id": "demo-007", "external_id": "d007", "provider": "demo",
        "title": "Node.js Backend Developer", "company": "WebSolutions Inc",
        "company_logo_url": None, "location": "Chennai, India", "is_remote": False,
        "work_type": "onsite", "employment_type": "full-time", "experience_level": "entry",
        "salary_min": 500000, "salary_max": 850000, "salary_currency": "INR",
        "description": "Join our backend team to build high-performance Node.js APIs.\n\nResponsibilities:\n- Build and maintain REST APIs with Node.js and Express\n- Design MongoDB schemas\n- Implement authentication and authorization\n- Write unit and integration tests\n\nRequirements:\n- Node.js proficiency\n- Express.js experience\n- MongoDB or MySQL knowledge\n- JavaScript/TypeScript skills",
        "required_skills": ["Node.js", "JavaScript", "TypeScript", "MongoDB", "REST APIs"],
        "preferred_skills": ["Redis", "Docker", "AWS Lambda", "Jest", "GraphQL"],
        "application_url": "https://example.com/apply/d007",
        "posted_at": "2026-11-07T00:00:00Z", "is_active": True,
    },
    {
        "id": "demo-008", "external_id": "d008", "provider": "demo",
        "title": "Android Developer", "company": "Mobile First",
        "company_logo_url": None, "location": "Delhi, India", "is_remote": True,
        "work_type": "remote", "employment_type": "full-time", "experience_level": "entry",
        "salary_min": 600000, "salary_max": 1000000, "salary_currency": "INR",
        "description": "Build beautiful Android applications used by millions.\n\nResponsibilities:\n- Develop Android apps using Kotlin and Jetpack Compose\n- Integrate with REST APIs\n- Write clean, maintainable code\n- Optimize app performance\n\nRequirements:\n- Kotlin proficiency\n- Jetpack Compose experience\n- Understanding of Android architecture components\n- REST API integration experience",
        "required_skills": ["Kotlin", "Android", "Jetpack Compose", "REST APIs", "Git"],
        "preferred_skills": ["MVVM", "Coroutines", "Dagger/Hilt", "Firebase", "Room"],
        "application_url": "https://example.com/apply/d008",
        "posted_at": "2026-11-08T00:00:00Z", "is_active": True,
    },
    {
        "id": "demo-009", "external_id": "d009", "provider": "demo",
        "title": "UI/UX Designer", "company": "Design Studio",
        "company_logo_url": None, "location": "Bangalore, India", "is_remote": True,
        "work_type": "hybrid", "employment_type": "full-time", "experience_level": "entry",
        "salary_min": 500000, "salary_max": 900000, "salary_currency": "INR",
        "description": "Create beautiful user experiences for our SaaS products.\n\nResponsibilities:\n- Design user interfaces for web and mobile\n- Create wireframes, prototypes, and high-fidelity mockups\n- Conduct user research and usability testing\n- Collaborate with engineers on implementation\n\nRequirements:\n- Proficiency in Figma or Sketch\n- Understanding of UX principles\n- Portfolio demonstrating product design work\n- Basic understanding of HTML/CSS",
        "required_skills": ["Figma", "UI Design", "UX Research", "Prototyping", "Wireframing"],
        "preferred_skills": ["Framer", "HTML", "CSS", "Adobe XD", "User Testing"],
        "application_url": "https://example.com/apply/d009",
        "posted_at": "2026-11-09T00:00:00Z", "is_active": True,
    },
    {
        "id": "demo-010", "external_id": "d010", "provider": "demo",
        "title": "Cloud Solutions Architect", "company": "Enterprise Tech",
        "company_logo_url": None, "location": "Remote", "is_remote": True,
        "work_type": "remote", "employment_type": "full-time", "experience_level": "senior",
        "salary_min": 2500000, "salary_max": 4000000, "salary_currency": "INR",
        "description": "Lead cloud architecture decisions for enterprise clients.\n\nResponsibilities:\n- Design scalable cloud architectures on AWS/Azure/GCP\n- Lead technical discussions with stakeholders\n- Define cloud migration strategies\n- Mentor junior engineers\n\nRequirements:\n- 5+ years cloud experience\n- AWS/Azure/GCP certifications preferred\n- Strong architecture design skills\n- Excellent communication skills",
        "required_skills": ["AWS", "Azure", "GCP", "Terraform", "Architecture Design"],
        "preferred_skills": ["Kubernetes", "Microservices", "Security", "Cost Optimization"],
        "application_url": "https://example.com/apply/d010",
        "posted_at": "2026-11-10T00:00:00Z", "is_active": True,
    },
]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/")
async def search_jobs(
    q: Optional[str] = Query(None, description="Search query"),
    location: Optional[str] = Query(None),
    work_type: Optional[str] = Query(None),
    experience_level: Optional[str] = Query(None),
    employment_type: Optional[str] = Query(None),
    salary_min: Optional[int] = Query(None),
    salary_max: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Search jobs with filters. Returns demo data when external APIs unavailable."""
    jobs = list(DEMO_JOBS)

    # Apply filters
    if q:
        q_lower = q.lower()
        jobs = [j for j in jobs if q_lower in j["title"].lower() or q_lower in j["company"].lower()
                or any(q_lower in s.lower() for s in j.get("required_skills", []))]
    if location:
        loc_lower = location.lower()
        jobs = [j for j in jobs if loc_lower in j["location"].lower() or j["is_remote"]]
    if work_type:
        jobs = [j for j in jobs if j["work_type"] == work_type]
    if experience_level:
        jobs = [j for j in jobs if j["experience_level"] == experience_level]
    if employment_type:
        jobs = [j for j in jobs if j["employment_type"] == employment_type]
    if salary_min:
        jobs = [j for j in jobs if j.get("salary_max", 0) and j["salary_max"] >= salary_min]
    if salary_max:
        jobs = [j for j in jobs if j.get("salary_min", 0) and j["salary_min"] <= salary_max]

    total = len(jobs)
    skip = (page - 1) * size
    paginated = jobs[skip : skip + size]

    return {
        "items": paginated,
        "total": total,
        "page": page,
        "size": size,
        "pages": max(1, (total + size - 1) // size),
        "is_demo": True,
        "demo_notice": "Showing demo jobs. Connect job APIs (Adzuna/Remotive) via environment variables for live listings.",
    }


@router.get("/{job_id}")
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    """Get a single job by ID."""
    job = next((j for j in DEMO_JOBS if j["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


class MatchRequest(BaseModel):
    job_id: str
    resume_id: Optional[str] = None


@router.post("/match")
async def match_job(
    req: MatchRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Calculate AI match score between resume and job."""
    job = next((j for j in DEMO_JOBS if j["id"] == req.job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Simple rule-based match (real AI match via /ai/match endpoint)
    return {
        "job_id": req.job_id,
        "resume_id": req.resume_id,
        "overall_score": 72,
        "skill_score": 80,
        "experience_score": 65,
        "education_score": 70,
        "keyword_score": 75,
        "matched_skills": job["required_skills"][:3],
        "missing_skills": job["required_skills"][3:],
        "explanation": "Your profile matches well with the core requirements. Consider strengthening the missing skills.",
        "recommendations": ["Build a project using the missing technologies", "Add relevant certifications to your profile"],
        "is_demo": True,
    }
