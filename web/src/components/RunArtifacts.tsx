import type { Decision, Draft, StudioRun } from "../types";

interface RunArtifactsProps {
  run: StudioRun;
  selectedDraft?: Draft;
  selectedDecision?: Decision;
}

function shortHash(value: string): string {
  return value ? `${value.slice(0, 10)}…` : "Not available";
}

function formatTimestamp(timestamp: string | null | undefined): string {
  if (!timestamp) return "Not recorded";
  const date = new Date(timestamp);
  if (Number.isNaN(date.valueOf())) return timestamp;
  return date.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

function decisionTimestamp(decision: Decision | undefined): string {
  return decision ? formatTimestamp(decision.at) : "Not recorded";
}

function decisionExplanation(decision: Decision | undefined): string {
  if (!decision) return "No human decision has been recorded for this draft yet.";
  if (decision.decision === "approve") {
    return "A human reviewer approved this candidate after comparing it with the alternatives and reading the Reviewer notes.";
  }
  if (decision.decision === "edit") {
    return "A human reviewer chose to revise this candidate. The edited artifact is preserved alongside the original draft.";
  }
  return "A human reviewer rejected this candidate. The rationale is preserved so the run remains inspectable.";
}

export function RunArtifacts({ run, selectedDraft, selectedDecision }: RunArtifactsProps) {
  const input = run.inputs[0];

  return (
    <section className="artifact-panel" aria-labelledby="artifact-panel-title">
      <div className="artifact-panel-header">
        <div>
          <span className="eyebrow">ARTIFACTS</span>
          <h3 id="artifact-panel-title">What this run produced</h3>
        </div>
        <span className="artifact-count">{run.drafts.length} drafts · {run.decisions.length} decisions</span>
      </div>
      {run.content_brief && (
        <article className="artifact-card artifact-brief">
          <div className="artifact-card-heading">
            <span className="eyebrow">CONTENT BRIEF</span>
            <span className="artifact-meta">{run.content_brief.platform}</span>
          </div>
          <div className="brief-facts">
            <div><span>Audience</span><strong>{run.content_brief.audience}</strong></div>
            <div><span>Outcome</span><strong>{run.content_brief.outcome}</strong></div>
            <div><span>Voice</span><strong>{run.content_brief.tone}</strong></div>
          </div>
          <p className="artifact-copy"><strong>Core idea:</strong> {run.content_brief.core_idea}</p>
          <div className="brief-angle-list"><span className="eyebrow">DRAFT ANGLES</span>{run.content_brief.angles.map((angle) => <span key={angle}>{angle}</span>)}</div>
        </article>
      )}
      {run.hook_candidates && run.hook_candidates.length > 0 && (
        <article className="artifact-card artifact-hooks">
          <div className="artifact-card-heading">
            <span className="eyebrow">HOOK DIRECTIONS</span>
            <span className="artifact-meta">Specialist starting points</span>
          </div>
          <p className="artifact-meta">The team generated grounded openings for comparison. They are editorial options, not performance promises.</p>
          <div className="hook-list">
            {run.hook_candidates.map((hook) => (
              <div className="hook-row" key={hook.hook_id}>
                <div><strong>{hook.pattern}</strong><span>{hook.variant}</span></div>
                <p>{hook.text}</p>
                <small>{hook.rationale}</small>
              </div>
            ))}
          </div>
        </article>
      )}
      {run.quality_report && (
        <article className="artifact-card artifact-quality">
          <div className="artifact-card-heading">
            <span className="eyebrow">REVIEW CHECKS</span>
            <span className="quality-score">{run.quality_report.overall}/10 review signal</span>
          </div>
          <p className="artifact-meta">{run.quality_report.method}</p>
          <div className="quality-grid">
            {Object.entries(run.quality_report.scores).map(([label, score]) => (
              <div key={label}><span>{label.replaceAll("_", " ")}</span><strong>{score}/10</strong></div>
            ))}
          </div>
          {run.quality_report.issues.length > 0 && <div className="why-panel"><span className="eyebrow">WATCH FOR</span><ul>{run.quality_report.issues.map((issue) => <li key={issue}>{issue}</li>)}</ul></div>}
        </article>
      )}
      <div className="artifact-grid">
        <article className="artifact-card artifact-source">
          <div className="artifact-card-heading">
            <span className="eyebrow">ORIGINAL MATERIAL</span>
            <span className="artifact-meta">{input?.chars ?? 0} chars</span>
          </div>
          <strong>{input?.path || "Workflow material"}</strong>
          <p className="artifact-meta">SHA-256 {shortHash(input?.sha256 || "")}</p>
          {input?.content ? (
            <details className="artifact-disclosure">
              <summary>View source material</summary>
              <p className="artifact-copy artifact-scroll">{input.content}</p>
            </details>
          ) : (
            <p className="artifact-meta">Idea-only brief. The team worked from the goal above.</p>
          )}
        </article>

        <article className="artifact-card artifact-drafts">
          <div className="artifact-card-heading">
            <span className="eyebrow">DRAFT ARTIFACTS</span>
            <span className="artifact-meta">Specialist output</span>
          </div>
          <div className="artifact-list">
            {run.drafts.map((draft) => (
              <div className={`artifact-draft-row ${draft.draft_id === selectedDraft?.draft_id ? "selected" : ""}`} key={draft.draft_id}>
                <strong>{draft.variant}</strong>
                <span>{draft.chars} chars</span>
                {draft.constraint_violations.length > 0 && <small>{draft.constraint_violations.length} constraint warnings</small>}
              </div>
            ))}
          </div>
        </article>

        <article className="artifact-card artifact-selected">
          <div className="artifact-card-heading">
            <span className="eyebrow">SELECTED DRAFT</span>
            <span className="artifact-meta">{selectedDraft?.chars ?? 0} chars</span>
          </div>
          <strong>{selectedDraft?.variant || "No draft selected"}</strong>
          {selectedDraft?.angle && <span className="draft-angle">{selectedDraft.angle}</span>}
          <p className="artifact-copy artifact-scroll">{selectedDraft?.text || "Select a draft above to inspect its full text."}</p>
          <div className="why-panel">
            <span className="eyebrow">WHY THIS DRAFT</span>
            <p>The Specialist produced this {selectedDraft?.variant || "candidate"} alternative from the supplied material after following the Architect plan.</p>
            {selectedDraft?.constraint_violations.length ? <p className="artifact-warning">Reviewer constraints: {selectedDraft.constraint_violations.join(", ")}</p> : <p className="artifact-meta">No draft-level constraint warnings were recorded.</p>}
          </div>
        </article>

        <article className="artifact-card artifact-review">
          <div className="artifact-card-heading">
            <span className="eyebrow">REVIEWER NOTES</span>
            <span className="artifact-meta">Reviewer output</span>
          </div>
          <p className="artifact-copy">{run.review_report?.summary || run.review || "No reviewer notes were recorded."}</p>
          {run.review_report && <div className="why-panel"><span className="eyebrow">RECOMMENDED NEXT STEP</span><p>{run.review_report.recommendations[0] || "Compare the drafts and make the final decision."}</p></div>}
          <div className="why-panel">
            <span className="eyebrow">AGENT PLAN</span>
            <p>{run.agent_plan || "No Architect plan was recorded."}</p>
          </div>
        </article>

        <article className="artifact-card artifact-decision">
          <div className="artifact-card-heading">
            <span className="eyebrow">DECISION ARTIFACT</span>
            {selectedDecision && <span className={`decision-tag ${selectedDecision.decision}`}>{selectedDecision.decision}</span>}
          </div>
          <div className="decision-receipt-facts">
            <div><span>Draft</span><strong>{selectedDraft?.variant || "No draft selected"}</strong></div>
            <div><span>Recorded</span><strong>{decisionTimestamp(selectedDecision)}</strong></div>
          </div>
          <div className="why-panel">
            <span className="eyebrow">WHY THIS DECISION</span>
            <p>{decisionExplanation(selectedDecision)}</p>
          </div>
          {selectedDecision?.reason && <p className="artifact-copy"><strong>Rationale:</strong> {selectedDecision.reason}</p>}
          {selectedDecision?.edited_text && (
            <details className="artifact-edited">
              <summary>View edited draft <span>Original draft remains preserved</span></summary>
              <p className="artifact-copy artifact-scroll">{selectedDecision.edited_text}</p>
            </details>
          )}
        </article>

        <article className="artifact-card artifact-summary">
          <div className="artifact-card-heading">
            <span className="eyebrow">RUN SUMMARY</span>
            <span className={`status-pill ${run.status}`}>{run.status.replaceAll("_", " ")}</span>
          </div>
          <div className="artifact-facts">
            <div><span>Platform</span><strong>{run.content_platform || "General"}</strong></div>
            <div><span>Provider</span><strong>{run.provider}</strong></div>
            <div><span>Model</span><strong>{run.model}</strong></div>
            <div><span>Drafts</span><strong>{run.drafts.length}</strong></div>
            <div><span>Decisions</span><strong>{run.decisions.length}</strong></div>
            <div><span>Started</span><strong>{formatTimestamp(run.started_at)}</strong></div>
            <div><span>Finished</span><strong>{formatTimestamp(run.finished_at)}</strong></div>
          </div>
        </article>
      </div>
    </section>
  );
}
