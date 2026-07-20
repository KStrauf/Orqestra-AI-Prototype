import type { StudioRun } from "../types";

interface ReviewPanelProps {
  run: StudioRun;
}

export function ReviewPanel({ run }: ReviewPanelProps) {
  const report = run.review_report;

  return (
    <aside className="review-card" aria-labelledby="review-title">
      <div className="review-card-top">
        <span className="eyebrow">REVIEWER NOTES</span>
        <span className="review-icon">✓</span>
      </div>
      <h3 id="review-title">Before you decide</h3>
      <p>{report?.summary || run.review || "No reviewer notes recorded."}</p>
      {report && (
        <div className="review-report">
          <div>
            <span className="eyebrow">WHAT WORKS</span>
            <ul>{report.strengths.map((item) => <li key={item}>{item}</li>)}</ul>
          </div>
          <div>
            <span className="eyebrow">WATCH FOR</span>
            <ul>{report.risks.map((item) => <li key={item}>{item}</li>)}</ul>
          </div>
          <div>
            <span className="eyebrow">RECOMMENDED NEXT STEP</span>
            <ul>{report.recommendations.map((item) => <li key={item}>{item}</li>)}</ul>
          </div>
        </div>
      )}
      {run.quality_report && (
        <div className="quality-summary">
          <div><span className="eyebrow">REVIEW SIGNAL</span><strong>{run.quality_report.overall}/10</strong></div>
          <p>{run.quality_report.method}</p>
        </div>
      )}
      <div className="plan-block">
        <span className="eyebrow">AGENT PLAN</span>
        <p>{run.agent_plan || "No plan recorded."}</p>
      </div>
      <div className="run-facts">
        <div>
          <span>Content platform</span>
          <strong>{run.content_platform || "General"}</strong>
        </div>
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
