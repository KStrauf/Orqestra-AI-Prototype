# Orqestra Studio

Orqestra Studio is a reviewable multi-agent content workspace for turning an idea or source material into platform-aware content directions and draft variants. An Architect shapes the brief, a Specialist produces drafts, and a Reviewer surfaces risks before a human approves, edits, or rejects a draft.

The hackathon MVP is deliberately small: it demonstrates useful agent handoffs, visible intermediate work, a hard human gate, provider-neutral inference, and durable local run records. Nothing is published automatically.

## What is included

- Idea-first composer with optional source material, audience, outcome, tone, platform, and creator context.
- Architect → Specialist → Reviewer workflow in `studio/`.
- Multiple named draft variants, including direct, reflective, and educational angles.
- Versioned content capabilities for idea coaching, grounded hooks, platform writing, and editorial checks.
- Durable creator profile context for audience, voice traits, CTA, point of view, stories, and social links.
- Reviewer notes and the Architect's plan shown alongside the drafts.
- Hook directions and an explainable Content Benchmark shown as review evidence, not engagement guarantees.
- Approve, edit, and reject decisions with durable JSON persistence.
- Deterministic mock inference for tests and a local Ollama adapter for Qwen-first development.
- Provider and model metadata recorded on each run.

## Repository map

```text
studio/       FastAPI routes, workflow orchestration, manifests, skills, and plans
engine/       Configuration, providers, content primitives, CLI, errors, and run persistence
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

The adapter uses Ollama's local `/api/chat` endpoint. OpenAI is available behind the same provider contract for later keyed use; it is not required for the current MVP.

## Current Studio API

- `GET /health`
- `POST /api/studio/runs`
- `GET /api/studio/runs`
- `GET /api/studio/runs/{run_id}`
- `POST /api/studio/runs/{run_id}/decisions`
- `GET /api/studio/brand-profile`
- `PUT /api/studio/brand-profile`

Run records are the source of truth and are written atomically under `data/runs/YYYY-MM-DD/`. Optional creator context is stored at `data/brand-profile.json` and snapshotted into each run.

## Product source of truth

Read the documents in `docs/` for the current product and implementation contract. `PROJECT.md` is a session handoff and implementation snapshot; it is useful context but is not the permanent product specification.

The product quality gate is [`docs/UX_BENCHMARK.md`](docs/UX_BENCHMARK.md), and
the accumulated team findings are preserved in
[`docs/TEAM_LESSONS.md`](docs/TEAM_LESSONS.md).

## Safety boundary

Orqestra Studio creates reviewable content artifacts. It does not publish, approve payments, close compliance work, or take other external business actions. Human approval is required before any future publication integration.
