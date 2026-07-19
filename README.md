# Orqestra Studio

Orqestra Studio is a reviewable multi-agent content workflow for turning a goal and source material into several draft variants. An Architect plans the work, a Specialist produces drafts, and a Reviewer surfaces risks before a human approves, edits, or rejects a draft.

The hackathon MVP is deliberately small: it demonstrates useful agent handoffs, visible intermediate work, a hard human gate, provider-neutral inference, and durable local run records. Nothing is published automatically.

## What is included

- Goal and source-material composer in the Vite + React frontend.
- Architect → Specialist → Reviewer workflow in `studio/`.
- Multiple named draft variants, currently `direct` and `reflective` by default.
- Reviewer notes and the Architect's plan shown alongside the drafts.
- Approve, edit, and reject decisions with durable JSON persistence.
- Deterministic mock inference for tests and a local Ollama adapter for Qwen-first development.
- Provider and model metadata recorded on each run.

## Repository map

```text
studio/       FastAPI routes, workflow orchestration, manifests, and plans
engine/       Configuration, providers, CLI, errors, and run persistence
web/          Vite + React + TypeScript Studio workspace
tests/        Python regression tests
docs/         Product, scope, architecture, requirements, and demo source of truth
scripts/      Local startup helpers
data/runs/    Gitignored durable run records created during local use
```

## Quick start

Create or activate the project environment, then install Python dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Start the backend:

```bash
./scripts/start-backend.sh
```

The API runs at `http://localhost:8000`; liveness is available at `/health`.

In a second terminal, start the frontend:

```bash
cd web
npm install
npm run dev
```

The frontend uses demo mode by default. To connect it to the local API, create `web/.env.local`:

```bash
VITE_DEMO_MODE=false
VITE_API_URL=http://localhost:8000
```

Run the backend regression suite from the repository root:

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

## Qwen-first local inference

The default provider is deterministic `mock`, which keeps tests and the UI demo reliable. For local model development, run Ollama separately, make Qwen available, and use:

```bash
ORQ_PROVIDER=ollama
ORQ_OLLAMA_MODEL=qwen3:1.7b
./scripts/start-backend.sh
```

The adapter uses Ollama's local `/api/chat` endpoint. OpenAI is a planned adapter behind the same provider contract; it is not required for the current MVP.

## Current Studio API

- `GET /health`
- `POST /api/studio/runs`
- `GET /api/studio/runs/{run_id}`
- `POST /api/studio/runs/{run_id}/decisions`

Run records are the source of truth and are written atomically under `data/runs/YYYY-MM-DD/`. The API contract will be stabilized and extended in Phase 1 without breaking these routes.

## Product source of truth

Read the documents in `docs/` for the current product and implementation contract. `PROJECT.md` is a session handoff and implementation snapshot; it is useful context but is not the permanent product specification.

## Safety boundary

Orqestra Studio creates reviewable content artifacts. It does not publish, approve payments, close compliance work, or take other external business actions. Human approval is required before any future publication integration.
