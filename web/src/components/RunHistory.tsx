import type { RunSummary } from "../types";

interface RunHistoryProps {
  runs: RunSummary[];
  activeRunId: string | null;
  loading: boolean;
  onSelect: (run: RunSummary) => void;
}

function formatDate(timestamp: string): string {
  const date = new Date(timestamp);
  if (Number.isNaN(date.valueOf())) return "Unknown time";
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export function RunHistory({
  runs,
  activeRunId,
  loading,
  onSelect,
}: RunHistoryProps) {
  return (
    <section className="history-panel" id="runs" aria-labelledby="history-title">
      <div className="history-heading">
        <span className="eyebrow" id="history-title">RUN HISTORY</span>
        <span className="history-count">{runs.length}</span>
      </div>
      {loading ? (
        <p className="history-empty">Loading saved runs…</p>
      ) : runs.length === 0 ? (
        <p className="history-empty">Runs from this session will appear here.</p>
      ) : (
        <div className="history-list">
          {runs.map((run) => (
            <button
              className={`history-item ${run.run_id === activeRunId ? "selected" : ""}`}
              key={run.run_id}
              onClick={() => onSelect(run)}
              type="button"
            >
              <span className="history-item-top">
                <strong>{run.task}</strong>
                <span className={`history-status ${run.status}`}>{run.status.replaceAll("_", " ")}</span>
              </span>
              <span className="history-item-meta">
                {formatDate(run.started_at)} · {run.draft_count} drafts
              </span>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
