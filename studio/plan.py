"""Typed workflow definitions and compilation for Orqestra Studio."""

from dataclasses import dataclass
from typing import Mapping

from engine.errors import WorkflowError
from studio.manifest import AgentManifest


@dataclass(frozen=True)
class WorkflowStep:
    """One executable step in a workflow definition."""

    id: str
    agent_id: str
    output_type: str
    depends_on: tuple[str, ...] = ()
    fan_out: bool = False
    requires_approval: bool = False


@dataclass(frozen=True)
class WorkflowDefinition:
    """A versioned, executable workflow topology."""

    id: str
    version: int
    steps: tuple[WorkflowStep, ...]


@dataclass(frozen=True)
class CompiledWorkflow:
    """A validated workflow with every step resolved to a manifest."""

    definition: WorkflowDefinition
    agents: Mapping[str, AgentManifest]

    def agent_for(self, step: WorkflowStep) -> AgentManifest:
        return self.agents[step.agent_id]


def content_workflow_definition() -> WorkflowDefinition:
    """Return the narrow workflow used by the Studio content demo."""
    return WorkflowDefinition(
        id="content_workflow",
        version=1,
        steps=(
            WorkflowStep(
                id="architect",
                agent_id="architect",
                output_type="agent_plan",
            ),
            WorkflowStep(
                id="specialist",
                agent_id="specialist",
                output_type="draft",
                depends_on=("architect",),
                fan_out=True,
            ),
            WorkflowStep(
                id="reviewer",
                agent_id="reviewer",
                output_type="review",
                depends_on=("specialist",),
                requires_approval=True,
            ),
        ),
    )


def compile_workflow(
    definition: WorkflowDefinition,
    manifests: Mapping[str, AgentManifest],
) -> CompiledWorkflow:
    """Validate topology and resolve every step to an existing manifest."""
    if not definition.steps:
        raise WorkflowError(f"workflow '{definition.id}' has no steps")
    if definition.version < 1:
        raise WorkflowError(f"workflow '{definition.id}' has an invalid version")

    steps_by_id: dict[str, WorkflowStep] = {}
    for step in definition.steps:
        if step.id in steps_by_id:
            raise WorkflowError(f"workflow has duplicate step ID '{step.id}'")
        if step.agent_id not in manifests:
            raise WorkflowError(
                f"workflow step '{step.id}' references unknown agent '{step.agent_id}'"
            )
        if manifests[step.agent_id].output_type != step.output_type:
            raise WorkflowError(
                f"workflow step '{step.id}' expects '{step.output_type}', "
                f"but agent '{step.agent_id}' produces '{manifests[step.agent_id].output_type}'"
            )
        steps_by_id[step.id] = step

    for step in definition.steps:
        missing = sorted(set(step.depends_on) - set(steps_by_id))
        if missing:
            raise WorkflowError(
                f"workflow step '{step.id}' has unknown dependencies: {', '.join(missing)}"
            )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(step_id: str) -> None:
        if step_id in visiting:
            raise WorkflowError(f"workflow contains a cycle at step '{step_id}'")
        if step_id in visited:
            return
        visiting.add(step_id)
        for dependency in steps_by_id[step_id].depends_on:
            visit(dependency)
        visiting.remove(step_id)
        visited.add(step_id)

    for step in definition.steps:
        visit(step.id)

    return CompiledWorkflow(definition=definition, agents=manifests)
