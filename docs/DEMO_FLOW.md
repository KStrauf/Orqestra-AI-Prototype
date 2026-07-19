# Demo Flow

The primary demo is a single happy-path run that takes roughly three minutes and requires no cloud credentials.

## Setup

1. Start the backend with the documented script, or use the frontend's default demo mode.
2. Confirm the Studio workspace is open and the runtime indicator is visible.
3. Use the seeded example or enter the following narrative: create an approval-ready launch post from supplied build notes.

## Live sequence

1. Enter a clear goal in the composer.
2. Paste source material that contains the facts the drafts must use.
3. Run the workflow and call out the visible `Architect → Specialist → Reviewer` pipeline.
4. Open the Architect plan and show that it selected a small team.
5. Compare the direct and reflective Specialist variants.
6. Read the Reviewer notes, emphasizing that the system identifies risks before a human decision.
7. Edit the preferred draft, record the decision, and point out that the run remains locally persisted.
8. Reopen or show the run record and identify the provider, model, timestamps, input fingerprint, decision, and diff.

## Backup path

If Ollama or the backend is unavailable, use deterministic demo mode. If a live run is unsuitable during recording, use a seeded fixture with the same goal, two variants, review text, and decision state. The narrative and visible controls must remain the same.

## Demo claims to make

- The system shows its work across multiple agents.
- Alternative drafts are deliberate outputs, not repeated single answers.
- Review is separate from generation.
- The human gate is explicit and durable.
- The model provider can change without changing the Studio experience.

## Claims to avoid

- Do not claim that the MVP publishes content automatically.
- Do not claim that OpenAI integration is already live.
- Do not imply that mock mode is a live model response.
