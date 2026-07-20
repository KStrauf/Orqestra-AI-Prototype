"""Typed HTTP contracts for the Orqestra Studio API."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from engine.runrecord import RunRecord


DecisionKind = Literal["approve", "edit", "reject"]


class BrandProfileRequest(BaseModel):
    """Optional creator context supplied with a workflow request."""

    profile_id: str = "default"
    name: str = ""
    audience: str = ""
    voice_traits: list[str] = Field(default_factory=list)
    primary_cta: str = ""
    strong_opinions: list[str] = Field(default_factory=list)
    story_vault: list[str] = Field(default_factory=list)
    social_links: dict[str, str] = Field(default_factory=dict)
    version: int = 1
    updated_at: str = ""


class BrandProfileResponse(BrandProfileRequest):
    """Creator context returned by the durable profile endpoint."""

    pass


class CreateRunRequest(BaseModel):
    """Inputs accepted by the Studio workflow composer."""

    goal: str
    material: str = ""
    material_name: str = "workflow-material"
    variants: list[str] = Field(default_factory=lambda: ["direct", "reflective"])
    platform: str = "general"
    audience: str = ""
    outcome: str = ""
    tone: str = "Clear and practical"
    brief: str = ""
    brand_profile: BrandProfileRequest | None = None


class IdeaCoachRequest(BaseModel):
    """Inputs for shaping an incomplete content idea before drafting."""

    idea: str
    platform: str = "general"
    audience: str = ""
    outcome: str = ""
    tone: str = ""
    brand_profile: BrandProfileRequest | None = None


class DecisionRequest(BaseModel):
    """A human decision recorded against one draft."""

    draft_id: str
    decision: DecisionKind
    reason_tag: str | None = None
    reason: str | None = None
    edited_text: str | None = None


class InputResponse(BaseModel):
    source: str
    path: str
    sha256: str
    chars: int
    content: str | None = None


class UsageResponse(BaseModel):
    input_tokens: int
    output_tokens: int
    cost_usd: float
    cost_is_estimate: bool


class DraftResponse(BaseModel):
    draft_id: str
    variant: str
    text: str
    chars: int
    constraint_violations: list[str] = Field(default_factory=list)
    angle: str = ""
    hook: str = ""
    cta: str = ""
    platform_fit: str = ""


class ContentBriefResponse(BaseModel):
    audience: str
    outcome: str
    platform: str
    tone: str
    core_idea: str
    angles: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class ReviewReportResponse(BaseModel):
    summary: str
    strongest_draft_id: str | None = None
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class HookCandidateResponse(BaseModel):
    hook_id: str
    pattern: str
    text: str
    rationale: str
    variant: str = ""


class QualityReportResponse(BaseModel):
    platform: str
    overall: int
    scores: dict[str, int] = Field(default_factory=dict)
    issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    method: str


class IdeaDirectionResponse(BaseModel):
    direction_id: str
    title: str
    format: str
    why_it_fits: str
    opening: str
    next_step: str


class IdeaCoachResponse(BaseModel):
    recommended_direction_id: str
    recommendation: str
    audience: str
    outcome: str
    tone: str
    directions: list[IdeaDirectionResponse] = Field(default_factory=list)
    sample_post: str
    starter_brief: str
    assumptions: list[str] = Field(default_factory=list)


class RunEventResponse(BaseModel):
    stage: str
    status: str
    at: str
    summary: str


class DecisionResponse(BaseModel):
    draft_id: str
    decision: DecisionKind
    at: str
    reason_tag: str | None = None
    reason: str | None = None
    edited_text: str | None = None
    diff: str | None = None


class PublishedResponse(BaseModel):
    draft_id: str
    at: str
    platform: str
    url: str


class RunResponse(BaseModel):
    """The complete durable run representation returned by Studio."""

    model_config = ConfigDict(extra="ignore")

    run_id: str
    agent: str
    task: str
    started_at: str
    finished_at: str | None = None
    duration_ms: int | None = None
    provider: str
    model: str
    temperature: float
    content_platform: str = "general"
    audience: str = ""
    outcome: str = ""
    tone: str = "Clear and practical"
    brief: str = ""
    brand_profile: BrandProfileRequest | None = None
    content_brief: ContentBriefResponse | None = None
    review_report: ReviewReportResponse | None = None
    events: list[RunEventResponse] = Field(default_factory=list)
    skill_versions: dict[str, str] = Field(default_factory=dict)
    hook_candidates: list[HookCandidateResponse] = Field(default_factory=list)
    quality_report: QualityReportResponse | None = None
    system_prompt: str
    user_prompt: str
    inputs: list[InputResponse] = Field(default_factory=list)
    template_name: str | None = None
    template_sha256: str | None = None
    voice_sha256: str | None = None
    voice_feedback_entries_used: int = 0
    voice_exemplars_used: int = 0
    usage: UsageResponse | None = None
    drafts: list[DraftResponse] = Field(default_factory=list)
    error: str | None = None
    status: str
    agent_plan: str | None = None
    review: str | None = None
    decisions: list[DecisionResponse] = Field(default_factory=list)
    published: list[PublishedResponse] = Field(default_factory=list)
    schema_version: int


class RunSummaryResponse(BaseModel):
    """Compact representation used by the run history endpoint."""

    run_id: str
    agent: str
    task: str
    started_at: str
    finished_at: str | None = None
    provider: str
    model: str
    content_platform: str = "general"
    status: str
    draft_count: int
    decision_count: int
    published_count: int


class RunListResponse(BaseModel):
    """A newest-first page of durable Studio runs."""

    runs: list[RunSummaryResponse]
    count: int
    limit: int


class ErrorBody(BaseModel):
    code: str
    message: str
    details: object | None = None


class ErrorResponse(BaseModel):
    """Normalized error envelope with a legacy-compatible ``detail`` field."""

    detail: object
    error: ErrorBody


def run_response(record: RunRecord) -> RunResponse:
    """Validate a durable record at the HTTP boundary."""

    from dataclasses import asdict

    payload = asdict(record)
    return RunResponse.model_validate(payload)


def run_summary(record: RunRecord) -> RunSummaryResponse:
    """Build the stable, compact representation used by run history."""

    from dataclasses import asdict

    data = asdict(record)
    return RunSummaryResponse(
        run_id=data["run_id"],
        agent=data["agent"],
        task=data["task"],
        started_at=data["started_at"],
        finished_at=data.get("finished_at"),
        provider=data["provider"],
        model=data["model"],
        content_platform=data.get("content_platform", "general"),
        status=data["status"],
        draft_count=len(data.get("drafts", [])),
        decision_count=len(data.get("decisions", [])),
        published_count=len(data.get("published", [])),
    )
