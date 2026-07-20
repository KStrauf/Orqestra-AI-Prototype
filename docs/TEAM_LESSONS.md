# Team Lessons and Decisions

This document preserves the useful findings from the benchmark, frontend,
AI-platform, ML, engineering, TypeScript, Python, challenger, and QA reviews.
It is project memory for the hackathon handoff.

## Product position

- Orqestra Studio is for content creation and review, not custom sub-agent
  creation or arbitrary workflow editing.
- The user may arrive with only an idea. The product must help shape the
  audience, outcome, angle, sample post, and starter brief before drafting.
- The system earns trust by showing what the Architect, Specialist, Reviewer,
  and human each contributed.
- A benchmark is valuable only when it explains what to improve. It must not
  imply virality or guaranteed engagement.

## Repeated UX findings

- Long-form artifact and trace pages read as AI-generated reports. Evidence
  should be summarized first and expanded only when needed.
- Empty or optional fields must use placeholders. Prefilled copy that requires
  deletion creates friction and makes the platform feel scripted.
- Creator context belongs before social links. Social channels are optional and
  should not dominate the Settings page.
- The selected draft must be obvious, and each variant must communicate a
  different editorial purpose rather than merely a different label.
- Provider, model, cost, timestamps, and run facts need explicit label/value
  spacing and quiet visual priority.

## Engineering lessons

- Preserve the current repository shape and API contract. Make additive changes
  in `studio/`, `engine/`, `web/`, and `tests/`.
- Keep `engine/runrecord.py` authoritative for durable runs and decisions.
- Keep provider selection behind `TextProvider`; mock is the reliable demo,
  Qwen/Ollama is the local inference path, and OpenAI remains an adapter.
- External content skills are selectively adapted as stage-owned capabilities;
  they are not copied into the repository as vendor-specific agents.
- Reviewer output is advice. The human gate is the only approval authority.

## Meta-agent synthesis

The recurring failure was not missing functionality. It was a mismatch between
working internals and the user's mental model. The corrective rule is:

> Every new capability must be expressed first as a creator outcome, then as an
> agent contribution, then as persisted evidence, and only then as metadata or
> controls.

The Architect manifest was therefore reframed as a Content Architect, and the
benchmark is now visible in both the review context and trace surfaces.

## Memory status

No project-level agent-memory directory was present during this audit. These
lessons are intentionally stored in `docs/` so the next session has a durable,
reviewable handoff rather than relying on an unavailable memory store.
