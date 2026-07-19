# OrqestraAI

OrqestraAI is a production-shaped starter repository for an AI-powered business operations and finance workflow platform.

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
./scripts/start-backend.sh
```

The API is available at `http://localhost:8000` and can be checked with
`http://localhost:8000/health`.

Frontend (in a second terminal):

```bash
cd web
npm install
npm run dev
```

To connect the frontend to the backend instead of demo mode, create
`web/.env.local` with:

```bash
VITE_DEMO_MODE=false
VITE_API_URL=http://localhost:8000
```

## Local Admin

After seeding:
- username: `admin`
- password: `password123`

## Safety Boundary

This project uses mock business operations and finance data. It does not approve payments, contracts, compliance closure, or real financial actions.
