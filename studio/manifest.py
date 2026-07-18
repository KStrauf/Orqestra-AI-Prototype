"""Declarative runtime-agent manifests for Orqestra Studio."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from engine.errors import ManifestError


REQUIRED_FIELDS = {
    "id",
    "name",
    "description",
    "purpose",
    "instructions",
    "input_types",
    "output_type",
}


@dataclass(frozen=True)
class AgentManifest:
    """The user-editable configuration for one Studio runtime agent."""

    id: str
    name: str
    description: str
    purpose: str
    instructions: str
    input_types: tuple[str, ...]
    output_type: str
    tools: tuple[str, ...] = ()
    handoffs: tuple[str, ...] = ()
    requires_approval: bool = True
    model: str = "gpt-5.6"
    temperature: float = 0.4


def _require_text(data: Mapping[str, Any], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"agent manifest field '{field}' must be a non-empty string")
    return value


def _string_tuple(data: Mapping[str, Any], field: str) -> tuple[str, ...]:
    value = data.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ManifestError(f"agent manifest field '{field}' must be a list of non-empty strings")
    return tuple(value)


def _load_data(path: Path) -> Mapping[str, Any]:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ManifestError(f"cannot read agent manifest {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ManifestError(f"invalid YAML in agent manifest {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ManifestError(f"agent manifest {path} must contain a YAML object")
    missing = sorted(REQUIRED_FIELDS - raw.keys())
    if missing:
        raise ManifestError(f"agent manifest {path} is missing: {', '.join(missing)}")
    return raw


def load_manifest(path: Path) -> AgentManifest:
    """Load and validate one YAML agent manifest."""
    data = _load_data(path)
    agent_id = _require_text(data, "id")
    tools = _string_tuple(data, "tools") if "tools" in data else ()
    handoffs = _string_tuple(data, "handoffs") if "handoffs" in data else ()

    requires_approval = data.get("requires_approval", True)
    if not isinstance(requires_approval, bool):
        raise ManifestError("agent manifest field 'requires_approval' must be a boolean")

    model = data.get("model", "gpt-5.6")
    if not isinstance(model, str) or not model.strip():
        raise ManifestError("agent manifest field 'model' must be a non-empty string")

    temperature = data.get("temperature", 0.4)
    if isinstance(temperature, bool) or not isinstance(temperature, (int, float)):
        raise ManifestError("agent manifest field 'temperature' must be a number")
    if not 0 <= float(temperature) <= 2:
        raise ManifestError("agent manifest field 'temperature' must be between 0 and 2")

    return AgentManifest(
        id=agent_id,
        name=_require_text(data, "name"),
        description=_require_text(data, "description"),
        purpose=_require_text(data, "purpose"),
        instructions=_require_text(data, "instructions"),
        input_types=_string_tuple(data, "input_types"),
        output_type=_require_text(data, "output_type"),
        tools=tools,
        handoffs=handoffs,
        requires_approval=requires_approval,
        model=model,
        temperature=float(temperature),
    )


def load_manifests(directory: Path) -> dict[str, AgentManifest]:
    """Load all YAML manifests in a directory, keyed by stable agent ID."""
    if not directory.exists():
        raise ManifestError(f"agent manifest directory does not exist: {directory}")
    if not directory.is_dir():
        raise ManifestError(f"agent manifest path is not a directory: {directory}")

    manifests: dict[str, AgentManifest] = {}
    for path in sorted(directory.glob("*.yaml")):
        manifest = load_manifest(path)
        if manifest.id in manifests:
            raise ManifestError(f"duplicate agent ID '{manifest.id}' in {directory}")
        manifests[manifest.id] = manifest

    known_ids = set(manifests)
    for manifest in manifests.values():
        missing_handoffs = sorted(set(manifest.handoffs) - known_ids)
        if missing_handoffs:
            missing = ", ".join(missing_handoffs)
            raise ManifestError(
                f"agent '{manifest.id}' references unknown handoffs: {missing}"
            )
    return manifests


def load_builtin_agents() -> dict[str, AgentManifest]:
    """Load the four agents shipped with the Studio prototype."""
    return load_manifests(Path(__file__).parent / "agents")
