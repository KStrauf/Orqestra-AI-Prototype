import type { Decision, Draft, StudioRun } from "../types";

interface DraftComparisonProps {
  run: StudioRun;
  selectedDraftId: string | null;
  onSelect: (draft: Draft) => void;
}

function decisionFor(run: StudioRun, draftId: string): Decision | undefined {
  return run.decisions.find((decision) => decision.draft_id === draftId);
}

export function DraftComparison({
  run,
  selectedDraftId,
  onSelect,
}: DraftComparisonProps) {
  const decidedCount = run.decisions.length;

  return (
    <section className="drafts-section" aria-labelledby="drafts-title">
      <div className="section-heading compact">
        <div>
          <span className="eyebrow">CANDIDATES</span>
          <h3 id="drafts-title">Compare and choose a draft</h3>
        </div>
        <span className="count-label">
          {decidedCount} / {run.drafts.length} decided
        </span>
      </div>
      <div className="draft-list">
        {run.drafts.map((draft) => {
          const decision = decisionFor(run, draft.draft_id);
          return (
            <button
              className={`draft-card ${draft.draft_id === selectedDraftId ? "selected" : ""}`}
              key={draft.draft_id}
              onClick={() => onSelect(draft)}
              type="button"
            >
              <div className="draft-card-top">
                <span>{draft.variant}</span>
                {decision && (
                  <span className={`decision-tag ${decision.decision}`}>
                    {decision.decision}
                  </span>
                )}
              </div>
              <p>{draft.text}</p>
              <span className="draft-card-bottom">
                {draft.chars} characters <span>↗</span>
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}
