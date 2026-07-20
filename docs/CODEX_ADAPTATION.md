# Codex Adaptation Guide

This repository is an existing Studio MVP. Codex should evolve it in place.

## Repository constraints

- Work in `studio/`, `engine/`, `web/`, `tests/`, `scripts/`, and `docs/`.
- Do not invent `apps/api`, `packages/agents`, a new monorepo, or a replacement runtime.
- Treat `PROJECT.md` as the current handoff and implementation snapshot.
- Treat this `docs/` set as the durable product and engineering source of truth.
- Preserve passing tests and keep existing Studio routes working through backward-compatible additions.

## Required phase order

1. Source-of-truth reset: docs and root README only.
2. Studio backend contract: schemas, run lifecycle, list/history, and normalized errors.
3. Provider abstraction: Qwen/Ollama first, OpenAI-ready second, with trace metadata.
4. Frontend workspace: components, API client, history, pipeline, decisions, and trace views.
5. Content intelligence and demo hardening: creator context, hooks, quality checks, artifacts, fixtures, smoke checks, screenshots, and freeze prep.

After each phase, stop and report changed files, rationale, commands, test results, remaining risks, and the recommended next phase.

## Implementation rules

- Prefer small, reviewable additive patches.
- Read the current implementation before changing contracts.
- Put orchestration in `studio/`, provider/config/persistence in `engine/`, and UI behavior in `web/`.
- Keep `engine/runrecord.py` as the durable source of truth.
- Keep provider-specific details behind `TextProvider`.
- Add regression coverage for every new contract or invariant.
- Make failures explicit and user-visible without leaking secrets.
- Do not expand the MVP into publishing, authentication, distributed execution, or unrelated business workflows.
- Adapt external content skills selectively into provider-neutral contracts. Do not copy their filesystem assumptions, vendor integrations, automatic scheduling, virality guarantees, or hidden rewrite loops.
- Keep content capabilities inside the existing Architect → Specialist → Reviewer → Human boundary.

## Definition of done for the hackathon

The product must be understandable from the UI, runnable locally without a cloud key, faithful to the documented Architect → Specialist → Reviewer flow, safe at the human gate, and supported by a clean test/demo handoff.
