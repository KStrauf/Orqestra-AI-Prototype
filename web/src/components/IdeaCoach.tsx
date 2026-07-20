import { useState } from "react";
import { coachIdea } from "../api";
import type { IdeaCoachResult, IdeaDirection } from "../types";

interface IdeaCoachProps {
  idea: string;
  platform: string;
  audience: string;
  outcome: string;
  tone: string;
  brief: string;
  onAudienceChange: (value: string) => void;
  onOutcomeChange: (value: string) => void;
  onToneChange: (value: string) => void;
  onBriefChange: (value: string) => void;
}

function briefForDirection(result: IdeaCoachResult, direction: IdeaDirection): string {
  return [
    `Audience: ${result.audience}`,
    `Outcome: ${result.outcome}`,
    `Voice: ${result.tone}`,
    `Core idea: ${result.directions.find((item) => item.direction_id === direction.direction_id)?.title || ""}`,
    `Recommended direction: ${direction.title}`,
    `Format: ${direction.format}`,
    `Opening: ${direction.opening}`,
    `Next step: ${direction.next_step}`,
    "",
    "Assumption: Replace general statements with supplied facts, examples, or personal experience before approval.",
  ].join("\n");
}

export function IdeaCoach({
  idea,
  platform,
  audience,
  outcome,
  tone,
  brief,
  onAudienceChange,
  onOutcomeChange,
  onToneChange,
  onBriefChange,
}: IdeaCoachProps) {
  const [result, setResult] = useState<IdeaCoachResult | null>(null);
  const [selectedDirectionId, setSelectedDirectionId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function shapeIdea() {
    if (!idea.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const nextResult = await coachIdea({ idea, platform, audience, outcome, tone });
      setResult(nextResult);
      setSelectedDirectionId(nextResult.recommended_direction_id);
      onBriefChange(nextResult.starter_brief);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to shape this idea");
    } finally {
      setBusy(false);
    }
  }

  function selectDirection(direction: IdeaDirection) {
    if (!result) return;
    setSelectedDirectionId(direction.direction_id);
    onBriefChange(briefForDirection(result, direction));
  }

  const selectedDirection = result?.directions.find((direction) => direction.direction_id === selectedDirectionId);

  return (
    <section className="idea-coach" aria-labelledby="idea-coach-title">
      <div className="idea-coach-heading">
        <div>
          <span className="eyebrow">IDEA COACH</span>
          <h3 id="idea-coach-title">Shape the idea before drafting</h3>
        </div>
        <span className="idea-coach-step">02 / 03</span>
      </div>
      <p className="idea-coach-intro">You do not need a finished post or a brand voice. The team will suggest what to say, who it is for, and where to begin.</p>
      <div className="idea-coach-fields">
        <label>
          <span>Who is this for?</span>
          <input value={audience} onChange={(event) => onAudienceChange(event.target.value)} placeholder="e.g. new creators who want a clear starting point" />
        </label>
        <label>
          <span>What should it do?</span>
          <select value={outcome} onChange={(event) => onOutcomeChange(event.target.value)}>
            <option value="">Teach something useful</option>
            <option>Announce an update</option>
            <option>Start a conversation</option>
            <option>Build trust</option>
            <option>Drive people to take action</option>
          </select>
        </label>
        <label>
          <span>Voice</span>
          <select value={tone} onChange={(event) => onToneChange(event.target.value)}>
            <option>Clear and practical</option>
            <option>Warm and personal</option>
            <option>Bold and opinionated</option>
            <option>Educational</option>
          </select>
        </label>
      </div>
      <button className="secondary-button idea-coach-button" disabled={!idea.trim() || busy} onClick={shapeIdea} type="button">
        {busy ? "Finding useful directions…" : result ? "Refresh ideas →" : "Help me find an angle →"}
      </button>
      {error && <p className="idea-coach-error" role="alert">{error}</p>}
      {result && (
        <div className="idea-coach-result">
          <article className="coach-recommendation">
            <span className="eyebrow">RECOMMENDED DIRECTION</span>
            <h4>{result.directions.find((direction) => direction.direction_id === result.recommended_direction_id)?.title}</h4>
            <p>{result.recommendation}</p>
            <div className="coach-facts"><span>{result.audience}</span><span>{platform}</span><span>{result.outcome}</span></div>
          </article>
          <div className="coach-directions-heading">
            <div><span className="eyebrow">THREE WAYS TO TAKE IT</span><p>Choose the direction that feels most like what you want to say.</p></div>
          </div>
          <div className="coach-direction-list">
            {result.directions.map((direction) => (
              <button className={`coach-direction-card ${direction.direction_id === selectedDirectionId ? "selected" : ""}`} key={direction.direction_id} onClick={() => selectDirection(direction)} type="button">
                <span className="coach-direction-top"><strong>{direction.title}</strong><span>{direction.format}</span></span>
                <p>{direction.why_it_fits}</p>
                <small>{direction.opening}</small>
              </button>
            ))}
          </div>
          <article className="coach-sample">
            <div className="coach-sample-heading"><span className="eyebrow">SAMPLE STARTER POST</span><span>Use as a starting point, not a final draft</span></div>
            <p>{result.sample_post}</p>
            {selectedDirection && <button className="quiet-button" onClick={() => selectDirection(selectedDirection)} type="button">Use “{selectedDirection.title}” in my brief →</button>}
          </article>
          <div className="coach-assumptions"><span className="eyebrow">ASSUMPTIONS TO CHECK</span>{result.assumptions.map((assumption) => <span key={assumption}>• {assumption}</span>)}</div>
          <label className="brief-editor">
            <span>Editable starter brief <small>Adjust this before creating drafts.</small></span>
            <textarea value={brief} onChange={(event) => onBriefChange(event.target.value)} rows={8} />
          </label>
        </div>
      )}
    </section>
  );
}
