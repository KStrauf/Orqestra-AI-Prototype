import type { RunSummary } from "../types";

interface DashboardPageProps {
  runs: RunSummary[];
  onStart: (goal: string, material: string) => void;
  onOpen: (run: RunSummary) => void;
}

const quickStarts = [
  {
    title: "Launch post",
    detail: "Turn build notes into an approval-ready announcement.",
    goal: "Write an approval-ready launch post",
    material: "We shipped a clearer multi-agent workflow with visible review and a human decision gate.",
  },
  {
    title: "Product update",
    detail: "Explain a new capability with useful alternative angles.",
    goal: "Write a concise product update",
    material: "Orqestra Studio turns a goal and source material into multiple drafts, then pauses for human review.",
  },
  {
    title: "Thought leadership",
    detail: "Shape an idea into a grounded point of view.",
    goal: "Draft a thought leadership post",
    material: "Reviewable agent teams make planning, drafting, and critique visible before publication.",
  },
];

function runStatus(status: RunSummary["status"]): string {
  return status.replaceAll("_", " ");
}

export function DashboardPage({ runs, onStart, onOpen }: DashboardPageProps) {
  return (
    <div className="page-stack">
      <header className="page-header dashboard-header">
        <div>
          <span className="eyebrow">DASHBOARD</span>
          <h1>Build with a reviewable agent team.</h1>
          <p>Start from a goal, see every handoff, and make the final call with confidence.</p>
        </div>
        <a className="primary-button page-cta" href="#/runs/new">Start new run</a>
      </header>

      <section className="dashboard-section" aria-labelledby="quick-starts-title">
        <div className="section-heading compact">
          <div>
            <span className="eyebrow">QUICK STARTS</span>
            <h2 id="quick-starts-title">What do you want to create?</h2>
          </div>
        </div>
        <div className="quick-start-grid">
          {quickStarts.map((item) => (
            <button
              className="quick-start-card"
              key={item.title}
              onClick={() => onStart(item.goal, item.material)}
              type="button"
            >
              <span className="quick-start-icon">✦</span>
              <strong>{item.title}</strong>
              <p>{item.detail}</p>
              <span className="quick-start-action">Use starting point →</span>
            </button>
          ))}
        </div>
      </section>

      <section className="dashboard-section" aria-labelledby="recent-runs-title">
        <div className="section-heading compact">
          <div>
            <span className="eyebrow">RECENT WORK</span>
            <h2 id="recent-runs-title">Recent runs</h2>
          </div>
          <a className="text-link" href="#/history">View all</a>
        </div>
        {runs.length === 0 ? (
          <div className="dashboard-empty">
            <span className="empty-orbit small">◷</span>
            <p>Your completed runs will collect here.</p>
            <a href="#/runs/new">Start with a quick run →</a>
          </div>
        ) : (
          <div className="recent-run-list">
            {runs.slice(0, 5).map((run) => (
              <button className="recent-run-row" key={run.run_id} onClick={() => onOpen(run)} type="button">
                <span className="recent-run-title"><strong>{run.task}</strong><small>{run.run_id}</small></span>
                <span className={`history-status ${run.status}`}>{runStatus(run.status)}</span>
                <span className="recent-run-provider">{run.provider} · {run.model}</span>
                <span className="recent-run-open">Open →</span>
              </button>
            ))}
          </div>
        )}
      </section>

      <section className="workflow-strip" aria-label="How Orqestra works">
        <div><span>01</span><strong>Plan</strong><small>Architect shapes the work</small></div>
        <div><span>02</span><strong>Draft</strong><small>Specialist creates alternatives</small></div>
        <div><span>03</span><strong>Review</strong><small>Reviewer checks the result</small></div>
        <div><span>04</span><strong>Decide</strong><small>You control what happens next</small></div>
      </section>
    </div>
  );
}
