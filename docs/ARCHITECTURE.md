# Architecture

## System shape

Orqestra Studio is a top-level Python + Vite application. The existing repository shape is part of the contract:

```text
web/  →  studio/api.py  →  studio/workflow.py  →  engine/providers/
                                      ↓
                              engine/runrecord.py
```

- `web/` is the presentation layer and API client. It may use deterministic demo data when configured for demo mode.
- `studio/api.py` exposes the HTTP boundary for health, run creation, run retrieval, and decisions.
- `studio/workflow.py` compiles the configured workflow, resolves agent manifests, calls the provider, creates drafts/review output, and writes a `RunRecord`.
- `studio/manifest.py` loads declarative YAML agent definitions from `studio/agents/`.
- `studio/plan.py` defines and validates the current `content_workflow` topology.
- `engine/providers/` owns the normalized text-completion protocol and provider adapters.
- `engine/config.py` loads environment-backed settings.
- `engine/runrecord.py` is the durable JSON source of truth.

## Execution flow

1. The composer sends a goal, material, material name, and variant names.
2. The Architect receives the goal and available template information and returns an agent plan.
3. The Specialist receives the goal, material, plan, and one variant at a time; the workflow fans out into drafts.
4. The Reviewer receives the goal, material, and all drafts and returns review notes.
5. The workflow records provider/model metadata, inputs, prompts, usage, drafts, plan, review, and `awaiting_approval` status.
6. A human decision is appended to the same record. Publication is not part of the Studio MVP.

## Persistence

Run records are JSON files under `data/runs/YYYY-MM-DD/<run_id>.json`. Writes are atomic through a temporary sibling file and replacement. The JSON records remain authoritative if an index or database is added later; any derived index must be rebuildable.

## Provider boundary

The orchestration layer depends only on `TextProvider.complete(...)` returning `ProviderReply`. The provider name, selected model, usage, and cost-estimate flag are retained for traceability. `mock` is deterministic; `ollama` is the Qwen-first local adapter. An OpenAI adapter belongs in `engine/providers/` and must not require frontend or workflow changes.

## Compatibility direction

The current Studio routes and run-record shape are preserved through additive changes. Backend schema extraction, list/history support, normalized errors, richer traces, and provider metadata are Phase 1–4 enhancements, not reasons to replace the existing layers.
