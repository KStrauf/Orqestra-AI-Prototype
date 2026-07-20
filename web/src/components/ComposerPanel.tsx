import type { FormEvent } from "react";
import { IdeaCoach } from "./IdeaCoach";

interface ComposerPanelProps {
  goal: string;
  material: string;
  platform: string;
  audience: string;
  outcome: string;
  tone: string;
  brief: string;
  busy: boolean;
  onGoalChange: (value: string) => void;
  onMaterialChange: (value: string) => void;
  onPlatformChange: (value: string) => void;
  onAudienceChange: (value: string) => void;
  onOutcomeChange: (value: string) => void;
  onToneChange: (value: string) => void;
  onBriefChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

export function ComposerPanel({
  goal,
  material,
  platform,
  audience,
  outcome,
  tone,
  brief,
  busy,
  onGoalChange,
  onMaterialChange,
  onPlatformChange,
  onAudienceChange,
  onOutcomeChange,
  onToneChange,
  onBriefChange,
  onSubmit,
}: ComposerPanelProps) {
  return (
    <section className="composer-card" aria-labelledby="composer-title">
      <div className="section-heading">
        <div>
          <span className="eyebrow">CREATE CONTENT</span>
          <h2 id="composer-title">Start with an idea.</h2>
        </div>
        <span className="step-label">01 / 03</span>
      </div>
      <form onSubmit={onSubmit}>
        <label>
          <span>What do you want to say?</span>
          <input
            value={goal}
            onChange={(event) => onGoalChange(event.target.value)}
            placeholder="Start with an idea, question, or outcome"
          />
        </label>
        <div className="idea-helper">
          <span className="field-help">Not sure what to post? Start with one sentence. The Architect will help find a useful angle.</span>
          <div className="idea-prompts" aria-label="Idea starters">
            <button type="button" onClick={() => onGoalChange("Announce a product or project update")}>Announce an update</button>
            <button type="button" onClick={() => onGoalChange("Turn one useful lesson into a post")}>Share a lesson</button>
            <button type="button" onClick={() => onGoalChange("Explain an idea to my audience")}>Explain an idea</button>
          </div>
        </div>
        <label>
          <span>Source material <small className="optional-label">optional</small></span>
          <textarea
            rows={3}
            value={material}
            onChange={(event) => onMaterialChange(event.target.value)}
            placeholder="Add notes, facts, links, or constraints if you have them"
          />
        </label>
        <label>
          <span>Content platform</span>
          <select value={platform} onChange={(event) => onPlatformChange(event.target.value)}>
            <option>LinkedIn</option>
            <option>X</option>
            <option>Instagram</option>
            <option>Facebook</option>
            <option>TikTok</option>
            <option>YouTube</option>
            <option>Lemon8</option>
            <option>Snapchat</option>
            <option>Spotify</option>
            <option>Amazon Podcasts</option>
            <option>Apple Podcasts</option>
            <option>Wondery</option>
          </select>
          <small className="field-help">Shapes the draft for this channel. Nothing publishes automatically.</small>
        </label>
        <IdeaCoach
          idea={goal}
          platform={platform}
          audience={audience}
          outcome={outcome}
          tone={tone}
          brief={brief}
          onAudienceChange={onAudienceChange}
          onOutcomeChange={onOutcomeChange}
          onToneChange={onToneChange}
          onBriefChange={onBriefChange}
        />
        <div className="form-footer">
          <span className="helper-text">
            Give the team an idea or a full brief. Plan, draft, review, then pause for your decision.
          </span>
          <button className="primary-button" disabled={busy} type="submit">
            {busy ? "Creating drafts…" : "Create drafts  →"}
          </button>
        </div>
      </form>
    </section>
  );
}
