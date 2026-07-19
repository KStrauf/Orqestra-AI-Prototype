import type { FormEvent } from "react";
import { ComposerPanel } from "./ComposerPanel";

interface NewRunPageProps {
  goal: string;
  material: string;
  busy: boolean;
  onGoalChange: (value: string) => void;
  onMaterialChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

export function NewRunPage(props: NewRunPageProps) {
  return (
    <div className="page-stack">
      <header className="page-header">
        <div>
          <span className="eyebrow">NEW RUN</span>
          <h1>Create a new workflow.</h1>
          <p>Give the team a clear outcome and the material it should use.</p>
        </div>
      </header>
      <div className="new-run-layout">
        <ComposerPanel {...props} />
        <aside className="helper-card">
          <span className="eyebrow">WHAT HAPPENS NEXT</span>
          <div className="helper-steps">
            <div><strong>01</strong><span><b>Architect plans</b><small>chooses the smallest useful team</small></span></div>
            <div><strong>02</strong><span><b>Specialist drafts</b><small>creates multiple variants</small></span></div>
            <div><strong>03</strong><span><b>Reviewer checks</b><small>flags gaps and risks</small></span></div>
            <div><strong>04</strong><span><b>You decide</b><small>approve, edit, or reject</small></span></div>
          </div>
          <div className="helper-safety"><span>⌑</span><p>Nothing publishes automatically. The final decision stays with you.</p></div>
        </aside>
      </div>
    </div>
  );
}
