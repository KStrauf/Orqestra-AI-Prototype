from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import httpx

import studio.api as studio_api


class StudioApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.original_settings = studio_api.settings
        studio_api.settings = replace(
            self.original_settings,
            data_dir=Path(self.temporary.name) / "data",
            provider="mock",
        )
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=studio_api.app),
            base_url="http://testserver",
        )

    async def asyncTearDown(self) -> None:
        await self.client.aclose()
        studio_api.settings = self.original_settings
        self.temporary.cleanup()

    async def test_create_and_get_run_keep_existing_contract_and_add_typed_fields(self) -> None:
        response = await self.client.post(
            "/api/studio/runs",
            json={
                "goal": "Write a launch post",
                "material": "The Studio workflow is now testable.",
                "platform": "LinkedIn",
                "audience": "early-stage builders",
                "outcome": "Build trust",
                "tone": "Warm and personal",
                "brief": "Explain why visible review matters.",
            },
        )

        self.assertEqual(response.status_code, 200)
        created = response.json()
        self.assertEqual(created["status"], "awaiting_approval")
        self.assertEqual(created["provider"], "mock")
        self.assertEqual(len(created["drafts"]), 2)
        self.assertEqual(created["content_platform"], "LinkedIn")
        self.assertEqual(created["audience"], "early-stage builders")
        self.assertEqual(created["content_brief"]["outcome"], "Build trust")
        self.assertEqual([event["stage"] for event in created["events"]], ["architect", "specialist", "reviewer", "human"])
        self.assertIn("schema_version", created)

        loaded_response = await self.client.get(f"/api/studio/runs/{created['run_id']}")

        self.assertEqual(loaded_response.status_code, 200)
        self.assertEqual(loaded_response.json()["run_id"], created["run_id"])
        self.assertEqual(loaded_response.json()["inputs"][0]["chars"], len("The Studio workflow is now testable."))
        self.assertEqual(loaded_response.json()["inputs"][0]["content"], "The Studio workflow is now testable.")
        self.assertEqual(len(created["hook_candidates"]), 2)
        self.assertIn("platform_fit", created["quality_report"]["scores"])
        self.assertIn("post_writer", created["skill_versions"])

    async def test_brand_profile_is_durable_and_used_by_later_runs(self) -> None:
        saved = await self.client.put(
            "/api/studio/brand-profile",
            json={
                "name": "Creator",
                "audience": "builders",
                "voice_traits": ["warm", "direct"],
                "primary_cta": "Share your experience",
                "social_links": {"linkedin": "https://linkedin.example/creator"},
            },
        )

        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json()["audience"], "builders")

        created = (await self.client.post(
            "/api/studio/runs",
            json={"goal": "Explain a useful idea", "material": "A source-backed idea."},
        )).json()

        self.assertEqual(created["brand_profile"]["name"], "Creator")
        self.assertEqual(created["brand_profile"]["voice_traits"], ["warm", "direct"])
        fetched = await self.client.get("/api/studio/brand-profile")
        self.assertEqual(fetched.json()["social_links"]["linkedin"], "https://linkedin.example/creator")

    async def test_run_list_returns_newest_durable_summaries(self) -> None:
        for goal in ("First post", "Second post"):
            response = await self.client.post(
                "/api/studio/runs",
                json={"goal": goal, "material": "Source material."},
            )
            self.assertEqual(response.status_code, 200)

        response = await self.client.get("/api/studio/runs?limit=1")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["count"], 1)
        self.assertEqual(body["limit"], 1)
        self.assertEqual(body["runs"][0]["draft_count"], 2)
        self.assertEqual(body["runs"][0]["status"], "awaiting_approval")

    async def test_decision_response_is_typed_and_persisted(self) -> None:
        created = (await self.client.post(
            "/api/studio/runs",
            json={"goal": "Write a post", "material": "A useful fact."},
        )).json()
        draft_id = created["drafts"][0]["draft_id"]

        response = await self.client.post(
            f"/api/studio/runs/{created['run_id']}/decisions",
            json={"draft_id": draft_id, "decision": "approve"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["decision"], "approve")
        loaded = (await self.client.get(f"/api/studio/runs/{created['run_id']}")).json()
        self.assertEqual(loaded["decisions"][0]["draft_id"], draft_id)
        self.assertEqual(loaded["status"], "decided")

    async def test_errors_include_normalized_envelope_and_legacy_detail(self) -> None:
        missing = await self.client.get("/api/studio/runs/not-a-real-run")
        invalid = await self.client.post("/api/studio/runs", json={"material": "missing goal"})

        self.assertEqual(missing.status_code, 404)
        self.assertEqual(missing.json()["detail"], "run not found")
        self.assertEqual(missing.json()["error"]["code"], "not_found")
        self.assertEqual(invalid.status_code, 422)
        self.assertEqual(invalid.json()["error"]["code"], "validation_error")
        self.assertIsInstance(invalid.json()["detail"], list)

    async def test_reject_without_reason_keeps_legacy_status_and_normalized_error(self) -> None:
        created = (await self.client.post(
            "/api/studio/runs",
            json={"goal": "Write a post", "material": "A useful fact."},
        )).json()
        draft_id = created["drafts"][0]["draft_id"]

        response = await self.client.post(
            f"/api/studio/runs/{created['run_id']}/decisions",
            json={"draft_id": draft_id, "decision": "reject"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("reject decision requires a reason", response.json()["detail"])
        self.assertEqual(response.json()["error"]["code"], "bad_request")


if __name__ == "__main__":
    unittest.main()
