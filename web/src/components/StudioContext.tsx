interface StudioContextProps {
  environmentLabel: string;
}

export function StudioContext({ environmentLabel }: StudioContextProps) {
  return (
    <div className="studio-context">
      <h3>How the team works</h3>
      <div className="context-agent-list">
        <div><span className="context-agent-number">01</span><span><strong>Architect</strong><small>plans the workflow</small></span></div>
        <div><span className="context-agent-number">02</span><span><strong>Specialist</strong><small>creates draft variants</small></span></div>
        <div><span className="context-agent-number">03</span><span><strong>Reviewer</strong><small>checks before you decide</small></span></div>
      </div>
      <div className="context-safety">
        <span className="eyebrow">SAFETY NOTE</span>
        <p>Nothing publishes automatically. You remain the final decision-maker.</p>
      </div>
      <div className="context-environment">
        <span className="eyebrow">ENVIRONMENT</span>
        <strong>{environmentLabel}</strong>
        <p>Provider selection is owned by the Studio service.</p>
      </div>
    </div>
  );
}
