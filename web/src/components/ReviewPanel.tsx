import type { StudioRun } from "../types";

interface ReviewPanelProps {
  run: StudioRun;
}

export function ReviewPanel({ run }: ReviewPanelProps) {
  return (
    <aside className="review-card" aria-labelledby="review-title">
      <div className="review-card-top">
        <span className="eyebrow">REVIEWER NOTES</span>
        <span className="review-icon">✓</span>
      </div>
      <h3 id="review-title">Before you decide</h3>
      <p>{run.review || "No reviewer notes recorded."}</p>
      <div className="plan-block">
        <span className="eyebrow">AGENT PLAN</span>
        <p>{run.agent_plan || "No plan recorded."}</p>
      </div>
      <div className="run-facts">
        <div>
          <span>Provider</span>
          <strong>{run.provider}</strong>
        </div>
        <div>
          <span>Model</span>
          <strong>{run.model}</strong>
        </div>
        <div>
          <span>Cost</span>
          <strong>{run.usage?.cost_usd ? `$${run.usage.cost_usd}` : "$0.00"}</strong>
        </div>
      </div>
    </aside>
  );
}
