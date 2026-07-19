import type { FormEvent } from "react";
import type { DecisionKind, Draft } from "../types";

interface DecisionControlsProps {
  draft: Draft;
  mode: DecisionKind | null;
  editText: string;
  reason: string;
  busy: boolean;
  hasDecision: boolean;
  onStart: (mode: DecisionKind) => void;
  onCancel: () => void;
  onEditTextChange: (value: string) => void;
  onReasonChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

export function DecisionControls({
  draft,
  mode,
  editText,
  reason,
  busy,
  hasDecision,
  onStart,
  onCancel,
  onEditTextChange,
  onReasonChange,
  onSubmit,
}: DecisionControlsProps) {
  return (
    <div className="decision-panel">
      <div className="decision-panel-heading">
        <div>
          <span className="eyebrow">HUMAN GATE</span>
          <h3>What should happen to this draft?</h3>
        </div>
        <span className="lock-label">⌑ Nothing publishes automatically</span>
      </div>
      {hasDecision && !mode ? (
        <p className="decision-recorded">A decision is already recorded for this draft.</p>
      ) : !mode ? (
        <div className="decision-actions">
          <button className="approve-button" onClick={() => onStart("approve")} type="button">
            Approve
          </button>
          <button className="edit-button" onClick={() => onStart("edit")} type="button">
            Edit draft
          </button>
          <button className="reject-button" onClick={() => onStart("reject")} type="button">
            Reject
          </button>
        </div>
      ) : (
        <form className="decision-form" onSubmit={onSubmit}>
          {mode === "edit" ? (
            <textarea
              rows={5}
              value={editText}
              onChange={(event) => onEditTextChange(event.target.value)}
              aria-label="Edited draft text"
            />
          ) : (
            <textarea
              rows={3}
              placeholder="Why are you rejecting this draft?"
              value={reason}
              onChange={(event) => onReasonChange(event.target.value)}
              aria-label="Rejection reason"
            />
          )}
          <div className="decision-form-footer">
            <button className="quiet-button" onClick={onCancel} type="button">
              Cancel
            </button>
            <button className="primary-button" disabled={busy} type="submit">
              Record {mode}
            </button>
          </div>
        </form>
      )}
      <span className="decision-target">Selected: {draft.variant}</span>
    </div>
  );
}
