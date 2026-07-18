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


@dataclass(frozen=True)
class ContentWorkflowRequest:
    """The user-controlled inputs for the first Studio workflow."""

    goal: str
    material: str
    material_name: str = "workflow-material"
    variants: tuple[str, ...] = ("direct", "reflective")


@dataclass(frozen=True)
class WorkflowResult:
    """The durable run plus the reviewer output awaiting human approval."""

    record: runrecord.RunRecord
    path: Path
    review_text: str
    agent_plan: str


def _prompt(manifest: AgentManifest, content: str) -> str:
    return f"Instructions:\n{manifest.instructions}\n\n{content}"


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
    if not request.material.strip():
        raise ValueError("workflow material cannot be empty")
    if not request.variants:
        raise ValueError("workflow requires at least one draft variant")

    provider = provider or MockProvider()
    agents = dict(manifests or load_builtin_agents())
    compiled = compile_workflow(
        workflow or content_workflow_definition(),
        agents,
    )
    steps = {step.id: step for step in compiled.definition.steps}
    run_id = runrecord.new_run_id()
    started_at = runrecord.utc_now()
    started_clock = time.monotonic()

    architect = compiled.agent_for(steps["architect"])
    architect_model = resolve_model(provider, architect.model)
    plan_reply = provider.complete(
        system_prompt=architect.instructions,
        user_prompt=(
            f"Goal: {request.goal}\n"
            "Available templates: content_workflow\n"
            "Return a small agent plan."
        ),
        model=architect_model,
        temperature=architect.temperature,
    )

    specialist = compiled.agent_for(steps["specialist"])
    specialist_model = resolve_model(provider, specialist.model)
    drafts: list[runrecord.Draft] = []
    replies = [plan_reply]
    for index, variant in enumerate(request.variants, start=1):
        draft_reply = provider.complete(
            system_prompt=_prompt(specialist, f"Agent plan: {plan_reply.text}"),
            user_prompt=(
                f"Goal: {request.goal}\n"
                f"Material: {request.material}\n"
                f"Variant: {variant}"
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
            )
        )

    reviewer = compiled.agent_for(steps["reviewer"])
    reviewer_model = resolve_model(provider, reviewer.model)
    review_reply = provider.complete(
        system_prompt=reviewer.instructions,
        user_prompt=(
            f"Goal: {request.goal}\n"
            f"Material: {request.material}\n"
            "Review constraints: identify unsupported claims, factual gaps, "
            "tone problems, and format errors.\n"
            f"Drafts:\n{chr(10).join(draft.text for draft in drafts)}"
        ),
        model=reviewer_model,
        temperature=reviewer.temperature,
    )
    replies.append(review_reply)

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
        provider=provider.name,
        model=specialist_model,
        temperature=specialist.temperature,
        system_prompt=agents["orchestrator"].instructions,
        user_prompt=f"Goal: {request.goal}\nMaterial: {request.material}",
        inputs=[
            runrecord.Input(
                source="workflow",
                path=request.material_name,
                sha256=runrecord.sha256_text(request.material),
                chars=len(request.material),
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
