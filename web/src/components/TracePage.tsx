import type { StudioRun } from "../types";

interface TracePageProps {
  run: StudioRun | null;
  onGoHistory: () => void;
}

export function TracePage({ run, onGoHistory }: TracePageProps) {
  if (!run) {
    return <div className="empty-state"><div className="empty-orbit">⌁</div><span className="eyebrow">RUN TRACE</span><h2>No run selected.</h2><p>Open a saved run to see how the Architect, Specialist, Reviewer, and human decision connect.</p><button className="primary-button" onClick={onGoHistory} type="button">Go to history</button></div>;
  }
  const decisions = run.decisions;
  return (
    <div className="page-stack">
      <header className="page-header">
        <div><span className="eyebrow">TRACE / {run.run_id}</span><h1>How this run came together.</h1><p>Plain-language handoffs show the work behind the draft.</p></div>
      </header>
      <section className="trace-page-card">
        <div className="trace-timeline">
          <article className="trace-event"><span className="trace-marker">01</span><div><span className="eyebrow">ARCHITECT</span><h3>Planned the team</h3><p>{run.agent_plan || "The Architect created a plan for this goal."}</p></div></article>
          <article className="trace-event"><span className="trace-marker">02</span><div><span className="eyebrow">SPECIALIST</span><h3>Produced {run.drafts.length} draft variants</h3><p>The Specialist turned the supplied material into alternatives for comparison.</p><div className="trace-artifacts">{run.drafts.map((draft) => <span key={draft.draft_id}>{draft.variant} · {draft.chars} chars</span>)}</div></div></article>
          <article className="trace-event"><span className="trace-marker">03</span><div><span className="eyebrow">REVIEWER</span><h3>Checked the candidates</h3><p>{run.review || "The Reviewer returned no notes for this run."}</p></div></article>
          <article className="trace-event"><span className="trace-marker human">04</span><div><span className="eyebrow">HUMAN DECISION</span><h3>{decisions.length ? `${decisions.length} decision recorded` : "Waiting for your decision"}</h3><p>{decisions.length ? decisions.map((decision) => `${decision.decision} · ${decision.draft_id}`).join("  /  ") : "Choose a draft and approve, edit, or reject it when you are ready."}</p></div></article>
        </div>
        <aside className="trace-facts"><span className="eyebrow">RUN FACTS</span><div><span>Provider</span><strong>{run.provider}</strong></div><div><span>Model</span><strong>{run.model}</strong></div><div><span>Status</span><strong>{run.status.replaceAll("_", " ")}</strong></div><div><span>Usage</span><strong>{run.usage ? `${run.usage.input_tokens + run.usage.output_tokens} tokens` : "Local preview"}</strong></div></aside>
      </section>
    </div>
  );
}
