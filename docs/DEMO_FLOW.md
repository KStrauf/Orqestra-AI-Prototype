# Demo Flow

The primary demo is a single happy-path run that takes roughly three minutes and requires no cloud credentials.

## Setup

1. Start the backend with the documented script, or use the frontend's default demo mode.
2. Confirm the Studio workspace is open and the runtime indicator is visible.
3. Optionally open Settings and add one audience, two voice traits, and a social profile link.
4. Use the seeded example or enter the following idea: explain why visible review makes AI content safer to use.

## Live sequence

1. Enter the idea in the composer; explain that a finished brief is optional.
2. Optionally paste source material and select a target platform.
3. Run the workflow and call out the visible `Architect → Specialist → Reviewer` pipeline.
4. Open the content brief and hook directions to show how the idea becomes usable directions.
5. Compare the direct, reflective, and educational Specialist variants.
6. Read the Reviewer notes and quality checks, emphasizing that they surface risks rather than auto-approve.
7. Edit the preferred draft, record the decision, and point out that the run remains locally persisted.
8. Reopen or show the run record and identify the provider, model, skill versions, creator context snapshot, timestamps, decision, and diff.

## Backup path

If Ollama or the backend is unavailable, use deterministic demo mode. If a live run is unsuitable during recording, use a seeded fixture with the same idea, three variants, review text, and decision state. The narrative and visible controls must remain the same.

## Demo claims to make

- The system shows its work across multiple agents.
- Alternative drafts are deliberate outputs, not repeated single answers.
- Review is separate from generation.
- The human gate is explicit and durable.
- The model provider can change without changing the Studio experience.
- The content capability layer helps a user move from an idea to a reviewable post.

## Claims to avoid

- Do not claim that the MVP publishes content automatically.
- Do not claim that OpenAI integration is already live.
- Do not imply that mock mode is a live model response.
- Do not describe the quality signal as a prediction of virality or guaranteed performance.
