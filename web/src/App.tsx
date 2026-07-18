import { FormEvent, useMemo, useState } from "react";
import { createWorkflow, isDemoMode, recordDecision } from "./api";
import type { Decision, DecisionKind, Draft, StudioRun } from "./types";

const initialGoal = "Write an approval-ready launch post";
const initialMaterial =
  "Orqestra Studio turns a goal into a small agent workflow, preserves the plan and review, and pauses before publication.";

function decisionFor(run: StudioRun | null, draftId: string): Decision | undefined {
  return run?.decisions.find((decision) => decision.draft_id === draftId);
}

function statusLabel(status: StudioRun["status"]): string {
  return status.replaceAll("_", " ");
}

function App() {
  const [goal, setGoal] = useState(initialGoal);
  const [material, setMaterial] = useState(initialMaterial);
  const [run, setRun] = useState<StudioRun | null>(null);
  const [selectedDraftId, setSelectedDraftId] = useState<string | null>(null);
  const [decisionMode, setDecisionMode] = useState<DecisionKind | null>(null);
  const [editText, setEditText] = useState("");
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  const selectedDraft = useMemo(
    () => run?.drafts.find((draft) => draft.draft_id === selectedDraftId),
    [run, selectedDraftId],
  );

  async function handleRun(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!goal.trim() || !material.trim()) return;
    setBusy(true);
    setNotice(null);
    try {
      const nextRun = await createWorkflow({
        goal,
        material,
        material_name: "studio-notes.md",
        variants: ["direct", "reflective"],
      });
      setRun(nextRun);
      setSelectedDraftId(nextRun.drafts[0]?.draft_id ?? null);
      setDecisionMode(null);
      setNotice("Workflow completed and is ready for review.");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Unable to run workflow");
    } finally {
      setBusy(false);
    }
  }

  function selectDraft(draft: Draft) {
    setSelectedDraftId(draft.draft_id);
    setDecisionMode(null);
    setEditText(draft.text);
    setReason("");
  }

  function startDecision(mode: DecisionKind) {
    if (!selectedDraft) return;
    setDecisionMode(mode);
    setEditText(selectedDraft.text);
    setReason("");
  }

  async function submitDecision(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!run || !selectedDraft || !decisionMode) return;
    if (decisionMode === "edit" && !editText.trim()) return;
    if (decisionMode === "reject" && !reason.trim()) return;
    setBusy(true);
    try {
      const decision = await recordDecision(run.run_id, {
        draft_id: selectedDraft.draft_id,
        decision: decisionMode,
        reason: decisionMode === "reject" ? reason : undefined,
        reason_tag: decisionMode === "reject" ? "human_review" : undefined,
        edited_text: decisionMode === "edit" ? editText : undefined,
      });
      setRun((current) =>
        current
          ? {
              ...current,
              status: "decided",
              decisions: [...current.decisions, decision],
            }
          : current,
      );
      setDecisionMode(null);
      setNotice(`Draft ${decisionMode}d and recorded in the run history.`);
    } finally {
      setBusy(false);
    }
  }

  const approvedCount = run?.decisions.filter(
    (decision) => decision.decision === "approve" || decision.decision === "edit",
  ).length ?? 0;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">O</div>
          <div>
            <strong>Orqestra</strong>
            <span>Studio</span>
          </div>
        </div>
        <nav className="nav-list" aria-label="Primary navigation">
          <a className="nav-item active" href="#workspace"><span>✦</span> Workspace</a>
          <a className="nav-item" href="#runs"><span>◷</span> Run history</a>
          <a className="nav-item" href="#agents"><span>⌘</span> Agent roster</a>
        </nav>
        <div className="sidebar-footer">
          <div className="status-dot" />
          <div>
            <strong>{isDemoMode ? "Demo mode" : "API connected"}</strong>
            <span>{isDemoMode ? "Local preview data" : "Studio service"}</span>
          </div>
        </div>
      </aside>

      <main className="main-content" id="workspace">
        <header className="topbar">
          <div>
            <span className="eyebrow">WORKSPACE / CONTENT</span>
            <h1>Build with a reviewable agent team.</h1>
          </div>
          <div className="topbar-meta">
            <span className="connection-pill"><span className="status-dot" /> Local runtime</span>
            <div className="avatar">KS</div>
          </div>
        </header>

        <section className="composer-card">
          <div className="section-heading">
            <div>
              <span className="eyebrow">NEW WORKFLOW</span>
              <h2>What should the team create?</h2>
            </div>
            <span className="step-label">01 / 03</span>
          </div>
          <form onSubmit={handleRun}>
            <label>
              <span>Goal</span>
              <input value={goal} onChange={(event) => setGoal(event.target.value)} />
            </label>
            <label>
              <span>Source material</span>
              <textarea
                rows={3}
                value={material}
                onChange={(event) => setMaterial(event.target.value)}
              />
            </label>
            <div className="form-footer">
              <span className="helper-text">The workflow will plan, draft, review, then pause for you.</span>
              <button className="primary-button" disabled={busy} type="submit">
                {busy ? "Running team…" : "Run workflow  →"}
              </button>
            </div>
          </form>
        </section>

        {notice && <div className="notice">{notice}</div>}

        {run ? (
          <section className="run-workspace">
            <div className="run-header">
              <div>
                <span className="eyebrow">CURRENT RUN</span>
                <h2>{run.task}</h2>
              </div>
              <div className="run-header-meta">
                <span className={`status-pill ${run.status}`}>{statusLabel(run.status)}</span>
                <span className="run-id">{run.run_id}</span>
              </div>
            </div>

            <div className="agent-pipeline">
              {[
                ["01", "Architect", "Plan recorded"],
                ["02", "Specialist", `${run.drafts.length} drafts produced`],
                ["03", "Reviewer", "Human decision required"],
              ].map(([number, name, detail], index) => (
                <div className="pipeline-step" key={name}>
                  <div className="pipeline-number">{number}</div>
                  <div><strong>{name}</strong><span>{detail}</span></div>
                  {index < 2 && <div className="pipeline-line" />}
                </div>
              ))}
            </div>

            <div className="content-grid">
              <section className="drafts-section">
                <div className="section-heading compact">
                  <div><span className="eyebrow">CANDIDATES</span><h3>Choose a draft to review</h3></div>
                  <span className="count-label">{approvedCount} / {run.drafts.length} decided</span>
                </div>
                <div className="draft-list">
                  {run.drafts.map((draft) => {
                    const decision = decisionFor(run, draft.draft_id);
                    return (
                      <button
                        className={`draft-card ${draft.draft_id === selectedDraftId ? "selected" : ""}`}
                        key={draft.draft_id}
                        onClick={() => selectDraft(draft)}
                        type="button"
                      >
                        <div className="draft-card-top"><span>{draft.variant}</span>{decision && <span className={`decision-tag ${decision.decision}`}>{decision.decision}</span>}</div>
                        <p>{draft.text}</p>
                        <span className="draft-card-bottom">{draft.chars} characters <span>↗</span></span>
                      </button>
                    );
                  })}
                </div>
                {selectedDraft && (
                  <div className="decision-panel">
                    <div className="decision-panel-heading"><div><span className="eyebrow">HUMAN GATE</span><h3>What should happen to this draft?</h3></div><span className="lock-label">⌑ Nothing publishes automatically</span></div>
                    {!decisionMode ? (
                      <div className="decision-actions">
                        <button className="approve-button" onClick={() => startDecision("approve")} type="button">Approve</button>
                        <button className="edit-button" onClick={() => startDecision("edit")} type="button">Edit draft</button>
                        <button className="reject-button" onClick={() => startDecision("reject")} type="button">Reject</button>
                      </div>
                    ) : (
                      <form className="decision-form" onSubmit={submitDecision}>
                        {decisionMode === "edit" ? <textarea rows={5} value={editText} onChange={(event) => setEditText(event.target.value)} /> : <textarea rows={3} placeholder="Why are you rejecting this draft?" value={reason} onChange={(event) => setReason(event.target.value)} />}
                        <div className="decision-form-footer"><button className="quiet-button" onClick={() => setDecisionMode(null)} type="button">Cancel</button><button className="primary-button" disabled={busy} type="submit">Record {decisionMode}</button></div>
                      </form>
                    )}
                  </div>
                )}
              </section>

              <aside className="review-card">
                <div className="review-card-top"><span className="eyebrow">REVIEWER NOTES</span><span className="review-icon">✓</span></div>
                <h3>Before you decide</h3>
                <p>{run.review}</p>
                <div className="plan-block"><span className="eyebrow">AGENT PLAN</span><p>{run.agent_plan}</p></div>
                <div className="run-facts"><div><span>Provider</span><strong>{run.provider}</strong></div><div><span>Model</span><strong>{run.model}</strong></div><div><span>Cost</span><strong>{run.usage?.cost_usd ? `$${run.usage.cost_usd}` : "$0.00"}</strong></div></div>
              </aside>
            </div>
          </section>
        ) : (
          <section className="empty-state"><div className="empty-orbit">✦</div><span className="eyebrow">READY WHEN YOU ARE</span><h2>Your next run will appear here.</h2><p>Start with a goal and some source material. Orqestra will show every handoff before anything can be published.</p></section>
        )}
      </main>
    </div>
  );
}

export default App;
