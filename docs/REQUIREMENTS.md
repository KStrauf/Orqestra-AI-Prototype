# Requirements

## Functional requirements

### Composition

- Accept a non-empty goal and non-empty source material.
- Preserve a material name/path label and a requested ordered list of variants.
- Reject a run with no variants before provider execution.

### Workflow

- Execute the current topology in order: Architect, Specialist fan-out, Reviewer.
- Pass the Architect plan to the Specialist.
- Produce one draft per requested variant.
- Give the Reviewer all generated drafts plus the goal and material.
- Stop in an approval-waiting state after review.

### Review and decisions

- Show draft text, variant, length, reviewer notes, and the Architect plan.
- Allow one decision per draft: approve, edit, or reject.
- Require non-empty edited text for an edit.
- Require a reason for a rejection.
- Preserve decision time, reason fields, edited text, and an edit diff when applicable.
- Never imply that an approval publishes content automatically.

### Persistence and traceability

- Persist every completed run durably and atomically.
- Retain input fingerprints, prompts, workflow/template identity, provider/model, usage, drafts, review, decisions, and status.
- Make records readable after process restart.
- Keep existing records readable when optional fields are absent.

### Provider support

- Support deterministic mock inference for tests and offline demos.
- Support local Ollama inference with Qwen configuration through environment variables.
- Keep provider selection explicit and isolated from UI and orchestration code.
- Add OpenAI behind the same contract only after the Qwen path is stable.

## Non-functional requirements

- Preserve the passing Python test suite after each phase.
- Prefer small additive patches over broad rewrites.
- Keep the core happy path understandable to a first-time demo viewer.
- Avoid logging or displaying secrets.
- Keep local development possible without an API key.
- Do not introduce external side effects into the MVP.

## Acceptance criteria for the submission MVP

- A fresh local setup can start the backend and frontend using documented commands.
- A user can complete the happy-path demo with mock inference and see the full pipeline.
- At least two variants are visible and selectable.
- A decision persists to the corresponding run record.
- Qwen/Ollama configuration is documented and covered by provider tests.
- Existing API routes and regression tests remain compatible.
