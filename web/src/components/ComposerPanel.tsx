import type { FormEvent } from "react";

interface ComposerPanelProps {
  goal: string;
  material: string;
  platform: string;
  busy: boolean;
  onGoalChange: (value: string) => void;
  onMaterialChange: (value: string) => void;
  onPlatformChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

export function ComposerPanel({
  goal,
  material,
  platform,
  busy,
  onGoalChange,
  onMaterialChange,
  onPlatformChange,
  onSubmit,
}: ComposerPanelProps) {
  return (
    <section className="composer-card" aria-labelledby="composer-title">
      <div className="section-heading">
        <div>
          <span className="eyebrow">NEW WORKFLOW</span>
          <h2 id="composer-title">What should the team create?</h2>
        </div>
        <span className="step-label">01 / 03</span>
      </div>
      <form onSubmit={onSubmit}>
        <label>
          <span>Goal</span>
          <input
            value={goal}
            onChange={(event) => onGoalChange(event.target.value)}
            placeholder="Describe the outcome you need"
          />
        </label>
        <label>
          <span>Source material</span>
          <textarea
            rows={3}
            value={material}
            onChange={(event) => onMaterialChange(event.target.value)}
            placeholder="Paste the facts, notes, or constraints the team should use"
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
        <div className="form-footer">
          <span className="helper-text">
            Plan, draft, review, then pause for your decision.
          </span>
          <button className="primary-button" disabled={busy} type="submit">
            {busy ? "Running team…" : "Run workflow  →"}
          </button>
        </div>
      </form>
    </section>
  );
}
