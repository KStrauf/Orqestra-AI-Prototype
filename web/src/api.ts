import type {
  CreateWorkflowInput,
  Decision,
  DecisionInput,
  RunSummary,
  StudioRun,
} from "./types";

const apiBaseUrl = (import.meta.env.VITE_API_URL as string | undefined)?.replace(
  /\/$/,
  "",
);
const demoMode = import.meta.env.VITE_DEMO_MODE !== "false";

export const isDemoMode = demoMode || !apiBaseUrl;

export class StudioApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly code?: string,
    public readonly details?: unknown,
  ) {
    super(message);
    this.name = "StudioApiError";
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  if (!apiBaseUrl) {
    throw new Error("VITE_API_URL is not configured");
  }
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    let payload: unknown = null;
    try {
      payload = await response.json();
    } catch {
      // Keep the status-based fallback when the service returns no JSON body.
    }
    const envelope = isRecord(payload) && isRecord(payload.error) ? payload.error : null;
    const detail = isRecord(payload) ? payload.detail : undefined;
    const message =
      (envelope && typeof envelope.message === "string" && envelope.message) ||
      (typeof detail === "string" && detail) ||
      `Studio API returned ${response.status}`;
    throw new StudioApiError(
      message,
      response.status,
      envelope && typeof envelope.code === "string" ? envelope.code : undefined,
      envelope?.details,
    );
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

export async function listRuns(limit = 20): Promise<RunSummary[]> {
  if (demoMode) return [];
  const response = await request<{ runs: RunSummary[] }>(
    `/api/studio/runs?limit=${limit}`,
  );
  return response.runs;
}

export async function getRun(runId: string): Promise<StudioRun> {
  if (demoMode) {
    throw new Error("Demo runs are available only in the current session");
  }
  return request<StudioRun>(`/api/studio/runs/${runId}`);
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
    started_at: new Date().toISOString(),
    finished_at: new Date().toISOString(),
    provider: "demo",
    model: "local-preview",
    temperature: 0.2,
    inputs: [{
      source: "workflow",
      path: input.material_name,
      sha256: "",
      chars: input.material.length,
      content: input.material,
    }],
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
