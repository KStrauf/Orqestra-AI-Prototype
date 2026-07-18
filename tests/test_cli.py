from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from engine.cli import cmd_studio_demo
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


if __name__ == "__main__":
    unittest.main()
