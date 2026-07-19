import type { StudioRun } from "../types";

interface PipelinePanelProps {
  run: StudioRun;
}

export function PipelinePanel({ run }: PipelinePanelProps) {
  const steps = [
    ["01", "Architect", "Plan recorded"],
    ["02", "Specialist", `${run.drafts.length} drafts produced`],
    ["03", "Reviewer", "Human decision required"],
  ];

  return (
    <div className="agent-pipeline" aria-label="Workflow pipeline">
      {steps.map(([number, name, detail], index) => (
        <div className="pipeline-step" key={name}>
          <div className="pipeline-number">{number}</div>
          <div>
            <strong>{name}</strong>
            <span>{detail}</span>
          </div>
          {index < steps.length - 1 && <div className="pipeline-line" />}
        </div>
      ))}
    </div>
  );
}
