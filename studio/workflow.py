"""The first executable Orqestra Studio workflow.

The workflow depends on a tiny text-provider protocol rather than an SDK. That
keeps the orchestration testable with the local mock provider and lets the
OpenAI adapter arrive later without changing the agent manifests or run
recording behavior.
"""

from dataclasses import dataclass
from pathlib import Path
import time
from typing import Protocol

from engine import runrecord
from studio.manifest import AgentManifest, load_builtin_agents


@dataclass(frozen=True)
class ProviderReply:
    """The provider-neutral result of one model call."""

    text: str
    input_tokens: int
    output_tokens: int
    cost_usd: float = 0.0
    cost_is_estimate: bool = True


class TextProvider(Protocol):
    """The smallest interface the Studio workflow needs from a model provider."""

    name: str

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float,
    ) -> ProviderReply:
        """Generate one text response."""


class MockProvider:
    """A deterministic provider for local development and the demo fixture."""

    name = "mock"

    def __init__(self) -> None:
        self.calls: list[dict[str, str | float]] = []

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float,
    ) -> ProviderReply:
        self.calls.append(
            {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "model": model,
                "temperature": temperature,
            }
        )
        if "Variant:" in user_prompt:
            variant = _prompt_value(user_prompt, "Variant") or "default"
            goal = _prompt_value(user_prompt, "Goal") or "the requested task"
            material = _prompt_value(user_prompt, "Material") or "the supplied material"
            text = f"{variant.title()} draft for {goal}: {material}"
        elif "agent plan" in user_prompt.lower():
            text = "Use the specialist to create two drafts, then send both to the reviewer."
        elif "review" in system_prompt.lower() or "Drafts:" in user_prompt:
            text = "Review: the drafts are grounded in the supplied material and ready for human approval."
        else:
            text = "The workflow completed without a specialized output."

        return ProviderReply(
            text=text,
            input_tokens=max(1, len(system_prompt + user_prompt) // 4),
            output_tokens=max(1, len(text) // 4),
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


def _prompt_value(prompt: str, label: str) -> str | None:
    prefix = f"{label}:"
    for line in prompt.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def _prompt(manifest: AgentManifest, content: str) -> str:
    return f"Instructions:\n{manifest.instructions}\n\n{content}"


def run_content_workflow(
    runs_dir: Path,
    request: ContentWorkflowRequest,
    provider: TextProvider | None = None,
) -> WorkflowResult:
    """Run the initial architect → specialist → reviewer workflow."""
    if not request.goal.strip():
        raise ValueError("workflow goal cannot be empty")
    if not request.material.strip():
        raise ValueError("workflow material cannot be empty")
    if not request.variants:
        raise ValueError("workflow requires at least one draft variant")

    provider = provider or MockProvider()
    agents = load_builtin_agents()
    run_id = runrecord.new_run_id()
    started_at = runrecord.utc_now()
    started_clock = time.monotonic()

    architect = agents["architect"]
    plan_reply = provider.complete(
        system_prompt=architect.instructions,
        user_prompt=(
            f"Goal: {request.goal}\n"
            "Available templates: content_workflow\n"
            "Return a small agent plan."
        ),
        model=architect.model,
        temperature=architect.temperature,
    )

    specialist = agents["specialist"]
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
            model=specialist.model,
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

    reviewer = agents["reviewer"]
    review_reply = provider.complete(
        system_prompt=reviewer.instructions,
        user_prompt=(
            f"Goal: {request.goal}\n"
            f"Drafts:\n{chr(10).join(draft.text for draft in drafts)}"
        ),
        model=reviewer.model,
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
        model=specialist.model,
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
        template_name="content_workflow",
        template_sha256=runrecord.sha256_text(
            "\n".join(sorted(agents))
        ),
        usage=usage,
        drafts=drafts,
    )
    path = runrecord.write(runs_dir, record)
    return WorkflowResult(
        record=record,
        path=path,
        review_text=review_reply.text,
        agent_plan=plan_reply.text,
    )
