from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from dataclasses import replace

from engine.errors import ManifestError
from studio.manifest import (
    AgentManifest,
    load_builtin_agents,
    load_manifest,
    load_manifests,
    manifest_fingerprint,
)


class ManifestTests(unittest.TestCase):
    def test_builtin_agents_load_with_expected_workflow(self) -> None:
        agents = load_builtin_agents()

        self.assertEqual(set(agents), {"architect", "orchestrator", "specialist", "reviewer"})
        self.assertIsInstance(agents["architect"], AgentManifest)
        self.assertEqual(agents["architect"].handoffs, ("orchestrator",))
        self.assertEqual(agents["orchestrator"].handoffs, ("specialist", "reviewer"))
        self.assertTrue(agents["reviewer"].requires_approval)

    def test_content_agents_include_creation_style_guidance(self) -> None:
        agents = load_builtin_agents()

        self.assertIn("Content creation skill", agents["specialist"].instructions)
        self.assertIn("Avoid em dashes", agents["specialist"].instructions)
        self.assertIn("platform", agents["specialist"].instructions)
        self.assertIn("Enforce the content-creation style rules", agents["reviewer"].instructions)
        self.assertIn("unsupported claims", agents["reviewer"].instructions)

    def test_manifest_defaults_are_applied(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "minimal.yaml"
            path.write_text(
                """id: minimal
name: Minimal
description: A minimal test agent.
purpose: Test loading.
instructions: Do the test.
input_types:
  - text
output_type: result
""",
                encoding="utf-8",
            )

            manifest = load_manifest(path)

        self.assertEqual(manifest.tools, ())
        self.assertEqual(manifest.handoffs, ())
        self.assertTrue(manifest.requires_approval)
        self.assertEqual(manifest.model, "gpt-5.6")
        self.assertEqual(manifest.temperature, 0.4)

    def test_missing_required_field_is_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "invalid.yaml"
            path.write_text(
                """id: invalid
name: Invalid
description: Missing purpose and instructions.
input_types: []
output_type: result
""",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ManifestError, "instructions, purpose"):
                load_manifest(path)

    def test_unknown_handoff_is_rejected_for_a_directory(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "invalid.yaml"
            path.write_text(
                """id: invalid
name: Invalid
description: An invalid handoff test agent.
purpose: Test handoff validation.
instructions: Do the test.
input_types:
  - text
output_type: result
handoffs:
  - missing-agent
""",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ManifestError, "missing-agent"):
                load_manifests(Path(temporary))

    def test_manifest_fingerprint_changes_when_instructions_change(self) -> None:
        agents = load_builtin_agents()
        changed = dict(agents)
        changed["specialist"] = replace(
            changed["specialist"],
            instructions=changed["specialist"].instructions + " Prefer concise output.",
        )

        self.assertNotEqual(manifest_fingerprint(agents), manifest_fingerprint(changed))


if __name__ == "__main__":
    unittest.main()
