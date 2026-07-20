# Hackathon Scope

## In scope

- A polished Studio workspace for one content workflow.
- Idea-first composition with optional source material, audience, outcome, tone, platform, and creator context.
- Architect planning, Specialist fan-out into multiple variants, and Reviewer analysis.
- Grounded hook directions and conservative platform-fit checks.
- Durable creator profile context for voice, audience, CTA, point of view, stories, and social links.
- Visible draft comparison and reviewer notes.
- Human approve, edit, and reject controls.
- Durable local run and decision history.
- Agent manifests and workflow topology that are readable and testable.
- Deterministic mock inference for reliable demos and tests.
- Qwen through local Ollama as the first real inference path.
- A provider contract that can accept an OpenAI adapter later.
- Versioned content capability manifests owned by the existing workflow stages.
- A clear demo script, seeded fallback content, and local setup instructions.

## Explicitly out of scope for the MVP

- Automatic publishing or any external side effect.
- A full repurposing batch workflow or social scheduling integration.
- Payments, finance approvals, compliance closure, or business-system mutation.
- A general-purpose workflow builder or arbitrary DAG editor.
- Multi-user accounts, authentication, authorization, or hosted deployment.
- Production queues, distributed workers, streaming, or background job infrastructure.
- Training or fine-tuning a model.
- A mandatory OpenAI dependency or cloud API key.
- Replacing the current repository with a monorepo or introducing `apps/api` or `packages/agents`.

## Submission narrative

The demo should show that Orqestra is more than a text box: the system turns one idea into a small accountable content team, shapes the brief, offers grounded hooks and distinct platform-aware alternatives, asks a reviewer to identify risks, and leaves the final decision with a human.

## Scope rule

Every addition must improve the happy-path workflow, explainability, reliability, or demo readiness. If a feature does not support those outcomes, defer it until after the hackathon freeze.
