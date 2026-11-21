# ApplyMate AI — Master Specification

## Project Root
`c:\Users\SS\OneDrive\Desktop\Ai-Jobapp\`

## Monorepo Structure
```
Ai-Jobapp/
├── frontend/          # React + Vite + TypeScript + Tailwind + shadcn/ui
├── backend/           # Python + FastAPI + SQLAlchemy + Alembic
├── docs/              # Architecture diagrams, ER diagrams, etc.
├── .env.example
├── docker-compose.yml
└── README.md
```

## Tech Stack
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, shadcn/ui, Lucide React, React Router DOM v6, TanStack Query v5, React Hook Form, Zod, Recharts, Axios
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, python-jose (JWT), passlib (bcrypt), python-multipart
- **Database**: PostgreSQL via Supabase (or local Docker PostgreSQL)
- **AI**: Google Gemini API (primary), OpenAI (optional) — via env vars
- **File Storage**: Supabase Storage
- **Job APIs**: Adzuna, Remotive, Arbeitnow (all via env vars with demo fallback)

## Design System
- Dark navy (#0f172a) + charcoal (#1e293b) backgrounds
- Purple (#8b5cf6) + electric blue (#3b82f6) accents
- Light mode: white/gray-50 backgrounds
- Font: Inter
- Rounded-xl cards, subtle shadows, smooth transitions

## Key Pages/Routes (Frontend)
- `/` — Landing page
- `/auth/login` — Login
- `/auth/register` — Register
- `/auth/forgot-password` — Forgot password
- `/app/dashboard` — Main dashboard (protected)
- `/app/resumes` — Resume management
- `/app/jobs` — Job discovery
- `/app/jobs/:id` — Job details
- `/app/agent` — AI Agent workspace
- `/app/tracker` — Application tracker (Kanban + Table)
- `/app/saved` — Saved jobs
- `/app/interview` — Interview preparation
- `/app/analytics` — Analytics dashboard
- `/app/settings` — Settings & profile

## Backend API Base: `/api/v1/`
All endpoints require JWT Bearer token except auth routes.

## Environment Variables (never hardcode)
```
# Database
DATABASE_URL=postgresql+asyncpg://...

# JWT
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# AI
GEMINI_API_KEY=
OPENAI_API_KEY=

# Supabase
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=
SUPABASE_STORAGE_BUCKET=applymate-files

# Job APIs
ADZUNA_APP_ID=
ADZUNA_API_KEY=
REMOTIVE_API_URL=https://remotive.com/api/remote-jobs
ARBEITNOW_API_URL=https://www.arbeitnow.com/api/job-board-api

# App
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
ENVIRONMENT=development
```

## Database Models (20 tables)
1. users
2. user_profiles  
3. resumes
4. resume_versions
5. extracted_resume_data
6. jobs
7. job_providers
8. job_matches
9. saved_jobs
10. applications
11. application_notes
12. cover_letters
13. generated_documents
14. ai_conversations
15. ai_conversation_messages
16. agent_tasks
17. notifications
18. subscription_plans
19. user_subscriptions
20. usage_records

## AI Features
1. Resume parsing (extract structured data from PDF/DOCX)
2. Resume analysis (score 0-100, section scores, suggestions)
3. Job matching (hybrid rule-based + semantic, 0-100 score)
4. Cover letter generation (tone-aware, job+resume context)
5. Resume tailoring (optimize without fabricating)
6. AI Agent (tool-calling orchestration)
7. Interview preparation (Q&A generation + mock interview)
8. Weekly career report

## Application Statuses
Interested → Saved → Applied → Assessment → Interview Scheduled → Interview Completed → Offer Received → Rejected → Withdrawn

## Subscription Plans
- Free: 2 resume uploads, 5 AI analyses/month, basic tracker
- Pro: 10 uploads, 50 AI analyses, all AI features
- Premium: Unlimited uploads, 200 AI analyses, advanced agent workflows
