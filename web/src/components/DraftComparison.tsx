import type { Decision, Draft, StudioRun } from "../types";

interface DraftComparisonProps {
  run: StudioRun;
  selectedDraftId: string | null;
  onSelect: (draft: Draft) => void;
}

function decisionFor(run: StudioRun, draftId: string): Decision | undefined {
  return run.decisions.find((decision) => decision.draft_id === draftId);
}

function variantDescription(variant: string): string {
  const descriptions: Record<string, string> = {
    direct: "Clear claim and next action",
    reflective: "Connects the change to a lesson",
    educational: "Explains the idea step by step",
    contrarian: "Challenges the obvious framing",
  };
  return descriptions[variant.toLowerCase()] || "A distinct angle for comparison";
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
              aria-pressed={draft.draft_id === selectedDraftId}
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
              <span className="draft-angle">{variantDescription(draft.variant)}</span>
              <p>{draft.text}</p>
              <span className="draft-card-bottom">
                {draft.draft_id === selectedDraftId ? "Selected for review" : "Select to review →"} <span>{draft.chars} characters</span>
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}
