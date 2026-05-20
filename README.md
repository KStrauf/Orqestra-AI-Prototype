His# OrqestraAI

—currently in development

It includes:
- Python FastAPI backend with SQLAlchemy models, JWT authentication, and mock AI analysis persistence.
- Vite React TypeScript frontend with task creation and AI analysis display.
- TypeScript agent runtime with command-driven meta-agent communication through a CLI.
- File-based message bus, session transcripts, handoff files, agent profiles, commands, skills, prompts, and schemas.

## Quick Start

```bash
npm install
npm run orqestra -- agents
npm run orqestra -- analyze "Vendor invoice is overdue and missing approval"
npm run orqestra -- transcript latest
npm run orqestra -- handoff latest
```

Backend:

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed.py
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
npm run dev:web
```

## Local Admin

After seeding:
- username: `admin`
- password: `password123`

## Safety Boundary

This project uses mock data not intended for operations, finance, or business use.
