from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from engine.cli import cmd_approve, cmd_pending, cmd_publish, cmd_studio_demo
from engine import runrecord


class StudioCliTests(unittest.TestCase):
    def test_studio_demo_prints_review_and_persists_run(self) -> None:
        with TemporaryDirectory() as temporary:
            class Settings:
                runs_dir = Path(temporary) / "runs"

            output = StringIO()
            with redirect_stdout(output):
                exit_code = cmd_studio_demo(
                    Settings(),
                    "Write a launch post",
                    "The new workflow is now testable.",
                    "build-notes.md",
                )

            run_ids = runrecord.list_run_ids(Settings.runs_dir)

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(run_ids), 1)
        rendered = output.getvalue()
        self.assertIn("architect -> specialist -> reviewer", rendered)
        self.assertIn("AGENT PLAN", rendered)
        self.assertIn("REVIEW", rendered)
        self.assertIn("human approval required", rendered)

    def test_pending_edit_and_publish_flow(self) -> None:
        with TemporaryDirectory() as temporary:
            class Settings:
                runs_dir = Path(temporary) / "runs"

            cmd_studio_demo(
                Settings(),
                "Write a launch post",
                "The new workflow is now testable.",
                "build-notes.md",
            )
            run_id = runrecord.list_run_ids(Settings.runs_dir)[0]
            record = runrecord.read(Settings.runs_dir, run_id)
            draft_id = record.drafts[0].draft_id

            pending_output = StringIO()
            with redirect_stdout(pending_output):
                self.assertEqual(cmd_pending(Settings()), 0)
            self.assertIn(draft_id, pending_output.getvalue())

            edited_text = record.drafts[0].text + " Edited."
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(
                    cmd_approve(
                        Settings(),
                        run_id,
                        draft_id,
                        "edit",
                        reason_tag="clarity",
                        reason="Tightened the closing sentence.",
                        edited_text=edited_text,
                    ),
                    0,
                )
                self.assertEqual(
                    cmd_publish(
                        Settings(), draft_id, "https://example.test/post/1", "example"
                    ),
                    0,
                )

            loaded = runrecord.read(Settings.runs_dir, run_id)
            self.assertEqual(loaded.status, "published")
            self.assertEqual(loaded.decisions[0].decision, "edit")
            self.assertEqual(loaded.decisions[0].edited_text, edited_text)
            self.assertIn("@@", loaded.decisions[0].diff or "")
            self.assertEqual(loaded.published[0].draft_id, draft_id)
            self.assertIn("published to example", output.getvalue())


if __name__ == "__main__":
    unittest.main()
