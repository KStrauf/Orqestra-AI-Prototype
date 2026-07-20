# Content Skill Adaptation

Orqestra Studio uses selected ideas from the Blotato content skills as
provider-neutral capabilities. The source skills are reference material, not
runtime agents and not dependencies of this repository.

## What is included now

- `brand_context`: optional creator audience, voice, CTA, point of view, story,
  and social-link context.
- `idea_coach`: turns an incomplete idea into a recommendation, three concrete
  content directions, a sample starter post, an editable brief, and assumptions
  to check before drafting.
- `hook_strategist`: records grounded hook directions for comparison.
- `post_writer`: gives the Specialist platform and brief context for distinct
  draft variants.
- `post_grader`: records transparent grounding, platform-fit, voice-fit, and
  actionability checks for the Reviewer.

The current run record preserves the skill versions, brand snapshot, hook
candidates, and quality report alongside the existing drafts and decisions.
The standalone `POST /api/studio/idea-coach` contract lets the composer coach an
idea before a run is created; demo mode returns the same structured shape
without requiring a provider.

## What is intentionally different

Orqestra does not promise virality, silently rewrite until a numeric threshold
is reached, or publish automatically. The Reviewer recommends; the human still
approves, edits, or rejects. Platform rules are conservative guidance and are
kept separate from provider prompts so they can be updated and tested.

## Deferred capabilities

- `repurpose` is represented as a future workflow mode. It must let the user
  choose target platforms and output count rather than force a fixed batch.
- `publish_handoff` is an export boundary for approved content.
- Direct scheduling integrations remain out of scope for the hackathon MVP.

## Runtime boundary

The existing Architect → Specialist → Reviewer → Human workflow remains the
orchestration boundary. Content capabilities are selected by stage; they are
not seven additional agents. Durable runs remain JSON records under the
existing `engine/runrecord.py` path, while the optional creator profile is
stored as `data/brand-profile.json` and snapshotted into runs.
