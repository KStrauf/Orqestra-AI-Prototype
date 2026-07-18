import type {
  CreateWorkflowInput,
  Decision,
  DecisionInput,
  StudioRun,
} from "./types";

const apiBaseUrl = (import.meta.env.VITE_API_URL as string | undefined)?.replace(
  /\/$/,
  "",
);
const demoMode = import.meta.env.VITE_DEMO_MODE !== "false";

export const isDemoMode = demoMode || !apiBaseUrl;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  if (!apiBaseUrl) {
    throw new Error("VITE_API_URL is not configured");
  }
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    throw new Error(`Studio API returned ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function createWorkflow(
  input: CreateWorkflowInput,
): Promise<StudioRun> {
  if (!demoMode) {
    return request<StudioRun>("/api/studio/runs", {
      method: "POST",
      body: JSON.stringify(input),
    });
  }
  return demoRun(input);
}

export async function recordDecision(
  runId: string,
  input: DecisionInput,
): Promise<Decision> {
  if (!demoMode) {
    return request<Decision>(`/api/studio/runs/${runId}/decisions`, {
      method: "POST",
      body: JSON.stringify(input),
    });
  }
  return {
    ...input,
    at: new Date().toISOString(),
  };
}

function demoRun(input: CreateWorkflowInput): StudioRun {
  const runId = `demo-${Date.now()}`;
  const drafts = input.variants.map((variant, index) => ({
    draft_id: `${runId}#${index + 1}`,
    variant,
    text: `${variant[0].toUpperCase()}${variant.slice(1)} draft for ${input.goal}: ${input.material}`,
    chars: 0,
    constraint_violations: [],
  }));
  drafts.forEach((draft) => {
    draft.chars = draft.text.length;
  });
  return {
    run_id: runId,
    agent: "orchestrator",
    task: input.goal,
    provider: "demo",
    model: "local-preview",
    temperature: 0.2,
    status: "awaiting_approval",
    agent_plan:
      "Use the specialist to create two grounded drafts, then route them to review before any publication.",
    review:
      "The drafts are grounded in the supplied material and ready for a human decision.",
    drafts,
    decisions: [],
    published: [],
    usage: {
      input_tokens: 0,
      output_tokens: 0,
      cost_usd: 0,
      cost_is_estimate: false,
    },
  };
}
