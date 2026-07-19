import { useEffect, useMemo, useState, type FormEvent, type ReactNode } from "react";
import {
  createWorkflow,
  getRun,
  isDemoMode,
  listRuns,
  recordDecision,
} from "./api";
import { AppShell } from "./components/AppShell";
import { DashboardPage } from "./components/DashboardPage";
import { DecisionControls } from "./components/DecisionControls";
import { RunArtifacts } from "./components/RunArtifacts";
import { DraftComparison } from "./components/DraftComparison";
import { HistoryPage } from "./components/HistoryPage";
import { NewRunPage } from "./components/NewRunPage";
import { PipelinePanel } from "./components/PipelinePanel";
import { ReviewPanel } from "./components/ReviewPanel";
import { SettingsPage } from "./components/SettingsPage";
import { StudioContext } from "./components/StudioContext";
import { TracePage } from "./components/TracePage";
import { routeFromHash, type StudioRoute } from "./routes";
import type { DecisionKind, Draft, RunSummary, StudioRun } from "./types";

const initialGoal = "Write an approval-ready launch post";
const initialMaterial =
  "Orqestra Studio turns a goal into a small agent workflow, preserves the plan and review, and pauses before publication.";

function statusLabel(status: StudioRun["status"]): string {
  return status.replaceAll("_", " ");
}

function summaryFromRun(run: StudioRun): RunSummary {
  return {
    run_id: run.run_id,
    agent: run.agent,
    task: run.task,
    started_at: run.started_at,
    finished_at: run.finished_at,
    provider: run.provider,
    model: run.model,
    status: run.status,
    draft_count: run.drafts.length,
    decision_count: run.decisions.length,
    published_count: run.published.length,
  };
}

function environmentLabel(run: StudioRun | null): string {
  if (isDemoMode) return "Demo";
  if (run?.provider === "ollama") return "Qwen local";
  if (run?.provider === "openai") return "OpenAI";
  return "API connected";
}

