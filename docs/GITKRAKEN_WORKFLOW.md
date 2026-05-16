# GitKraken Workflow

## Branches
Use short-lived branches from `main`:
- `feature/agent-runtime`
- `feature/fastapi-backend`
- `feature/react-agent-trace`
- `feature/security-auth`
- `feature/demo-polish`

## Commit Pattern
`<area>: <clear change>`

Examples:
- `agents: add message bus`
- `api: add business task model`
- `web: add agent analysis panel`

## GitKraken Steps
1. Open repository in GitKraken.
2. Create a feature branch from `main`.
3. Stage related files only.
4. Review diffs before commit.
5. Commit frequently with focused messages.
6. Merge only after CLI, backend, and frontend smoke checks pass.
