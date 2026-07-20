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
5. Content intelligence and demo hardening: creator context, hooks, quality benchmarks, artifacts, fixtures, smoke checks, screenshots, and freeze prep.

### Plan status — 2026-07-19

- **Phase 0:** complete.
- **Phase 1:** complete.
- **Phase 2:** complete.
- **Phase 3:** complete.
- **Phase 4:** complete.
- **Phase 5:** automated validation complete; final manual browser pass,
  screenshots, and branch freeze remain.

The next session is a release validation session, not another redesign cycle.
Any issue found must be classified as a submission blocker against
`docs/UX_BENCHMARK.md` before code is changed.

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
- Treat `docs/UX_BENCHMARK.md` as a release gate. Do not accept a surface that
  merely exposes metadata if it does not help a creator decide what to say or
  what to improve.
- When repeated UX findings show a mismatch between system capability and user
  mental model, fix the product language and the responsible agent contract
  together. Do not patch only the visual symptom.

## Definition of done for the hackathon

The product must be understandable from the UI, useful from an incomplete idea,
runnable locally without a cloud key, faithful to the documented Content
Architect → Specialist → Reviewer → Human flow, benchmarkable with explainable
checks, safe at the human gate, and supported by a clean test/demo handoff.
