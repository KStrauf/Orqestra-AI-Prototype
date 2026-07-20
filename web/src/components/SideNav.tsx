interface SideNavProps {
  activeRunId: string | null;
  activeRoute: string;
  onNewRun: () => void;
}

export function SideNav({ activeRunId, activeRoute, onNewRun }: SideNavProps) {
  const itemClass = (route: string) =>
    `nav-item ${activeRoute === route ? "active" : ""}`;

  return (
    <aside className="sidebar" aria-label="Studio navigation">
      <nav className="nav-list" aria-label="Primary navigation">
        <a className={itemClass("dashboard")} href="#/"><span>✦</span> Dashboard</a>
        <a className={itemClass("new-run")} href="#/runs/new" onClick={onNewRun}><span>＋</span> New run</a>
        <a className={itemClass("run")} href={activeRunId ? `#/runs/${activeRunId}` : "#/history"}><span>◈</span> Runs</a>
        <a className={itemClass("history")} href="#/history"><span>◷</span> History</a>
        <a className={itemClass("trace")} href={activeRunId ? `#/trace/${activeRunId}` : "#/history"}><span>⌁</span> Trace</a>
        <a className={itemClass("settings")} href="#/settings"><span>⚙</span> Settings</a>
      </nav>
      <div className="sidebar-footer">
        <div className="status-dot" />
        <div>
          <strong>Human gate active</strong>
          <span>Nothing publishes automatically</span>
        </div>
      </div>
    </aside>
  );
}
