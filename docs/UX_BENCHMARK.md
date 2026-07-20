# Orqestra Studio UX and Content Benchmark

## Purpose

Orqestra Studio is an AI-powered, UX-first content platform. Its quality bar
is not whether it can produce text. The bar is whether a creator with only an
idea can understand what to do, receive materially useful content directions,
and see why the system recommends or flags a draft.

The benchmark is an editorial review aid. It is not a virality score,
engagement prediction, or automatic approval threshold.

## Client test

Before the hackathon freeze, a first-time user should be able to answer these
questions without an explanation from the builder:

1. What can I create here?
2. What should I enter if I only have an idea?
3. What did each agent contribute?
4. Why are these drafts different?
5. What does the benchmark say I should review?
6. What remains my decision?

If the answer is unclear, the issue is a product defect, not a documentation
problem.

## Benchmark dimensions

The Reviewer records transparent checks for:

- **Grounding** — whether the work is tied to supplied material or clearly
  labels idea-only assumptions.
- **Platform fit** — whether the structure and length fit the selected channel.
- **Voice fit** — whether saved creator context is available and reflected.
- **Actionability** — whether the draft gives the audience a useful next step.
- **Distinctness** — whether alternatives begin from meaningfully different
  editorial directions; repeated openings are called out as a risk.

Scores are persisted in `quality_report` with issues and recommendations. The
UI must show the score alongside its explanation and must never present it as a
promise of performance.

## UX acceptance gates

### Composer

- Empty fields use placeholders, not text the user must delete.
- A user can submit a one-sentence idea without a finished brief or brand voice.
- Idea Coach can produce concrete directions, a sample starter post, an
  editable brief, and assumptions to verify.

### Run workspace

- The content task is visually primary; agent metadata is supportive.
- Direct, reflective, and educational drafts are visibly distinct and each has
  a clear angle.
- The selected draft, benchmark, Reviewer notes, and human decision controls
  are easy to find.
- Approve, edit, and reject remain explicit human actions.

### Trace and history

- Architect → Specialist → Reviewer → Human is understandable in seconds.
- Trace shows contributions and evidence before raw metadata.
- Long source material is collapsed by default.
- Run facts use label/value spacing and never concatenate into a single word.

### Settings

- Settings teaches Orqestra about the creator before asking for optional links.
- Audience, voice, CTA, point of view, and story are the primary context.
- Social channels are grouped and collapsed unless configured.
- Save state is visible and profile links are never treated as credentials.

## Disqualifiers

The submission is not ready if:

- the Specialist mostly repeats the user's request instead of transforming it;
- the three variants are only cosmetic rewrites;
- the benchmark is a fixed decorative number with no review evidence;
- the interface reads like a custom-agent builder or workflow editor;
- the primary Run or Trace surface becomes a long, unstructured report;
- the human approval boundary is unclear; or
- empty panels, missing notes, or unexplained whitespace make the system feel
  unfinished.

## Source of truth

This benchmark is the UX quality gate for the hackathon. Product scope is in
`TARGET_PRODUCT.md`, runtime behavior is in `BUSINESS_LOGIC.md`, and the
current handoff status is in `PROJECT.md`.
