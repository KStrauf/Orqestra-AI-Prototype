# Target Product: Orqestra Studio

## Product statement

Orqestra Studio is a small, transparent workspace for directing a goal and source material through a configured team of AI agents. It makes the plan, handoffs, draft variants, reviewer feedback, provider, and human decision visible in one place.

The product is designed around a simple promise: AI can do useful creative work while a person retains context and control before anything leaves the workspace.

## Primary user

The primary user is a solo creator, operator, or small team member who needs a publishable content artifact but wants to review how it was produced. The hackathon judge should be able to understand the workflow without knowing the repository or the underlying model provider.

## Core experience

1. Enter a concrete goal and paste or name the supporting material.
2. Run a configured Architect → Specialist → Reviewer workflow.
3. Inspect the Architect's plan, multiple Specialist drafts, and Reviewer notes.
4. Approve, edit, or reject a selected draft.
5. Reopen the durable run record and understand what happened.

## Product qualities

- Reviewable: intermediate work is shown instead of being hidden behind one final answer.
- Grounded: drafts are expected to use the supplied material and identify assumptions.
- Human-controlled: the workflow pauses at the decision gate.
- Traceable: each run records inputs, model/provider metadata, prompts, outputs, decisions, and timing.
- Replaceable: orchestration depends on a small text-provider contract, not a vendor SDK.
- Demo-friendly: a new judge can reach the value proposition in one happy-path run.

## MVP definition

The hackathon MVP is complete when a user can run the content workflow locally, see at least two draft variants and reviewer feedback, record a decision, and find the resulting JSON run record without any automatic external action.
