interface TopBarProps {
  environmentLabel: string;
  onNewRun: () => void;
}

export function TopBar({ environmentLabel, onNewRun }: TopBarProps) {
  return (
    <header className="topbar global-topbar">
      <a className="global-brand" href="#/" aria-label="Orqestra Studio home">
        <span className="brand-mark">O</span>
        <span>
          <strong>Orqestra Studio</strong>
          <small>Review-first agent workspace</small>
        </span>
      </a>
      <div className="global-actions">
        <span className="environment-badge">
          <span className="status-dot" />
          {environmentLabel}
        </span>
        <a className="topbar-action primary" href="#/runs/new" onClick={onNewRun}>New run</a>
        <a className="topbar-action" href="#/settings">Settings</a>
      </div>
    </header>
  );
}
