# Requirements

## Functional requirements

### Composition

- Accept a non-empty idea or goal with optional source material.
- Preserve a material name/path label and a requested ordered list of variants.
- Accept platform, audience, outcome, tone, starter brief, and optional creator context.
- Reject a run with no variants before provider execution.

### Workflow

- Execute the current topology in order: Architect, Specialist fan-out, Reviewer.
- Pass the Architect plan to the Specialist.
- Produce one draft per requested variant.
- Give the Reviewer all generated drafts plus the goal and material.
- Stop in an approval-waiting state after review.
- Make explicit assumptions when a run starts without source material.
- Produce grounded hook directions before Specialist drafting.
- Help users who have only a rough idea by recommending a useful angle,
  showing multiple directions, and providing a sample starter post before
  they create drafts.
- Apply conservative platform checks without claiming engagement outcomes.
- Produce a structured, explainable content benchmark for grounding, platform fit,
  voice fit, actionability, and variant distinctness.

### Review and decisions

- Show draft text, variant, length, reviewer notes, and the Architect plan.
- Show content brief, hook directions, quality checks, and why a draft is being recommended.
- Show benchmark dimensions with their recommendations near the human review gate.
- Allow one decision per draft: approve, edit, or reject.
- Require non-empty edited text for an edit.
- Require a reason for a rejection.
- Preserve decision time, reason fields, edited text, and an edit diff when applicable.
- Never imply that an approval publishes content automatically.

### Persistence and traceability

- Persist every completed run durably and atomically.
- Retain input fingerprints, prompts, workflow/template identity, provider/model, usage, drafts, review, decisions, and status.
- Retain creator-profile snapshot, skill versions, hook candidates, and quality report.
- Make records readable after process restart.
- Keep existing records readable when optional fields are absent.

### Provider support

- Support deterministic mock inference for tests and offline demos.
- Support local Ollama inference with Qwen configuration through environment variables.
- Keep provider selection explicit and isolated from UI and orchestration code.
- Keep the OpenAI adapter behind the same contract; live OpenAI use requires explicit credentials and is not required for the MVP.

### Creator context

- Support durable audience, voice traits, primary CTA, point of view, story, and social-link context.
- Snapshot the context into each run so later profile edits do not change historical traceability.
- Never store social credentials in the creator profile.

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
- A user can start from an idea without first writing a finished brief.
- Hook directions and quality checks are visible without implying automatic approval.
- The benchmark helps a first-time creator understand what to improve without
  pretending to predict reach or engagement.
- A decision persists to the corresponding run record.
- Qwen/Ollama configuration is documented and covered by provider tests.
- Existing API routes and regression tests remain compatible.
