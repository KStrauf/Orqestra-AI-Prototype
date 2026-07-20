from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from engine.content import (
    BrandProfile,
    build_hook_candidates,
    grade_drafts,
    platform_profile,
    read_brand_profile,
    write_brand_profile,
)
from engine import runrecord
from studio.skills import load_content_skills, skill_fingerprint, skill_versions


class ContentCapabilityTests(unittest.TestCase):
    def test_skill_registry_loads_versioned_content_capabilities(self) -> None:
        skills = load_content_skills()

        self.assertEqual(
            set(skills),
            {"brand_context", "idea_coach", "hook_strategist", "post_writer", "post_grader", "repurpose", "publish_handoff"},
        )
        self.assertEqual(skills["post_writer"].owner_stage, "specialist")
        self.assertTrue(skill_fingerprint(skills))
        self.assertEqual(skill_versions(skills)["post_grader"], "1.0.0")

    def test_hook_candidates_use_supplied_context_without_claiming_virality(self) -> None:
        profile = BrandProfile(audience="early builders", strong_opinions=["Useful content starts with a real problem"])
        hooks = build_hook_candidates(
            "Explain an AI sparring partner",
            "LinkedIn",
            ("direct", "reflective", "educational"),
            audience="early builders",
            brand_profile=profile,
        )

        self.assertEqual(len(hooks), 3)
        self.assertIn("Useful content starts with a real problem", hooks[2].text)
        self.assertNotIn("viral", " ".join(hook.text.lower() for hook in hooks))

    def test_grader_records_platform_risk_and_idea_mode_risk(self) -> None:
        drafts = [runrecord.Draft("draft#1", "direct", "x" * 320, 320)]

        report = grade_drafts(drafts, "X", material_supplied=False)

        self.assertEqual(platform_profile("X").max_chars, 280)
        self.assertTrue(drafts[0].constraint_violations)
        self.assertLess(report.scores["platform_fit"], 8)
        self.assertTrue(any("idea" in issue for issue in report.issues))

    def test_brand_profile_persists_separately_from_run_records(self) -> None:
        with TemporaryDirectory() as temporary:
            data_dir = Path(temporary)
            profile = BrandProfile(
                name="Creator",
                audience="builders",
                voice_traits=["warm", "direct"],
                social_links={"linkedin": "https://linkedin.example/creator"},
            )

            path = write_brand_profile(data_dir, profile)
            loaded = read_brand_profile(data_dir)

            self.assertTrue(path.exists())
            self.assertEqual(loaded, profile)



if __name__ == "__main__":
    unittest.main()
