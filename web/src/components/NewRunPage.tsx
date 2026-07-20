import type { FormEvent } from "react";
import { ComposerPanel } from "./ComposerPanel";

interface NewRunPageProps {
  goal: string;
  material: string;
  platform: string;
  audience: string;
  outcome: string;
  tone: string;
  brief: string;
  busy: boolean;
  onGoalChange: (value: string) => void;
  onMaterialChange: (value: string) => void;
  onPlatformChange: (value: string) => void;
  onAudienceChange: (value: string) => void;
  onOutcomeChange: (value: string) => void;
  onToneChange: (value: string) => void;
  onBriefChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

export function NewRunPage(props: NewRunPageProps) {
  return (
    <div className="page-stack">
      <header className="page-header">
        <div>
          <span className="eyebrow">CREATE CONTENT</span>
          <h1>Turn an idea into content.</h1>
          <p>Give the team an idea or source material, and let it shape the first directions.</p>
        </div>
      </header>
      <div className="new-run-layout">
        <ComposerPanel {...props} />
        <aside className="helper-card">
          <span className="eyebrow">HOW ORQESTRA HELPS</span>
          <p className="helper-intro">You do not need a finished brief or a brand voice. Give the team an idea and it will help shape the first directions.</p>
          <div className="helper-steps">
            <div><strong>01</strong><span><b>Architect finds an angle</b><small>turns your idea into a useful brief</small></span></div>
            <div><strong>02</strong><span><b>Specialist drafts</b><small>creates multiple content directions</small></span></div>
            <div><strong>03</strong><span><b>Reviewer checks</b><small>flags gaps, risks, and assumptions</small></span></div>
            <div><strong>04</strong><span><b>You decide</b><small>approve, edit, or reject</small></span></div>
          </div>
          <div className="helper-safety"><span>⌑</span><p>Nothing publishes automatically. The final decision stays with you.</p></div>
        </aside>
      </div>
    </div>
  );
}
