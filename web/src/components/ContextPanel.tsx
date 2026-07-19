import type { ReactNode } from "react";

interface ContextPanelProps {
  children: ReactNode;
}

export function ContextPanel({ children }: ContextPanelProps) {
  return (
    <aside className="context-panel" id="trace" aria-label="Context and trust signals">
      <div className="context-panel-heading">
        <span className="eyebrow">STUDIO CONTEXT</span>
        <span className="context-lock">⌑</span>
      </div>
      {children}
    </aside>
  );
}
