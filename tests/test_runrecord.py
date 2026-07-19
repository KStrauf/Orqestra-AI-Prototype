import json
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from engine import runrecord
from engine.errors import DecisionError, PublicationError


class RunRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.runs_dir = Path(self.temp_dir.name) / "runs"
        self.record = runrecord.RunRecord(
            run_id="20260718-1200-ab12",
            agent="content",
            task="Write a post",
            started_at="2026-07-18T12:00:00Z",
            provider="test",
            model="test-model",
            temperature=0.7,
            system_prompt="System",
            user_prompt="User",
            inputs=[runrecord.Input("inbox", "notes.md", "abc", 5)],
            usage=runrecord.Usage(10, 20, 0.01, True),
            drafts=[runrecord.Draft("20260718-1200-ab12#1", "plain", "Hello", 5)],
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_utc_now_returns_parseable_utc_timestamp(self) -> None:
        timestamp = runrecord.utc_now()

        self.assertTrue(timestamp.endswith("Z"))
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        self.assertIsNotNone(parsed.tzinfo)
        self.assertEqual(parsed.utcoffset().total_seconds(), 0)

    def test_write_and_read_round_trip_nested_values(self) -> None:
        path = runrecord.write(self.runs_dir, self.record)

        self.assertEqual(
            path,
            self.runs_dir / "2026-07-18" / "20260718-1200-ab12.json",
        )
        loaded = runrecord.read(self.runs_dir, self.record.run_id)
        self.assertEqual(loaded, self.record)
        self.assertIsInstance(loaded.inputs[0], runrecord.Input)
        self.assertIsInstance(loaded.usage, runrecord.Usage)
        self.assertIsInstance(loaded.drafts[0], runrecord.Draft)

    def test_append_decision_and_publication_preserve_record(self) -> None:
        runrecord.write(self.runs_dir, self.record)
        decision = runrecord.Decision(
            draft_id="20260718-1200-ab12#1",
            decision="approve",
            at="2026-07-18T12:01:00Z",
        )
        publication = runrecord.Published(
            draft_id="20260718-1200-ab12#1",
            at="2026-07-18T12:02:00Z",
            platform="example",
            url="https://example.test/post/1",
        )

        runrecord.append_decision(self.runs_dir, self.record.run_id, decision)
        runrecord.append_published(self.runs_dir, self.record.run_id, publication)

        loaded = runrecord.read(self.runs_dir, self.record.run_id)
        self.assertEqual(loaded.drafts, self.record.drafts)
        self.assertEqual(loaded.decisions, [decision])
        self.assertEqual(loaded.published, [publication])
        self.assertEqual(loaded.status, "published")

    def test_publication_requires_approval(self) -> None:
        runrecord.write(self.runs_dir, self.record)
        publication = runrecord.Published(
            draft_id="20260718-1200-ab12#1",
            at="2026-07-18T12:02:00Z",
            platform="example",
            url="https://example.test/post/1",
        )

        with self.assertRaises(PublicationError):
            runrecord.append_published(self.runs_dir, self.record.run_id, publication)

    def test_rejected_draft_cannot_be_published(self) -> None:
        runrecord.write(self.runs_dir, self.record)
        runrecord.append_decision(
            self.runs_dir,
            self.record.run_id,
            runrecord.Decision(
                draft_id="20260718-1200-ab12#1",
                decision="reject",
                at="2026-07-18T12:01:00Z",
                reason_tag="unsupported_claim",
                reason="The source does not support this claim.",
            ),
        )

        with self.assertRaises(PublicationError):
            runrecord.append_published(
                self.runs_dir,
                self.record.run_id,
                runrecord.Published(
                    draft_id="20260718-1200-ab12#1",
                    at="2026-07-18T12:02:00Z",
                    platform="example",
                    url="https://example.test/post/1",
                ),
            )

    def test_decision_requires_existing_draft_and_required_fields(self) -> None:
        runrecord.write(self.runs_dir, self.record)

        with self.assertRaises(DecisionError):
            runrecord.append_decision(
                self.runs_dir,
                self.record.run_id,
                runrecord.Decision("missing#1", "approve", "2026-07-18T12:01:00Z"),
            )
        with self.assertRaises(DecisionError):
            runrecord.append_decision(
                self.runs_dir,
                self.record.run_id,
                runrecord.Decision(
                    "20260718-1200-ab12#1", "edit", "2026-07-18T12:01:00Z"
                ),
            )
        with self.assertRaises(DecisionError):
            runrecord.append_decision(
                self.runs_dir,
                self.record.run_id,
                runrecord.Decision(
                    "20260718-1200-ab12#1", "reject", "2026-07-18T12:01:00Z"
                ),
            )

    def test_write_leaves_no_temporary_file(self) -> None:
        path = runrecord.write(self.runs_dir, self.record)

        self.assertTrue(path.is_file())
        self.assertEqual(list(path.parent.glob("*.tmp")), [])
        self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["run_id"], self.record.run_id)

    def test_failed_replace_cleans_up_temporary_file(self) -> None:
        with patch.object(runrecord.os, "replace", side_effect=OSError("replace failed")):
            with self.assertRaises(OSError):
                runrecord.write(self.runs_dir, self.record)

        day_dir = self.runs_dir / "2026-07-18"
        self.assertEqual(list(day_dir.glob("*.tmp")), [])
        self.assertFalse((day_dir / f"{self.record.run_id}.json").exists())

    def test_read_supports_records_with_omitted_optional_fields(self) -> None:
        path = runrecord.run_path(self.runs_dir, self.record.run_id)
        path.parent.mkdir(parents=True)
        legacy_record = {
            "schema_version": 1,
            "run_id": self.record.run_id,
            "agent": "content",
            "task": "Write a post",
            "started_at": "2026-07-18T12:00:00Z",
            "provider": "test",
            "model": "test-model",
            "temperature": 0.7,
            "system_prompt": "System",
            "user_prompt": "User",
        }
        path.write_text(json.dumps(legacy_record), encoding="utf-8")

        loaded = runrecord.read(self.runs_dir, self.record.run_id)

        self.assertEqual(loaded.run_id, self.record.run_id)
        self.assertEqual(loaded.inputs, [])
        self.assertIsNone(loaded.usage)
        self.assertEqual(loaded.decisions, [])
        self.assertEqual(loaded.published, [])
        self.assertEqual(loaded.status, "completed")

    def test_read_normalizes_legacy_status_and_recovers_explicit_material(self) -> None:
        path = runrecord.run_path(self.runs_dir, self.record.run_id)
        path.parent.mkdir(parents=True)
        legacy_record = {
            "schema_version": 1,
            "run_id": self.record.run_id,
            "agent": "orchestrator",
            "task": "Write a post",
            "started_at": "2026-07-18T12:00:00Z",
            "finished_at": "2026-07-18T12:01:00Z",
            "provider": "mock",
            "model": "local",
            "temperature": 0.7,
            "system_prompt": "System",
            "user_prompt": "Goal: Write a post\nMaterial: Recovered source material.",
            "inputs": [{"source": "workflow", "path": "notes.md", "sha256": "abc", "chars": 26}],
            "drafts": [],
            "status": None,
        }
        path.write_text(json.dumps(legacy_record), encoding="utf-8")

        loaded = runrecord.read(self.runs_dir, self.record.run_id)

        self.assertEqual(loaded.status, "completed")
        self.assertEqual(loaded.inputs[0].content, "Recovered source material.")

    def test_list_run_ids_returns_newest_first(self) -> None:
        runrecord.write(self.runs_dir, self.record)
        newer = self.record.run_id.replace("1200", "1201")
        runrecord.write(self.runs_dir, runrecord.RunRecord(
            run_id=newer,
            agent="content",
            task="New post",
            started_at="2026-07-18T12:01:00Z",
            provider="test",
            model="test-model",
            temperature=0.7,
            system_prompt="System",
            user_prompt="User",
        ))

        self.assertEqual(runrecord.list_run_ids(self.runs_dir), [newer, self.record.run_id])

    def test_list_records_reads_newest_records_from_durable_storage(self) -> None:
        runrecord.write(self.runs_dir, self.record)
        newer = self.record.run_id.replace("1200", "1201")
        runrecord.write(self.runs_dir, runrecord.RunRecord(
            run_id=newer,
            agent="test",
            task="New post",
            started_at="2026-07-18T12:01:00Z",
            provider="test",
            model="test-model",
            temperature=0.7,
            system_prompt="System",
            user_prompt="User",
        ))

        records = runrecord.list_records(self.runs_dir, limit=1)

        self.assertEqual([record.run_id for record in records], [newer])


if __name__ == "__main__":
    unittest.main()
