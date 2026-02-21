# EPC Digital Admission Portal + Question Paper Practice Platform

All-in-one platform for digital admissions (Student / College / Associate / Admin) with integrated AI-assisted question paper practice from last 10 years PDFs uploaded by admin.

## Core Product Flows
- Landing + Auth with role selection
- Student panel: profile, college search/compare, apply, admission status, finance, and question-paper practice
- College panel: institute profile, applications, analytics
- Associate panel: lead management, commission tracking
- Admin panel: verifications, rankings, CRM/finance, and past paper ingestion pipeline
- AI layer: OCR extraction, question-block parsing, blueprint inference, similar paper generation

## Backend (FastAPI + PostgreSQL)
### Implemented APIs
- Auth: `/auth/register`, `/auth/login`
- Dashboards: `/dashboards/student`, `/dashboards/college`, `/dashboards/associate`, `/dashboards/admin`
- Admission: `/applications`, `/applications/me`, `/applications/{id}/status`
- Associate: `/associates/leads`
- Ranking: `/admin/rankings`
- Search: `/colleges/search`
- Question Bank: `/questions`, `/questions/{id}/verify`
- Templates: `/templates`
- Papers: `/papers/generate`, `/papers/{id}`, `/papers/{id}/download`, `/papers/{id}/answerkey`
- Practice pipeline:
  - `/admin/past-papers/upload`
  - `/admin/past-papers/{paper_id}/ingest`
  - `/students/practice/papers`
  - `/students/practice/generate-from-paper/{paper_id}`
- Tests: `/tests/start`, `/tests/{id}/answer`, `/tests/{id}/submit`
- Analytics: `/students/{id}/analytics`

### Database
Includes original MVP tables and EPC extension tables:
- `college_profiles`, `admission_applications`, `student_documents`, `verification_tasks`,
  `associate_leads`, `associate_commissions`, `ranking_snapshots`, `past_papers`, `ai_insights`.

## Frontend (Next.js + Tailwind)
Routes added for all EPC roles and linked pages:
- `/`, `/auth`
- `/student/*`, `/college/*`, `/associate/*`, `/admin/*`

## Run
```bash
docker compose up --build
```
- API docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`

## Local backend setup
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload
```

## Seed Users
Password for all seeded users: `pass123`
- admin@example.com (ADMIN)
- student@example.com (STUDENT)
- college@example.com (COLLEGE)
- associate@example.com (ASSOCIATE)
