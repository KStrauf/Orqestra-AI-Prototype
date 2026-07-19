import { useMemo, useState } from "react";
import type { RunStatus, RunSummary } from "../types";

interface HistoryPageProps {
  runs: RunSummary[];
  onOpen: (run: RunSummary) => void;
}

const statusOptions: Array<"all" | RunStatus> = ["all", "awaiting_approval", "decided", "published", "completed"];

function label(value: string): string {
  return value.replaceAll("_", " ");
}

function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  if (Number.isNaN(date.valueOf())) return "Unknown time";
  return date.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

export function HistoryPage({ runs, onOpen }: HistoryPageProps) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<(typeof statusOptions)[number]>("all");
  const [provider, setProvider] = useState("all");
  const providers = ["all", ...new Set(runs.map((run) => run.provider))];
  const filteredRuns = useMemo(
    () => runs.filter((run) => {
      const matchesQuery = !query.trim() || run.task.toLowerCase().includes(query.toLowerCase());
      const matchesStatus = status === "all" || run.status === status;
      const matchesProvider = provider === "all" || run.provider === provider;
      return matchesQuery && matchesStatus && matchesProvider;
    }),
    [provider, query, runs, status],
  );

  return (
    <div className="page-stack">
      <header className="page-header">
        <div>
          <span className="eyebrow">HISTORY</span>
          <h1>Run history.</h1>
          <p>Reopen work, inspect decisions, and keep the production trail visible.</p>
        </div>
      </header>
      <section className="history-page-card">
        <div className="history-summary-grid" aria-label="History summary">
          <div><span className="eyebrow">TOTAL RUNS</span><strong>{runs.length}</strong><small>durable records</small></div>
          <div><span className="eyebrow">IN REVIEW</span><strong>{runs.filter((run) => run.status === "awaiting_approval").length}</strong><small>human gate open</small></div>
          <div><span className="eyebrow">DECISIONS</span><strong>{runs.reduce((total, run) => total + run.decision_count, 0)}</strong><small>recorded choices</small></div>
        </div>
        <div className="history-filters">
          <input aria-label="Search runs" placeholder="Search by goal or task" value={query} onChange={(event) => setQuery(event.target.value)} />
          <select aria-label="Filter by status" value={status} onChange={(event) => setStatus(event.target.value as typeof status)}>
            {statusOptions.map((option) => <option key={option} value={option}>{label(option)}</option>)}
          </select>
          <select aria-label="Filter by provider" value={provider} onChange={(event) => setProvider(event.target.value)}>
            {providers.map((option) => <option key={option} value={option}>{option === "all" ? "All providers" : option}</option>)}
          </select>
        </div>
        {filteredRuns.length === 0 ? (
          <div className="dashboard-empty"><span className="empty-orbit small">◷</span><p>No runs match these filters.</p><a href="#/runs/new">Create a new run →</a></div>
        ) : (
          <div className="history-table" role="table" aria-label="Studio run history">
            {filteredRuns.map((run) => (
              <button className="history-table-row" key={run.run_id} onClick={() => onOpen(run)} type="button">
                <span><strong>{run.task}</strong><small>{run.run_id}</small><small>{formatTimestamp(run.started_at)}</small></span>
                <span className={`history-status ${run.status}`}>{label(run.status)}</span>
                <span className="history-table-metadata">{run.provider}<small>{run.model}</small></span>
                <span className="history-table-metadata">{run.decision_count} decisions<small>{run.draft_count} drafts</small></span>
                <span className="recent-run-open">Open →</span>
              </button>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
