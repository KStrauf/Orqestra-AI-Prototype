export type RunStatus =
  | "awaiting_approval"
  | "decided"
  | "published"
  | "completed"
  | "failed";

export type DecisionKind = "approve" | "edit" | "reject";

export interface Draft {
  draft_id: string;
  variant: string;
  text: string;
  chars: number;
  constraint_violations: string[];
}

export interface RunInput {
  source: string;
  path: string;
  sha256: string;
  chars: number;
  content?: string | null;
}

export interface Decision {
  draft_id: string;
  decision: DecisionKind;
  at: string;
  reason_tag?: string;
  reason?: string;
  edited_text?: string;
  diff?: string;
}

export interface Usage {
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  cost_is_estimate: boolean;
}

export interface StudioRun {
  run_id: string;
  agent: string;
  task: string;
  started_at: string;
  finished_at?: string | null;
  provider: string;
  model: string;
  temperature: number;
  inputs: RunInput[];
  status: RunStatus;
  agent_plan: string | null;
  review: string | null;
  drafts: Draft[];
  decisions: Decision[];
  published: Array<{
    draft_id: string;
    at: string;
    platform: string;
    url: string;
  }>;
  usage?: Usage;
}

export interface RunSummary {
  run_id: string;
  agent: string;
  task: string;
  started_at: string;
  finished_at?: string | null;
  provider: string;
  model: string;
  status: RunStatus;
  draft_count: number;
  decision_count: number;
  published_count: number;
}

export interface CreateWorkflowInput {
  goal: string;
  material: string;
  material_name: string;
  variants: string[];
}

export interface DecisionInput {
  draft_id: string;
  decision: DecisionKind;
  reason_tag?: string;
  reason?: string;
  edited_text?: string;
}
