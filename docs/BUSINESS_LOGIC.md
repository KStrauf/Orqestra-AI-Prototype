# Business Logic

## Run lifecycle

```text
requested → executing → awaiting_approval → decided
                                      └──→ published (future/CLI-gated)
```

The current workflow persists the completed generation in `awaiting_approval`. Recording any valid decision changes the record to `decided`. Publication, where it exists in legacy CLI support, requires an approval or edit decision and is not an automatic Studio action.

## Invariants

- A run cannot execute with an empty goal. Source material is optional when the user has only an idea.
- An idea-only run must label assumptions and keep factual claims subject to human verification.
- Platform, audience, outcome, tone, and optional creator context shape the brief without becoming hidden provider state.
- A run must request at least one variant.
- Each draft has a stable ID scoped to its run.
- A draft can receive at most one decision.
- An edit must contain non-empty replacement text and stores a diff from the original.
- A rejection must contain a human reason.
- A rejected draft cannot be published.
- No publication can be recorded without a prior approve or edit decision.
- The original draft remains available after an edit; the edited text is a separate decision field.
- The run record retains enough metadata to explain which provider, model, prompts, inputs, and manifests produced the result.
- The run record retains the creator-profile snapshot, skill versions, hook candidates, and quality report used during review.

## Grounding and review rules

- The Specialist receives only the supplied material or idea context, goal, plan, creator context, and permitted instructions/tools.
- The Reviewer evaluates against the goal, supplied material or idea assumptions, platform, creator context, and review constraints.
- Reviewer output is advice, not an implicit rewrite or approval.
- The human decides whether a draft is acceptable, needs editing, or should be rejected.
- Hook candidates are alternatives for human comparison, not promises of virality.
- Quality scores are deterministic review signals based on supplied context and platform checks, not automatic approval thresholds.
- Benchmark issues and recommendations are advisory evidence for the human
  reviewer. A high score never records approval, and a low score never blocks
  a human edit or rejection decision.

## Provider rules

- Provider selection comes from environment-backed settings, not frontend logic.
- `mock` is deterministic and suitable for tests and fallback demos.
- `ollama` is the Qwen-first local inference path and carries zero local cost.
- Provider-specific model naming is resolved at the engine boundary.
- Provider failures are surfaced as provider errors and must not be disguised as successful runs.

## Persistence rules

- JSON run files under `data/runs/` are authoritative.
- Writes happen atomically so an interrupted write does not replace a valid record with a partial file.
- Optional fields remain backward-readable for older records.
- Any future index is derived state and must be rebuildable from JSON.
