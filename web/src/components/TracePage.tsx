import { DecisionTimeline } from "./DecisionTimeline";
import type { StudioRun } from "../types";

interface TracePageProps {
  run: StudioRun | null;
  selectedDraftId?: string | null;
  onGoHistory: () => void;
}

function formatTimestamp(timestamp: string | null | undefined): string {
  if (!timestamp) return "Not recorded";
  const date = new Date(timestamp);
  if (Number.isNaN(date.valueOf())) return timestamp;
  return date.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

export function TracePage({ run, selectedDraftId, onGoHistory }: TracePageProps) {
  if (!run) {
    return <div className="empty-state"><div className="empty-orbit">⌁</div><span className="eyebrow">RUN TRACE</span><h2>No run selected.</h2><p>Open a saved run to see how the Architect, Specialist, Reviewer, and human decision connect.</p><button className="primary-button" onClick={onGoHistory} type="button">Go to history</button></div>;
  }

  const firstDecision = run.decisions[0];
  const selectedDraft = run.drafts.find((draft) => draft.draft_id === selectedDraftId) || run.drafts[0];
  const selectedDecision = selectedDraft ? run.decisions.find((decision) => decision.draft_id === selectedDraft.draft_id) : undefined;
  const reviewerNotes = run.review_report?.summary || run.review || "Reviewer notes were not recorded for this run.";
  const agentPlan = run.agent_plan || "The Architect plan was not recorded for this run.";

  return (
    <div className="page-stack">
      <header className="page-header">
        <div><span className="eyebrow">TRACE / {run.run_id}</span><h1>How this run came together.</h1><p>Follow the handoffs, inspect the selected artifact, and see where the human decision fits.</p></div>
        <span className={`status-pill ${run.status}`}>{run.status.replaceAll("_", " ")}</span>
      </header>
      <section className="trace-page-card">
        <div className="trace-main">
          <div className="trace-timeline" aria-label="Agent and human trace">
            <article className="trace-event"><span className="trace-marker">01</span><div><span className="eyebrow">ARCHITECT</span><h3>Planned the team</h3><p>{agentPlan}</p><time className="trace-event-meta" dateTime={run.started_at}>Run started {formatTimestamp(run.started_at)}</time></div></article>
            <article className="trace-event"><span className="trace-marker">02</span><div><span className="eyebrow">SPECIALIST</span><h3>Produced {run.drafts.length} draft variants</h3><p>The Specialist turned the supplied material into alternatives for comparison.</p><div className="trace-artifacts">{run.drafts.map((draft) => <span key={draft.draft_id}>{draft.variant} · {draft.chars} chars</span>)}</div><span className="trace-event-meta">Draft artifacts preserved in this run</span></div></article>
            <article className="trace-event"><span className="trace-marker">03</span><div><span className="eyebrow">REVIEWER</span><h3>Checked the candidates</h3><p>{reviewerNotes}</p><time className="trace-event-meta" dateTime={run.finished_at || undefined}>Run completed {formatTimestamp(run.finished_at)}</time></div></article>
            <article className="trace-event"><span className="trace-marker human">04</span><div><span className="eyebrow">HUMAN DECISION</span><h3>{run.decisions.length ? `${run.decisions.length} decision${run.decisions.length === 1 ? "" : "s"} recorded` : "Waiting for your decision"}</h3><p>{run.decisions.length ? "The decision record below preserves what happened to each candidate." : "Choose a draft and approve, edit, or reject it when you are ready."}</p>{firstDecision ? <time className="trace-event-meta" dateTime={firstDecision.at}>First decision {formatTimestamp(firstDecision.at)}</time> : <span className="trace-event-meta">Human gate still open</span>}</div></article>
          </div>

          <div className="trace-highlights">
            <article className="trace-highlight trace-highlight-selected">
              <div className="trace-highlight-heading"><span className="eyebrow">SELECTED DRAFT</span><span>{selectedDraft?.chars ?? 0} chars</span></div>
              <h3>{selectedDraft?.variant || "No draft selected"}</h3>
              <p className="trace-highlight-text">{selectedDraft?.text || "Select a draft from the Run Workspace to inspect it here."}</p>
              <div className="why-panel"><span className="eyebrow">WHY THIS DRAFT</span><p>The Specialist produced this selected alternative after following the Architect plan.</p></div>
            </article>
            <article className="trace-highlight">
              <div className="trace-highlight-heading"><span className="eyebrow">REVIEWER NOTES</span><span>Reviewer output</span></div>
              <p className="trace-highlight-text">{reviewerNotes}</p>
              <div className="why-panel"><span className="eyebrow">AGENT PLAN</span><p>{agentPlan}</p></div>
            </article>
            <article className="trace-highlight trace-highlight-wide">
              <div className="trace-highlight-heading"><span className="eyebrow">WORKFLOW EVIDENCE</span><span>{run.hook_candidates?.length ?? 0} hook directions · {run.drafts.length} drafts</span></div>
              <div className="trace-evidence-facts">
                <div><span>Core idea</span><strong>{run.content_brief?.core_idea || run.task}</strong></div>
                <div><span>Audience</span><strong>{run.content_brief?.audience || run.audience || "Not specified"}</strong></div>
                <div><span>Outcome</span><strong>{run.content_brief?.outcome || run.outcome || "Not specified"}</strong></div>
              </div>
              <p className="trace-highlight-note">This evidence shows what the team used to shape the drafts. It is editorial context, not a performance prediction.</p>
            </article>
            {run.quality_report && (
              <article className="trace-highlight trace-highlight-wide trace-benchmark">
                <div className="trace-highlight-heading"><span className="eyebrow">CONTENT BENCHMARK</span><strong>{run.quality_report.overall}/10</strong></div>
                <p className="trace-highlight-note">The Reviewer checks the work before you decide. These scores explain where a human should focus attention; they do not predict reach or engagement.</p>
                <div className="trace-benchmark-grid">
                  {Object.entries(run.quality_report.scores).map(([label, score]) => (
                    <div key={label}><span>{label.replaceAll("_", " ")}</span><strong>{score}/10</strong></div>
                  ))}
                </div>
                {run.quality_report.recommendations[0] && <p className="trace-benchmark-recommendation"><span className="eyebrow">REVIEWER RECOMMENDATION</span>{run.quality_report.recommendations[0]}</p>}
              </article>
            )}
          </div>

          <DecisionTimeline run={run} />
        </div>
        <aside className="trace-facts"><span className="eyebrow">RUN FACTS</span><div><span>Content platform</span><strong>{run.content_platform || "General"}</strong></div><div><span>Provider</span><strong>{run.provider}</strong></div><div><span>Model</span><strong>{run.model}</strong></div><div><span>Status</span><strong>{run.status.replaceAll("_", " ")}</strong></div><div><span>Started</span><strong>{formatTimestamp(run.started_at)}</strong></div><div><span>Usage</span><strong>{run.usage ? `${run.usage.input_tokens + run.usage.output_tokens} tokens` : "Local preview"}</strong></div></aside>
      </section>
    </div>
  );
}
