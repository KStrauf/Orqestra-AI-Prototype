"""The first executable Orqestra Studio workflow.

The workflow depends on a tiny text-provider protocol rather than an SDK. That
keeps the orchestration testable with the local mock provider and lets the
OpenAI adapter arrive later without changing the agent manifests or run
recording behavior.
"""

from dataclasses import dataclass
from pathlib import Path
import time
from typing import Mapping

from engine.content import (
    BrandProfile,
    build_hook_candidates,
    grade_drafts,
)
from engine import runrecord
from engine.providers import MockProvider, ProviderReply, TextProvider, resolve_model
from studio.manifest import (
    AgentManifest,
    load_builtin_agents,
    manifest_fingerprint,
)
from studio.plan import (
    WorkflowDefinition,
    compile_workflow,
    content_workflow_definition,
)
from studio.skills import load_content_skills, skill_versions


@dataclass(frozen=True)
class ContentWorkflowRequest:
    """The user-controlled inputs for the first Studio workflow."""

    goal: str
    material: str
    material_name: str = "workflow-material"
    variants: tuple[str, ...] = ("direct", "reflective")
    platform: str = "general"
    audience: str = ""
    outcome: str = ""
    tone: str = "Clear and practical"
    brief: str = ""
    brand_profile: BrandProfile | None = None


@dataclass(frozen=True)
class WorkflowResult:
    """The durable run plus the reviewer output awaiting human approval."""

    record: runrecord.RunRecord
    path: Path
    review_text: str
    agent_plan: str


def _prompt(manifest: AgentManifest, content: str) -> str:
    return f"Instructions:\n{manifest.instructions}\n\n{content}"


ANGLE_LABELS = {
    "direct": "Clear announcement",
    "reflective": "Personal lesson",
    "educational": "Practical how-to",
    "contrarian": "Contrarian take",
}


