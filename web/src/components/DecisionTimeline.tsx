import type { Decision, StudioRun } from "../types";

interface DecisionTimelineProps {
  run: StudioRun;
}

function draftVariant(run: StudioRun, decision: Decision): string {
  return run.drafts.find((draft) => draft.draft_id === decision.draft_id)?.variant || decision.draft_id;
}

function explanation(decision: Decision): string {
  if (decision.decision === "approve") return "Human approval recorded after review.";
  if (decision.decision === "edit") return "Human revision recorded before any publication.";
  return "Human rejection recorded with rationale.";
}

export function DecisionTimeline({ run }: DecisionTimelineProps) {
  return (
    <section className="decision-history" aria-labelledby="decision-history-title">
      <div className="section-heading compact">
        <div>
          <span className="eyebrow">HUMAN HISTORY</span>
          <h3 id="decision-history-title">Decision timeline</h3>
        </div>
        <span className="count-label">{run.decisions.length} recorded</span>
      </div>
      {run.decisions.length === 0 ? (
        <div className="decision-history-empty">No human decision yet. The run is waiting at the review gate.</div>
      ) : (
        <div className="decision-history-list">
          {run.decisions.map((decision) => (
            <article className="decision-event" key={`${decision.draft_id}-${decision.at}`}>
              <span className={`decision-marker ${decision.decision}`} aria-hidden="true">{decision.decision === "approve" ? "✓" : decision.decision === "edit" ? "✎" : "×"}</span>
              <div>
                <div className="decision-event-heading">
                  <strong>{draftVariant(run, decision)}</strong>
                  <span className={`decision-tag ${decision.decision}`}>{decision.decision}</span>
                </div>
                <time className="artifact-meta" dateTime={decision.at}>{decision.at}</time>
                <p className="decision-explanation"><span className="eyebrow">WHY THIS DECISION</span>{explanation(decision)}</p>
                {decision.reason && <p className="decision-reason"><strong>Rationale:</strong> {decision.reason}</p>}
                {decision.edited_text && <p className="decision-edited"><strong>Edited artifact:</strong> {decision.edited_text}</p>}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
