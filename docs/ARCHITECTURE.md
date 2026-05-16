# Architecture

```text
React Web App -> FastAPI Backend -> SQLAlchemy Database
TypeScript CLI -> Agent Runtime -> JSONL Message Bus -> Transcript + Handoff
```

## Boundaries
- Backend owns application state.
- Agent runtime owns reasoning workflow and session trace.
- Frontend owns user interaction.
- CLI exposes agent communication for developer workflows.
