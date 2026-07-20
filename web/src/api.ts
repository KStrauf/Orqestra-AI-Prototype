import type {
  CreateWorkflowInput,
  BrandProfile,
  Decision,
  DecisionInput,
  IdeaCoachInput,
  IdeaCoachResult,
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

export async function getBrandProfile(): Promise<BrandProfile | null> {
  if (demoMode) return null;
  return request<BrandProfile | null>("/api/studio/brand-profile");
}

export async function saveBrandProfile(profile: BrandProfile): Promise<BrandProfile> {
  if (demoMode) return profile;
  return request<BrandProfile>("/api/studio/brand-profile", {
    method: "PUT",
    body: JSON.stringify(profile),
  });
}

export async function coachIdea(input: IdeaCoachInput): Promise<IdeaCoachResult> {
  if (!demoMode) {
    return request<IdeaCoachResult>("/api/studio/idea-coach", {
      method: "POST",
      body: JSON.stringify(input),
    });
  }
  const idea = input.idea.trim().replace(/\.+$/, "");
  const audience = input.audience?.trim() || "people who will find the idea useful";
  const outcome = input.outcome?.trim() || "Teach the audience something useful";
  const tone = input.tone?.trim() || "Clear and practical";
  const directions = [
    {
      direction_id: "practical-breakdown",
      title: `Make ${idea} practical`,
      format: "Step-by-step post",
      why_it_fits: `Show ${audience} what to do with the idea instead of only naming it.`,
      opening: `Start with the one choice that makes ${idea} useful.`,
      next_step: "Give the reader one action they can try today.",
    },
    {
      direction_id: "beginner-guide",
      title: `Explain ${idea} for a beginner`,
      format: "Beginner-friendly explainer",
      why_it_fits: `Translate the idea into plain language for ${audience}.`,
      opening: `If ${idea.toLowerCase()} feels harder than it should, begin with this simple distinction.`,
      next_step: "Define the first step and one common mistake to avoid.",
    },
    {
      direction_id: "point-of-view",
      title: `Take a point of view on ${idea}`,
      format: "Opinion-led post",
      why_it_fits: "Give the idea a clear position so the audience understands why it matters.",
      opening: `The useful question is not whether ${idea.toLowerCase()} matters. It is how to use it well.`,
      next_step: "Support the point of view with one example and invite a specific response.",
    },
  ];
  const recommended = directions[0];
  const samplePost = `${recommended.opening}\n\nIf you are exploring ${idea.toLowerCase()}, do not stop at the label. Explain what it helps someone do, when it is useful, and where to begin.\n\nStart with one concrete example for ${audience}. Then give one next step. ${recommended.next_step}`;
  const starterBrief = [
    `Audience: ${audience}`,
    `Outcome: ${outcome}`,
    `Voice: ${tone}`,
    `Core idea: ${idea}`,
    `Recommended direction: ${recommended.title}`,
    `Format: ${recommended.format}`,
    `Opening: ${recommended.opening}`,
    `Next step: ${recommended.next_step}`,
    "",
    "Assumption: Replace general statements with supplied facts, examples, or personal experience before approval.",
  ].join("\n");
  return {
    recommended_direction_id: recommended.direction_id,
    recommendation: `Start with a practical breakdown for ${audience}. It gives the idea a clear promise and a useful next step for ${input.platform}.`,
    audience,
    outcome,
    tone,
    directions,
    sample_post: samplePost,
    starter_brief: starterBrief,
    assumptions: [
      "The idea is the source of truth until the user adds supporting material.",
      "Specific claims, names, and examples should be supplied or verified before approval.",
    ],
  };
}

function demoRun(input: CreateWorkflowInput): StudioRun {
  const runId = `demo-${Date.now()}`;
  const drafts = input.variants.map((variant, index) => ({
    draft_id: `${runId}#${index + 1}`,
    variant,
    text: demoDraftText(input, variant),
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
    content_platform: input.platform,
    status: "awaiting_approval",
    agent_plan:
      "Use the specialist to create distinct grounded drafts, then route them to review before any publication.",
    review:
      "The drafts are grounded in the supplied material and ready for a human decision.",
    drafts,
    decisions: [],
    published: [],
    hook_candidates: input.variants.slice(0, 3).map((variant, index) => ({
      hook_id: `hook-${index + 1}`,
      pattern: index === 0 ? "clear claim" : index === 1 ? "audience question" : "practical lesson",
      text: index === 0
        ? `A clear way to approach ${input.goal}: start with the audience's next useful step.`
        : index === 1
          ? `What would ${input.platform} readers need to understand before acting on ${input.goal}?`
          : `The useful lesson behind ${input.goal} is easier to apply when the first step is concrete.`,
      rationale: "A grounded opening direction for human comparison.",
      variant,
    })),
    quality_report: {
      platform: input.platform,
      overall: input.material.trim() ? 7 : 5,
      scores: { grounding: input.material.trim() ? 8 : 5, platform_fit: 8, voice_fit: 5, actionability: 6 },
      issues: input.material.trim() ? ["No saved voice profile was supplied."] : ["The run started from an idea; verify factual claims.", "No saved voice profile was supplied."],
      recommendations: ["Compare the hook, audience fit, and next step before deciding."],
      method: "Demo checks for review orientation; not an engagement prediction.",
    },
    skill_versions: {
      brand_context: "1.0.0",
      idea_coach: "1.0.0",
      hook_strategist: "1.0.0",
      post_writer: "1.0.0",
      post_grader: "1.0.0",
    },
    usage: {
      input_tokens: 0,
      output_tokens: 0,
      cost_usd: 0,
      cost_is_estimate: false,
    },
  };
}

function demoDraftText(input: CreateWorkflowInput, variant: string): string {
  const goal = input.goal.trim().replace(/[?.!]$/, "");
  const normalizedGoal = goal.toLowerCase();
  const prefixes = ["how do i ", "how to ", "write a post about ", "create a post about "];
  const prefix = prefixes.find((candidate) => normalizedGoal.startsWith(candidate));
  const topic = prefix ? goal.slice(prefix.length).trim() : goal;
  const source = input.material.trim() || "No source material was supplied, so add one fact or example from your experience before approval.";
  const audience = input.audience?.trim() || "your audience";
  const outcome = input.outcome?.trim() || "give the audience a useful next step";
  const hook = "Start with the clearest useful point.";
  if (variant === "reflective") {
    return `${hook}\n\nThe useful lesson in ${topic.toLowerCase()} is to make the first step concrete for ${audience}. Use this context as your starting point: ${source}.\n\nThen ask what would make the next step easier for someone else. That keeps the post focused on ${outcome.toLowerCase()} instead of repeating the idea.\n\nPlatform: ${input.platform}.`;
  }
  if (variant === "educational") {
    return `How to approach ${topic.toLowerCase()}:\n\n1. Start with the problem or question your audience has.\n2. Use this supplied context: ${source}.\n3. End with one action that helps ${audience} move forward.\n\nThe goal is to ${outcome.toLowerCase()} without asking the reader to fill in the missing steps.\n\nPlatform: ${input.platform}.`;
  }
  if (variant === "contrarian") {
    return `The obvious way to talk about ${topic.toLowerCase()} is to list the answer. A more useful post starts with the decision behind it.\n\nUse this grounded detail: ${source}. Then explain what you would do first and why. Give ${audience} a practical way to respond or try it.\n\nPlatform: ${input.platform}.`;
  }
  const directOpening = prefix === "write a post about " || prefix === "create a post about "
    ? `A useful post about ${topic.toLowerCase()} starts with the clearest practical point.`
    : `Trying to ${topic.toLowerCase()}? Start with the clearest useful step.`;
  return `${directOpening}\n\nHere is the context to work from: ${source}. Turn it into one concrete recommendation for ${audience}, then tell the reader what to do next.\n\nNext step: ${outcome}.\n\nPlatform: ${input.platform}.`;
}
