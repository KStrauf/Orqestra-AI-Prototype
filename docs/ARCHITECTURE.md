# Architecture

## System shape

Orqestra Studio is a top-level Python + Vite application. The existing repository shape is part of the contract:

```text
web/  →  studio/api.py  →  studio/workflow.py  →  engine/providers/
                              ↓          ↓              ↓
                    studio/skills/  engine/content.py  engine/runrecord.py
```

- `web/` is the presentation layer and API client. It may use deterministic demo data when configured for demo mode.
- `studio/api.py` exposes the HTTP boundary for health, run creation/listing/retrieval, decisions, and creator profile context.
- `studio/workflow.py` compiles the configured workflow, resolves agent manifests, calls the provider, creates drafts/review output, and writes a `RunRecord`.
- `studio/manifest.py` loads declarative YAML agent definitions from `studio/agents/`.
- `studio/plan.py` defines and validates the current `content_workflow` topology.
- `studio/skills/` contains versioned content capability manifests. These are stage-owned capabilities, not additional top-level agents.
- `engine/providers/` owns the normalized text-completion protocol and provider adapters.
- `engine/content.py` owns brand-profile snapshots, platform guidance, hook candidates, and deterministic quality checks.
- `engine/config.py` loads environment-backed settings.
- `engine/runrecord.py` is the durable JSON source of truth.

## Execution flow

1. The composer sends an idea, optional material, platform, audience/outcome context, and optional creator profile.
2. The Architect shapes the creative brief, declares assumptions, and returns an agent plan.
3. The content capability layer creates grounded hook directions and platform guidance.
4. The Specialist receives the goal, material, plan, hook direction, and one variant at a time; the workflow fans out into drafts.
5. The Reviewer receives the goal, material, context, and all drafts and returns review notes plus deterministic quality checks.
6. The workflow records provider/model metadata, inputs, prompts, usage, drafts, hooks, quality report, plan, review, skill versions, and `awaiting_approval` status.
7. A human decision is appended to the same record. Publication is not part of the Studio MVP.

## Benchmark boundary

The Reviewer produces two related outputs: human-readable review notes and a
structured `quality_report`. The report is intentionally conservative and
provider-neutral. It checks grounding, platform fit, voice fit, actionability,
length constraints, and whether requested alternatives are meaningfully
distinct. The frontend presents these as a content benchmark with its method,
issues, and recommendations. It is not a model-confidence score, virality
prediction, or automatic approval gate.

The benchmark belongs at the review boundary because it explains why a human
should inspect or revise a draft. It must not silently rewrite content or
change the decision state.

## Persistence

Run records are JSON files under `data/runs/YYYY-MM-DD/<run_id>.json`. Writes are atomic through a temporary sibling file and replacement. The optional creator profile is stored at `data/brand-profile.json`, then snapshotted into runs. JSON remains authoritative if an index or database is added later; any derived index must be rebuildable.

## Provider boundary

The orchestration layer depends only on `TextProvider.complete(...)` returning `ProviderReply`. The provider name, selected model, usage, and cost-estimate flag are retained for traceability. `mock` is deterministic; `ollama` is the Qwen-first local adapter; OpenAI uses the same boundary. No provider is allowed to change the frontend content contract.

## Compatibility direction

The current Studio routes and run-record shape are preserved through additive changes. Backend schema extraction, list/history support, normalized errors, richer traces, and provider metadata are Phase 1–4 enhancements, not reasons to replace the existing layers.
