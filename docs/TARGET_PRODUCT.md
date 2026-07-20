# Target Product: Orqestra Studio

## Product statement

Orqestra Studio is a transparent, UX-first AI content and benchmarking workspace for turning an idea, source material, or both into reviewable platform-native drafts. It makes the creative brief, agent handoffs, hook directions, draft variants, benchmark evidence, reviewer feedback, provider, and human decision visible in one place.

The product is designed around a simple promise: AI can do useful creative work while a person retains context and control before anything leaves the workspace.

## Primary user

The primary user is a solo creator, operator, or small team member who has an idea but may not yet know what to post, who it is for, or how to express it in their voice. The hackathon judge should understand the workflow without knowing the repository or underlying model provider.

## Core experience

1. Start with an idea, optionally add source material, and choose a platform.
2. Add audience, outcome, tone, or saved creator context, or let the Architect make explicit assumptions.
3. Run a configured Architect → Specialist → Reviewer workflow.
4. Inspect the brief, hook directions, multiple Specialist drafts, quality checks, and Reviewer notes.
5. Approve, edit, or reject a selected draft.
6. Reopen the durable run record and understand what happened.

The Reviewer benchmark is part of the product experience. It identifies where
to focus human attention; it does not predict engagement or replace judgment.

## Product qualities

- Reviewable: intermediate work is shown instead of being hidden behind one final answer.
- Grounded: drafts are expected to use the supplied material and identify assumptions.
- Helpful from a blank page: an incomplete idea becomes a usable brief and several directions.
- Human-controlled: the workflow pauses at the decision gate.
- Traceable: each run records inputs, model/provider metadata, prompts, outputs, decisions, and timing.
- Replaceable: orchestration depends on a small text-provider contract, not a vendor SDK.
- Demo-friendly: a new judge can reach the value proposition in one happy-path run.
- Benchmarkable: the work is evaluated with visible, explainable editorial checks.

## Product boundary

Orqestra Studio is for creating and reviewing content. It is not a custom-agent
builder, workflow editor, social scheduler, or automatic publishing system in
the hackathon MVP.

## MVP definition

The hackathon MVP is complete when a user can start from an idea, run the content workflow locally, see multiple distinct draft angles, hook directions, reviewer feedback, and quality checks, record a decision, and find the resulting JSON run record without any automatic external action.
