# Orqestra Studio web

The frontend is a Vite + React + TypeScript review workspace. It keeps the core demo flow visible: compose a goal and source material, watch the Architect → Specialist → Reviewer pipeline, compare draft variants, record a human decision, and revisit runs from history.

## Run locally

```bash
npm install
npm run dev
```

The app starts in demo mode by default, so it does not require the Python service or an API key. Demo runs and their history live only in the current browser session.

To use the Studio HTTP service, create `web/.env.local`:

```bash
VITE_DEMO_MODE=false
VITE_API_URL=http://localhost:8000
```

The API-backed client uses:

- `POST /api/studio/runs` to create a workflow run.
- `GET /api/studio/runs?limit=20` to populate run history.
- `GET /api/studio/runs/{run_id}` to reopen a saved run.
- `POST /api/studio/runs/{run_id}/decisions` to record approve/edit/reject.

## Workspace routes

The lightweight hash router keeps the MVP dependency-free while providing stable workspace destinations:

- `#/` — Dashboard and quick starts.
- `#/runs/new` — New Run composer and workflow preview.
- `#/runs/{run_id}` — Run Workspace with pipeline, drafts, and decisions.
- `#/history` — Searchable/filterable durable run history.
- `#/trace/{run_id}` — Plain-language Architect/Specialist/Reviewer/human trace.
- `#/settings` — Informational environment and safety settings.

The desktop shell keeps orientation in the left rail, the primary task in the center, and trust/context signals on the right. On mobile it collapses to one pane with route-aware bottom tabs.

## Frontend slices

- `App.tsx` owns page state and coordinates API actions.
- `components/ComposerPanel.tsx` captures the goal and source material.
- `components/PipelinePanel.tsx` shows the three agent stages.
- `components/DraftComparison.tsx` presents selectable variants.
- `components/DecisionControls.tsx` owns the human gate controls.
- `components/ReviewPanel.tsx` shows reviewer notes, plan, and run facts.
- `components/RunHistory.tsx` shows saved runs and the current-session fallback.
- `components/DashboardPage.tsx`, `NewRunPage.tsx`, `HistoryPage.tsx`, `TracePage.tsx`, and `SettingsPage.tsx` provide the workspace destinations.
- `routes.ts` provides the dependency-free hash route mapping.
- `api.ts` keeps demo/API switching and the backend contract in one place.

Build the production bundle with:

```bash
npm run build
```
