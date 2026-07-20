# Orqestra Studio — Current Handoff

Updated: 2026-07-19

## Product north star

Orqestra Studio is an AI-powered, UX-first content and benchmarking platform.
A creator can bring one sentence, source material, or both. The Content
Architect shapes the idea, the Specialist produces distinct platform-aware
directions, the Reviewer benchmarks the work, and the human decides what is
approved, edited, or rejected.

This is not a custom-agent builder, workflow editor, social scheduler, or
automatic publishing product. The product must feel useful to a creator before
it feels impressive to an engineer.

The durable product and engineering contract is in `docs/`. This file is the
active implementation snapshot for the next session.

## Completed phases

### Phase 0 — Source of truth

- Replaced the stale finance-workflow README and filled the product, scope,
  architecture, requirements, agent, business-logic, demo, and Codex guidance.

### Phase 1 — Studio backend contract

- Formalized run, decision, detail, summary, list, and normalized error shapes.
- Preserved existing Studio endpoints and made durable persistence remain
  centered on `engine/runrecord.py`.

### Phase 2 — Provider abstraction

- Added one text-provider contract.
- Kept deterministic mock mode for tests and demos.
- Added Qwen-first local Ollama configuration and an OpenAI-ready adapter.
- Persisted provider, model, usage, and cost-estimate metadata.

### Phase 3 — Review workspace

- Built the Vite + React + TypeScript shell, responsive layout, tokens, typed
  API client, composer, pipeline, draft comparison, decision controls, history,
  settings, and trace surfaces.

### Phase 4 — Transparency and content intelligence

- Added creator context, Idea Coach, grounded hook directions, platform checks,
  quality benchmarking, artifact evidence, decision history, and trace views.
- Reframed the runtime Architect as a Content Architect so the product language
  matches the creator-facing mission.
- Improved deterministic demo drafts so they transform an idea into a hook,
  useful body, audience framing, and next action instead of echoing the request.

## Validation status

The current automated checks are green:

- Python regression suite: **52 tests passed**.
- Frontend TypeScript/Vite build: **passed** from `web/`.
- `git diff --check`: **passed**.
- Agent manifests load with the four runtime roles: Architect, Orchestrator,
  Specialist, and Reviewer.
- API smoke coverage has exercised run creation, durable retrieval, approve,
  edit, reject, and history listing.

The latest UX changes still need one manual browser pass after refresh. That is
the only open release gate before recording; no new feature work should begin
until that pass is complete.

## Current quality bar

Use `docs/UX_BENCHMARK.md` as the acceptance contract. In particular:

1. A first-time creator can start with only an idea.
2. The Specialist materially transforms the input and produces distinct angles.
3. The benchmark explains grounding, platform fit, voice fit, and actionability.
4. Trace shows Architect → Specialist → Reviewer → Human without becoming a
   long debug report.
5. Creator context is useful, optional, and separate from publishing credentials.
6. Nothing publishes automatically.

## Next-session plan

### Gate A — Manual browser validation

With backend and frontend running, hard-refresh the browser and verify:

- Dashboard quick starts and empty/recent states.
- Idea-only New Run flow, placeholders, Idea Coach, platform selection, and
  create-drafts action.
- Run Workspace: three distinct drafts, benchmark in context, selected draft,
  reviewer notes, and approve/edit/reject persistence.
- Trace: four-stage timeline, selected draft, workflow evidence, benchmark, and
  spaced Run Facts.
- Settings: creator context, collapsed social channels, save feedback, and no
  accidental credential language.

### Gate B — Demo freeze

- Select one polished happy-path run and one seeded backup run.
- Confirm mock mode recording path and Qwen/Ollama fallback instructions.
- Capture screenshots only after the browser pass.
- Freeze scope and use the smoke checklist in `docs/DEMO_FLOW.md`.

### Deferred after submission

- Live OpenAI validation and cost accounting.
- Repurposing across multiple platforms.
- Publishing, scheduling, authentication, hosted persistence, and deeper
  per-agent telemetry.

## Startup commands

Backend:

```bash
cd /Users/kimberlystrauf/Desktop/orqestra-ai-prototype
./scripts/start-backend.sh
```

Frontend:

```bash
cd /Users/kimberlystrauf/Desktop/orqestra-ai-prototype/web
npm run dev
```

Use `web/.env.local` with `VITE_DEMO_MODE=false` and
`VITE_API_URL=http://localhost:8000` to connect the frontend to the backend.

## Important files

- `studio/api.py` — FastAPI routes and backend contract.
- `studio/workflow.py` — Content Architect → Specialist → Reviewer orchestration.
- `studio/agents/` — runtime agent manifests.
- `engine/content.py` — creator context, hooks, platform guidance, and benchmark checks.
- `engine/providers/` — mock, Qwen/Ollama, and OpenAI-ready text providers.
- `engine/runrecord.py` — authoritative durable JSON runs and decisions.
- `web/src/components/` — creator workspace, review, trace, history, and settings UI.
- `docs/UX_BENCHMARK.md` — product quality gate.
- `docs/TEAM_LESSONS.md` — durable synthesis of previous team findings.
