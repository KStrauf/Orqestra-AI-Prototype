# Orqestra Studio web

This is the first frontend slice for Orqestra Studio: a Vite + React + TypeScript review workspace.

## Run locally

```bash
npm install
npm run dev
```

The app starts in demo mode by default, so it does not require the Python service or an API key. To use the future HTTP service, create `web/.env.local`:

```bash
VITE_DEMO_MODE=false
VITE_API_URL=http://localhost:8000
```

The client expects `POST /api/studio/runs` and `POST /api/studio/runs/{run_id}/decisions`.