def run_content_workflow(
    runs_dir: Path,
    request: ContentWorkflowRequest,
    provider: TextProvider | None = None,
    manifests: Mapping[str, AgentManifest] | None = None,
    workflow: WorkflowDefinition | None = None,
) -> WorkflowResult:
    """Run the initial architect → specialist → reviewer workflow."""
    if not request.goal.strip():
        raise ValueError("workflow goal cannot be empty")
    if not request.platform.strip():
        raise ValueError("workflow platform cannot be empty")
    if not request.variants:
        raise ValueError("workflow requires at least one draft variant")

    provider = provider or MockProvider()
    content_skills = load_content_skills()
    content_skill_versions = skill_versions(content_skills)
    agents = dict(manifests or load_builtin_agents())
    compiled = compile_workflow(
        workflow or content_workflow_definition(),
        agents,
    )
    steps = {step.id: step for step in compiled.definition.steps}
    run_id = runrecord.new_run_id()
    started_at = runrecord.utc_now()
    started_clock = time.monotonic()
    material_context = request.material.strip() or (
        "(No source material supplied. Treat the user's goal as the creative "
        "brief, develop useful angles from that idea, and label assumptions.)"
    )
    audience = request.audience.strip() or "Not specified; infer a reasonable audience from the idea."
    outcome = request.outcome.strip() or "Teach or help the audience understand something useful."
    tone = request.tone.strip() or "Clear and practical"
    brief = request.brief.strip() or "No pre-draft brief supplied; propose one from the idea."
    content_context = (
        f"Platform: {request.platform}\n"
        f"Audience: {audience}\n"
        f"Desired outcome: {outcome}\n"
        f"Tone: {tone}\n"
        f"Starter brief: {brief}"
    )
    if request.brand_profile:
        content_context += (
            f"\nCreator voice traits: {', '.join(request.brand_profile.voice_traits) or 'not specified'}"
            f"\nPrimary CTA: {request.brand_profile.primary_cta or 'not specified'}"
        )

    hook_candidates = build_hook_candidates(
        request.goal,
        request.platform,
        request.variants,
        audience,
        request.brand_profile,
    )
    architect = compiled.agent_for(steps["architect"])
    # Each call resolves through the provider boundary. This lets a provider
    # replace provider-neutral manifest models (for example gpt-5.6) with its
    # configured local model while keeping the run trace explicit.
    architect_model = resolve_model(provider, architect.model)
    plan_reply = provider.complete(
        system_prompt=architect.instructions,
        user_prompt=(
            f"Goal: {request.goal}\n"
            f"{content_context}\n"
            f"Content capabilities: {', '.join(content_skills)}\n"
            "Available templates: content_workflow\n"
            "Return a small agent plan."
        ),
        model=architect_model,
        temperature=architect.temperature,
    )
    events = [
        runrecord.RunEvent(
            stage="architect",
            status="completed",
            at=runrecord.utc_now(),
            summary="Created a content direction from the idea, audience, platform, and outcome.",
        )
    ]

    specialist = compiled.agent_for(steps["specialist"])
    specialist_model = resolve_model(provider, specialist.model)
    drafts: list[runrecord.Draft] = []
    replies = [plan_reply]
    for index, variant in enumerate(request.variants, start=1):
        hook_candidate = hook_candidates[index - 1] if index <= len(hook_candidates) else None
        draft_reply = provider.complete(
            system_prompt=_prompt(specialist, f"Agent plan: {plan_reply.text}"),
            user_prompt=(
                f"Goal: {request.goal}\n"
                f"{content_context}\n"
                f"Material: {material_context}\n"
                f"Variant: {variant}\n"
                f"Hook direction: {hook_candidate.text if hook_candidate else 'Choose a grounded opening.'}\n"
                "Return the finished content, not a description of what a draft could say. "
                "Do not repeat the goal as a label or write 'draft for'. Transform the idea "
                "and supplied material into a coherent post with an opening, useful body, "
                "and concrete next action."
            ),
            model=specialist_model,
            temperature=specialist.temperature,
        )
        replies.append(draft_reply)
        draft_id = f"{run_id}#{index}"
        drafts.append(
            runrecord.Draft(
                draft_id=draft_id,
                variant=variant,
                text=draft_reply.text,
                chars=len(draft_reply.text),
                angle=ANGLE_LABELS.get(variant, variant.replace("_", " ").title()),
                hook=(hook_candidate.text if hook_candidate else draft_reply.text.splitlines()[0][:160])
                if draft_reply.text.strip() else "",
                cta="Invite the audience to respond or take the next useful step.",
                platform_fit=f"Drafted for {request.platform}.",
            )
        )
    events.append(
        runrecord.RunEvent(
            stage="specialist",
            status="completed",
            at=runrecord.utc_now(),
            summary=f"Created {len(drafts)} distinct content angles and grounded hook directions for {request.platform}.",
        )
    )

    reviewer = compiled.agent_for(steps["reviewer"])
    reviewer_model = resolve_model(provider, reviewer.model)
    review_reply = provider.complete(
        system_prompt=reviewer.instructions,
        user_prompt=(
            f"Goal: {request.goal}\n"
            f"{content_context}\n"
            f"Material: {material_context}\n"
            "Review constraints: identify unsupported claims, factual gaps, "
            "tone problems, and format errors.\n"
            f"Drafts:\n{chr(10).join(draft.text for draft in drafts)}"
        ),
        model=reviewer_model,
        temperature=reviewer.temperature,
    )
    replies.append(review_reply)
    review_report = runrecord.ReviewReport(
        summary=review_reply.text,
        strongest_draft_id=drafts[0].draft_id if drafts else None,
        strengths=[
            "The drafts are grounded in the supplied material or idea.",
            f"The drafts offer multiple angles for {request.platform}.",
        ],
        risks=[
            "Verify factual claims and add brand-specific examples before publishing."
            if request.material.strip()
            else "The run began from an idea without source material, so verify claims before publishing.",
            "The final voice and call to action still need human review.",
        ],
        recommendations=[
            "Compare the hooks and choose the angle that best fits the audience.",
            "Edit the selected draft for your own voice before approval.",
        ],
    )
    quality_report = grade_drafts(
        drafts,
        request.platform,
        bool(request.material.strip()),
        request.brand_profile,
    )
    events.extend(
        [
            runrecord.RunEvent(
                stage="reviewer",
                status="completed",
                at=runrecord.utc_now(),
                summary="Checked the draft set for grounding, platform fit, and review risks.",
            ),
            runrecord.RunEvent(
                stage="human",
                status="awaiting_approval",
                at=runrecord.utc_now(),
                summary="Waiting for a human to approve, edit, or reject a draft.",
            ),
        ]
    )
    content_brief = runrecord.ContentBrief(
        audience=audience,
        outcome=outcome,
        platform=request.platform,
        tone=tone,
        core_idea=request.goal,
        angles=[ANGLE_LABELS.get(variant, variant.replace("_", " ").title()) for variant in request.variants],
        assumptions=(
            ["No source material was supplied; factual claims require human verification."]
            if not request.material.strip()
            else ["The supplied material is the source of truth for factual claims."]
        ),
    )

    finished_at = runrecord.utc_now()
    usage = runrecord.Usage(
        input_tokens=sum(reply.input_tokens for reply in replies),
        output_tokens=sum(reply.output_tokens for reply in replies),
        cost_usd=sum(reply.cost_usd for reply in replies),
        cost_is_estimate=any(reply.cost_is_estimate for reply in replies),
    )
    record = runrecord.RunRecord(
        run_id=run_id,
        agent="orchestrator",
        task=request.goal,
        started_at=started_at,
        finished_at=finished_at,
        duration_ms=round((time.monotonic() - started_clock) * 1000),
        # RunRecord has one primary model field; use the Specialist model that
        # produced the persisted candidate drafts and retain the provider name.
        provider=provider.name,
        model=specialist_model,
        temperature=specialist.temperature,
        system_prompt=agents["orchestrator"].instructions,
        user_prompt=(
            f"Goal: {request.goal}\n"
            f"{content_context}\n"
            f"Material: {material_context}"
        ),
        content_platform=request.platform,
        audience=audience,
        outcome=outcome,
        tone=tone,
        brief=brief,
        brand_profile=request.brand_profile,
        content_brief=content_brief,
        review_report=review_report,
        events=events,
        skill_versions=content_skill_versions,
        hook_candidates=hook_candidates,
        quality_report=quality_report,
        inputs=[
            runrecord.Input(
                source="workflow",
                path=request.material_name if request.material.strip() else "idea-brief",
                sha256=runrecord.sha256_text(request.material) if request.material else "",
                chars=len(request.material),
                content=request.material or None,
            )
        ],
        template_name=compiled.definition.id,
        template_sha256=manifest_fingerprint(agents),
        usage=usage,
        drafts=drafts,
        status="awaiting_approval",
        agent_plan=plan_reply.text,
        review=review_reply.text,
    )
    path = runrecord.write(runs_dir, record)
    return WorkflowResult(
        record=record,
        path=path,
        review_text=review_reply.text,
        agent_plan=plan_reply.text,
    )
