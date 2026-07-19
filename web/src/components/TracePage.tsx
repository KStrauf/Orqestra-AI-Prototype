import { DecisionTimeline } from "./DecisionTimeline";
import { RunArtifacts } from "./RunArtifacts";
import type { StudioRun } from "../types";

interface TracePageProps {
  run: StudioRun | null;
  onGoHistory: () => void;
}

function formatTimestamp(timestamp: string | null | undefined): string {
  if (!timestamp) return "Not recorded";
  const date = new Date(timestamp);
  if (Number.isNaN(date.valueOf())) return timestamp;
  return date.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

export function TracePage({ run, onGoHistory }: TracePageProps) {
  if (!run) {
    return <div className="empty-state"><div className="empty-orbit">⌁</div><span className="eyebrow">RUN TRACE</span><h2>No run selected.</h2><p>Open a saved run to see how the Architect, Specialist, Reviewer, and human decision connect.</p><button className="primary-button" onClick={onGoHistory} type="button">Go to history</button></div>;
  }

  const firstDecision = run.decisions[0];
  const selectedDraft = run.drafts[0];
  const selectedDecision = selectedDraft ? run.decisions.find((decision) => decision.draft_id === selectedDraft.draft_id) : undefined;

  return (
    <div className="page-stack">
      <header className="page-header">
        <div><span className="eyebrow">TRACE / {run.run_id}</span><h1>How this run came together.</h1><p>Plain-language handoffs show the work behind the draft and the human decision.</p></div>
        <span className={`status-pill ${run.status}`}>{run.status.replaceAll("_", " ")}</span>
      </header>
      <section className="trace-page-card">
        <div className="trace-main">
          <div className="trace-timeline" aria-label="Agent and human trace">
            <article className="trace-event"><span className="trace-marker">01</span><div><span className="eyebrow">ARCHITECT</span><h3>Planned the team</h3><p>{run.agent_plan || "The Architect created a plan for this goal."}</p><time className="trace-event-meta" dateTime={run.started_at}>Run started {formatTimestamp(run.started_at)}</time></div></article>
            <article className="trace-event"><span className="trace-marker">02</span><div><span className="eyebrow">SPECIALIST</span><h3>Produced {run.drafts.length} draft variants</h3><p>The Specialist turned the supplied material into alternatives for comparison.</p><div className="trace-artifacts">{run.drafts.map((draft) => <span key={draft.draft_id}>{draft.variant} · {draft.chars} chars</span>)}</div><span className="trace-event-meta">Draft artifacts preserved in this run</span></div></article>
            <article className="trace-event"><span className="trace-marker">03</span><div><span className="eyebrow">REVIEWER</span><h3>Checked the candidates</h3><p>{run.review || "The Reviewer returned no notes for this run."}</p><time className="trace-event-meta" dateTime={run.finished_at || undefined}>Run completed {formatTimestamp(run.finished_at)}</time></div></article>
            <article className="trace-event"><span className="trace-marker human">04</span><div><span className="eyebrow">HUMAN DECISION</span><h3>{run.decisions.length ? `${run.decisions.length} decision${run.decisions.length === 1 ? "" : "s"} recorded` : "Waiting for your decision"}</h3><p>{run.decisions.length ? "The decision record below preserves what happened to each candidate." : "Choose a draft and approve, edit, or reject it when you are ready."}</p>{firstDecision ? <time className="trace-event-meta" dateTime={firstDecision.at}>First decision {formatTimestamp(firstDecision.at)}</time> : <span className="trace-event-meta">Human gate still open</span>}</div></article>
          </div>
          <DecisionTimeline run={run} />
        </div>
        <aside className="trace-facts"><span className="eyebrow">RUN FACTS</span><div><span>Provider</span><strong>{run.provider}</strong></div><div><span>Model</span><strong>{run.model}</strong></div><div><span>Status</span><strong>{run.status.replaceAll("_", " ")}</strong></div><div><span>Started</span><strong>{formatTimestamp(run.started_at)}</strong></div><div><span>Usage</span><strong>{run.usage ? `${run.usage.input_tokens + run.usage.output_tokens} tokens` : "Local preview"}</strong></div></aside>
      </section>
      <RunArtifacts run={run} selectedDraft={selectedDraft} selectedDecision={selectedDecision} />
    </div>
  );
}
