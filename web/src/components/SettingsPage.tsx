interface SettingsPageProps {
  environmentLabel: string;
  provider: string;
  model: string;
}

export function SettingsPage({ environmentLabel, provider, model }: SettingsPageProps) {
  return (
    <div className="page-stack">
      <header className="page-header"><div><span className="eyebrow">SETTINGS</span><h1>Studio environment.</h1><p>Understand the active runtime without exposing unsafe controls in the hackathon MVP.</p></div></header>
      <div className="settings-grid">
        <section className="settings-card"><span className="eyebrow">ENVIRONMENT</span><h2>{environmentLabel}</h2><div className="settings-fact"><span>Provider</span><strong>{provider}</strong></div><div className="settings-fact"><span>Model</span><strong>{model}</strong></div><p className="settings-note">Provider selection is owned by the backend service. The frontend reports the active run metadata.</p></section>
        <section className="settings-card safety-card"><span className="eyebrow">SAFETY</span><h2>Human gate enabled</h2><p>Orqestra creates reviewable content. Nothing publishes automatically, and every draft decision is recorded with the run.</p><div className="safety-badge">⌑ Human approval required</div></section>
      </div>
    </div>
  );
}