function App() {
  const [route, setRoute] = useState<StudioRoute>(() => routeFromHash(window.location.hash));
  const [goal, setGoal] = useState(initialGoal);
  const [material, setMaterial] = useState(initialMaterial);
  const [run, setRun] = useState<StudioRun | null>(null);
  const [runCache, setRunCache] = useState<Record<string, StudioRun>>({});
  const [history, setHistory] = useState<RunSummary[]>([]);
  const [selectedDraftId, setSelectedDraftId] = useState<string | null>(null);
  const [decisionMode, setDecisionMode] = useState<DecisionKind | null>(null);
  const [editText, setEditText] = useState("");
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(!isDemoMode);
  const [loadingRunId, setLoadingRunId] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    const handleHashChange = () => setRoute(routeFromHash(window.location.hash));
    window.addEventListener("hashchange", handleHashChange);
    if (!window.location.hash) window.location.hash = "#/";
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  useEffect(() => {
    if (isDemoMode || !route.id || !["run", "trace"].includes(route.name)) return;
    if (run?.run_id === route.id || runCache[route.id]) {
      if (run?.run_id !== route.id) showRun(runCache[route.id]);
      return;
    }
    setLoadingRunId(route.id);
    getRun(route.id)
      .then((loadedRun) => {
        setRunCache((current) => ({ ...current, [loadedRun.run_id]: loadedRun }));
        showRun(loadedRun);
      })
      .catch((error) => setNotice(error instanceof Error ? error.message : "Unable to load this run"))
      .finally(() => setLoadingRunId(null));
  }, [route.id, route.name]);

  useEffect(() => {
    if (isDemoMode) {
      setHistoryLoading(false);
      return;
    }
    listRuns()
      .then(setHistory)
      .catch((error) => setNotice(error instanceof Error ? error.message : "Unable to load run history"))
      .finally(() => setHistoryLoading(false));
  }, []);

  const selectedDraft = useMemo(
    () => run?.drafts.find((draft) => draft.draft_id === selectedDraftId),
    [run, selectedDraftId],
  );
  const selectedDecision = run?.decisions.find(
    (decision) => decision.draft_id === selectedDraftId,
  );

  function showRun(nextRun: StudioRun) {
    setRun(nextRun);
    setSelectedDraftId(nextRun.drafts[0]?.draft_id ?? null);
    setDecisionMode(null);
    setEditText(nextRun.drafts[0]?.text ?? "");
    setReason("");
  }

  function go(path: string) {
    window.location.hash = path;
  }

  function startQuickStart(nextGoal: string, nextMaterial: string) {
    setGoal(nextGoal);
    setMaterial(nextMaterial);
    setNotice(null);
    go("#/runs/new");
  }

  async function handleRun(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!goal.trim() || !material.trim()) {
      setNotice("Add a goal and source material before running the team.");
      return;
    }
    setBusy(true);
    setNotice(null);
    try {
      const nextRun = await createWorkflow({
        goal,
        material,
        material_name: "studio-notes.md",
        variants: ["direct", "reflective"],
      });
      setRunCache((current) => ({ ...current, [nextRun.run_id]: nextRun }));
      setHistory((current) => [summaryFromRun(nextRun), ...current.filter((item) => item.run_id !== nextRun.run_id)]);
      showRun(nextRun);
      go(`#/runs/${nextRun.run_id}`);
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

  async function handleHistorySelect(summary: RunSummary) {
    const cachedRun = runCache[summary.run_id];
    if (cachedRun) {
      showRun(cachedRun);
      go(`#/runs/${summary.run_id}`);
      return;
    }
    if (isDemoMode) return;
    setLoadingRunId(summary.run_id);
    setNotice(null);
    try {
      const loadedRun = await getRun(summary.run_id);
      setRunCache((current) => ({ ...current, [loadedRun.run_id]: loadedRun }));
      showRun(loadedRun);
      go(`#/runs/${loadedRun.run_id}`);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Unable to load this run");
    } finally {
      setLoadingRunId(null);
    }
  }

  async function submitDecision(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!run || !selectedDraft || !decisionMode) return;
    if (decisionMode === "edit" && !editText.trim()) {
      setNotice("An edited draft cannot be empty.");
      return;
    }
    if (decisionMode === "reject" && !reason.trim()) {
      setNotice("Add a reason before rejecting this draft.");
      return;
    }
    setBusy(true);
    setNotice(null);
    try {
      const decision = await recordDecision(run.run_id, {
        draft_id: selectedDraft.draft_id,
        decision: decisionMode,
        reason: decisionMode === "reject" ? reason : undefined,
        reason_tag: decisionMode === "reject" ? "human_review" : undefined,
        edited_text: decisionMode === "edit" ? editText : undefined,
      });
      const updatedRun: StudioRun = { ...run, status: "decided", decisions: [...run.decisions, decision] };
      setRun(updatedRun);
      setRunCache((current) => ({ ...current, [updatedRun.run_id]: updatedRun }));
      setHistory((current) => current.map((item) => item.run_id === updatedRun.run_id ? summaryFromRun(updatedRun) : item));
      setDecisionMode(null);
      setNotice(`Draft ${decisionMode}d and recorded in the run history.`);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Unable to record decision");
    } finally {
      setBusy(false);
    }
  }

  function renderRunWorkspace() {
    if (!run) {
      return <div className="empty-state"><div className="empty-orbit">◈</div><span className="eyebrow">RUN WORKSPACE</span><h2>No run selected.</h2><p>Start a new run or open one from history to review drafts.</p><a className="primary-button" href="#/runs/new">Start new run</a></div>;
    }
    return (
      <div className="page-stack">
        <header className="page-header run-page-header"><div><span className="eyebrow">RUN / {run.run_id}</span><h1>{run.task}</h1><p>Compare the variants, read the review, and choose what happens next.</p></div><span className={`status-pill ${run.status}`}>{statusLabel(run.status)}</span></header>
        <section className="run-workspace" aria-labelledby="current-run-title">
          <div className="run-header"><div><span className="eyebrow">CURRENT RUN</span><h2 id="current-run-title">{run.task}</h2></div><div className="run-header-meta"><span className="run-id">{run.run_id}</span></div></div>
          <PipelinePanel run={run} />
          <div className="content-grid"><div><DraftComparison run={run} selectedDraftId={selectedDraftId} onSelect={selectDraft} />{selectedDraft && <DecisionControls draft={selectedDraft} mode={decisionMode} editText={editText} reason={reason} busy={busy} hasDecision={Boolean(selectedDecision)} onStart={startDecision} onCancel={() => setDecisionMode(null)} onEditTextChange={setEditText} onReasonChange={setReason} onSubmit={submitDecision} />}<RunArtifacts run={run} selectedDraft={selectedDraft} selectedDecision={selectedDecision} /></div></div>
        </section>
      </div>
    );
  }

  const currentEnvironment = environmentLabel(run);
  const context = run && (route.name === "run" || route.name === "trace")
    ? <ReviewPanel run={run} />
    : <StudioContext environmentLabel={currentEnvironment} />;

  let page: ReactNode;
  switch (route.name) {
    case "new-run":
      page = <NewRunPage goal={goal} material={material} busy={busy} onGoalChange={setGoal} onMaterialChange={setMaterial} onSubmit={handleRun} />;
      break;
    case "run":
      page = renderRunWorkspace();
      break;
    case "history":
      page = <HistoryPage runs={history} onOpen={handleHistorySelect} />;
      break;
    case "trace":
      page = <TracePage run={route.id ? run : run} onGoHistory={() => go("#/history")} />;
      break;
    case "settings":
      page = <SettingsPage environmentLabel={currentEnvironment} provider={run?.provider ?? (isDemoMode ? "demo" : "backend configured")} model={run?.model ?? (isDemoMode ? "local preview" : "backend configured")} />;
      break;
    default:
      page = <DashboardPage runs={history} onStart={startQuickStart} onOpen={handleHistorySelect} />;
  }

  return (
    <AppShell environmentLabel={currentEnvironment} runs={history} activeRunId={run?.run_id ?? null} activeRoute={route.name} historyLoading={historyLoading || loadingRunId !== null} onSelectRun={handleHistorySelect} context={context}>
      {notice && <div className="notice" role="status">{notice}</div>}
      {page}
    </AppShell>
  );
}

export default App;
