"""Internal content skill registry.

The registry adapts external content skill ideas into inspectable runtime
capabilities. Skills are not extra agents: the existing Architect, Specialist,
Reviewer, and Human stages remain the orchestration boundary.
"""

from dataclasses import dataclass, asdict
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class SkillManifest:
    id: str
    name: str
    description: str
    owner_stage: str
    input_types: tuple[str, ...]
    output_type: str
    version: str = "1.0.0"
    requires_human_gate: bool = False


def load_content_skills(directory: Path | None = None) -> dict[str, SkillManifest]:
    """Load the adapted skill contracts shipped with Studio."""
    skill_dir = directory or Path(__file__).parent / "skills"
    manifests: dict[str, SkillManifest] = {}
    for path in sorted(skill_dir.glob("*.yaml")):
        raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError(f"skill manifest {path} must contain an object")
        required = ("id", "name", "description", "owner_stage", "input_types", "output_type")
        missing = [field for field in required if not raw.get(field)]
        if missing:
            raise ValueError(f"skill manifest {path} is missing: {', '.join(missing)}")
        skill = SkillManifest(
            id=str(raw["id"]),
            name=str(raw["name"]),
            description=str(raw["description"]),
            owner_stage=str(raw["owner_stage"]),
            input_types=tuple(str(item) for item in raw["input_types"]),
            output_type=str(raw["output_type"]),
            version=str(raw.get("version", "1.0.0")),
            requires_human_gate=bool(raw.get("requires_human_gate", False)),
        )
        if skill.id in manifests:
            raise ValueError(f"duplicate content skill ID: {skill.id}")
        manifests[skill.id] = skill
    return manifests


def skill_versions(skills: dict[str, SkillManifest]) -> dict[str, str]:
    """Return stable skill versions for run traceability."""
    return {skill_id: skill.version for skill_id, skill in sorted(skills.items())}


def skill_fingerprint(skills: dict[str, SkillManifest]) -> str:
    payload = json.dumps(
        {skill_id: asdict(skill) for skill_id, skill in sorted(skills.items())},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
