from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from studio.workflow import ContentWorkflowRequest, MockProvider, run_content_workflow
from engine import runrecord


class WorkflowTests(unittest.TestCase):
    def test_content_workflow_creates_reviewable_run_record(self) -> None:
        with TemporaryDirectory() as temporary:
            runs_dir = Path(temporary) / "runs"
            provider = MockProvider()
            request = ContentWorkflowRequest(
                goal="Write a post about today's build",
                material="We replaced the brittle router with explicit manifests.",
                material_name="business/inbox/build-notes.md",
            )

            result = run_content_workflow(runs_dir, request, provider)
            loaded = runrecord.read(runs_dir, result.record.run_id)

        self.assertEqual(result.path, runrecord.run_path(runs_dir, result.record.run_id))
        self.assertEqual(loaded.provider, "mock")
        self.assertEqual(loaded.agent, "orchestrator")
        self.assertEqual(loaded.status, "awaiting_approval")
        self.assertEqual(len(loaded.drafts), 2)
        self.assertEqual(
            [draft.draft_id for draft in loaded.drafts],
            [f"{loaded.run_id}#1", f"{loaded.run_id}#2"],
        )
        self.assertIn("Direct draft", loaded.drafts[0].text)
        self.assertIn("Reflective draft", loaded.drafts[1].text)
        self.assertIn("ready for human approval", result.review_text)
        self.assertEqual(loaded.review, result.review_text)
        self.assertTrue(result.agent_plan)
        self.assertEqual(loaded.agent_plan, result.agent_plan)
        self.assertEqual(len(provider.calls), 4)
        self.assertEqual(loaded.inputs[0].path, "business/inbox/build-notes.md")
        self.assertEqual(loaded.inputs[0].content, request.material)
        self.assertIn("Material:", provider.calls[-1]["user_prompt"])
        self.assertIsNotNone(loaded.usage)

    def test_empty_workflow_inputs_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "goal cannot be empty"):
            run_content_workflow(
                Path("data/runs"),
                ContentWorkflowRequest(goal="", material="some material"),
            )

        with self.assertRaisesRegex(ValueError, "material cannot be empty"):
            run_content_workflow(
                Path("data/runs"),
                ContentWorkflowRequest(goal="Do work", material=""),
            )


if __name__ == "__main__":
    unittest.main()
