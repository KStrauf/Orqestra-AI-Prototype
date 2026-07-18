import unittest

from engine.errors import WorkflowError
from studio.manifest import load_builtin_agents
from studio.plan import (
    WorkflowDefinition,
    WorkflowStep,
    compile_workflow,
    content_workflow_definition,
)


class WorkflowPlanTests(unittest.TestCase):
    def test_content_workflow_compiles_to_manifest_resolved_steps(self) -> None:
        compiled = compile_workflow(
            content_workflow_definition(),
            load_builtin_agents(),
        )

        self.assertEqual(
            [step.id for step in compiled.definition.steps],
            ["architect", "specialist", "reviewer"],
        )
        self.assertTrue(compiled.definition.steps[1].fan_out)
        self.assertTrue(compiled.definition.steps[2].requires_approval)
        self.assertEqual(compiled.agent_for(compiled.definition.steps[1]).id, "specialist")

    def test_unknown_agent_is_rejected_before_execution(self) -> None:
        definition = WorkflowDefinition(
            id="invalid",
            version=1,
            steps=(
                WorkflowStep(
                    id="missing",
                    agent_id="does-not-exist",
                    output_type="draft",
                ),
            ),
        )

        with self.assertRaisesRegex(WorkflowError, "does-not-exist"):
            compile_workflow(definition, load_builtin_agents())

    def test_cycle_is_rejected_before_execution(self) -> None:
        definition = WorkflowDefinition(
            id="cyclic",
            version=1,
            steps=(
                WorkflowStep(
                    id="first",
                    agent_id="architect",
                    output_type="agent_plan",
                    depends_on=("second",),
                ),
                WorkflowStep(
                    id="second",
                    agent_id="architect",
                    output_type="agent_plan",
                    depends_on=("first",),
                ),
            ),
        )

        with self.assertRaisesRegex(WorkflowError, "cycle"):
            compile_workflow(definition, load_builtin_agents())


if __name__ == "__main__":
    unittest.main()
