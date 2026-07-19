"""The durable JSON record of one agent run.

The JSON file is the source of truth. Any future SQLite index is derived from
these files and must be rebuildable, so this module deliberately keeps the
storage path simple and explicit.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import secrets
import tempfile
from typing import Any

from engine.errors import DecisionError, PublicationError


SCHEMA_VERSION = 2


# --- small helpers ---------------------------------------------------------
def utc_now() -> str:
    """Return the current time as a UTC ISO-8601 timestamp."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def new_run_id() -> str:
    """Return a sortable run ID with a short random collision guard."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    return f"{stamp}-{secrets.token_hex(2)}"


def sha256_text(text: str) -> str:
    """Return the SHA-256 fingerprint of a text value."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# --- the pieces of a run ---------------------------------------------------
@dataclass
class Input:
    """One piece of raw material fed to the model."""

    source: str
    path: str
    sha256: str
    chars: int


@dataclass
class Usage:
    """What the model call cost."""

    input_tokens: int
    output_tokens: int
    cost_usd: float
    cost_is_estimate: bool


@dataclass
class Draft:
    """One candidate piece of content."""

    draft_id: str
    variant: str
    text: str
    chars: int
    constraint_violations: list[str] = field(default_factory=list)


@dataclass
class Decision:
    """A human verdict on one draft."""

    draft_id: str
    decision: str
    at: str
    reason_tag: str | None = None
    reason: str | None = None
    edited_text: str | None = None
    diff: str | None = None


@dataclass
class Published:
    """Proof that a draft went live."""

    draft_id: str
    at: str
    platform: str
    url: str


@dataclass
class RunRecord:
    """One execution of one agent, from prompt to publication."""

    run_id: str
    agent: str
    task: str
    started_at: str

    provider: str
    model: str
    temperature: float

    system_prompt: str
    user_prompt: str

    finished_at: str | None = None
    duration_ms: int | None = None

    inputs: list[Input] = field(default_factory=list)
    template_name: str | None = None
    template_sha256: str | None = None
    voice_sha256: str | None = None
    voice_feedback_entries_used: int = 0
    voice_exemplars_used: int = 0

    usage: Usage | None = None
    drafts: list[Draft] = field(default_factory=list)
    error: str | None = None
    status: str = "completed"
    agent_plan: str | None = None
    review: str | None = None

    # These fields are appended after the run completes.
    decisions: list[Decision] = field(default_factory=list)
    published: list[Published] = field(default_factory=list)

    schema_version: int = SCHEMA_VERSION


# --- reading and writing ---------------------------------------------------
def run_path(runs_dir: Path, run_id: str) -> Path:
    """Return the day-foldered path for a run ID."""
    day = f"{run_id[0:4]}-{run_id[4:6]}-{run_id[6:8]}"
    return runs_dir / day / f"{run_id}.json"


def write(runs_dir: Path, record: RunRecord) -> Path:
    """Write a run record atomically and return its final path.

    The temporary file is created beside the destination, which keeps
    ``os.replace`` atomic on the supported local filesystems.
    """
    path = run_path(runs_dir, record.run_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = json.dumps(asdict(record), indent=2, ensure_ascii=False) + "\n"
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            temporary_file.write(payload)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return path


def _load_nested(raw: dict[str, Any]) -> RunRecord:
    """Rebuild typed nested values from a decoded JSON object."""
    raw["inputs"] = [Input(**item) for item in raw.get("inputs", [])]
    raw["drafts"] = [Draft(**item) for item in raw.get("drafts", [])]
    raw["decisions"] = [Decision(**item) for item in raw.get("decisions", [])]
    raw["published"] = [Published(**item) for item in raw.get("published", [])]
    if raw.get("usage") is not None:
        raw["usage"] = Usage(**raw["usage"])
    return RunRecord(**raw)


def read(runs_dir: Path, run_id: str) -> RunRecord:
    """Load a run record from disk, rebuilding nested dataclasses."""
    path = run_path(runs_dir, run_id)
    if not path.exists():
        raise FileNotFoundError(f"no run record at {path}")

    raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return _load_nested(raw)


def append_decision(runs_dir: Path, run_id: str, decision: Decision) -> None:
    """Append a human decision to an existing run record."""
    record = read(runs_dir, run_id)
    valid_decisions = {"approve", "edit", "reject"}
    if decision.decision not in valid_decisions:
        raise DecisionError(
            f"decision must be one of: {', '.join(sorted(valid_decisions))}"
        )
    if not any(draft.draft_id == decision.draft_id for draft in record.drafts):
        raise DecisionError(f"draft not found in run: {decision.draft_id}")
    if any(item.draft_id == decision.draft_id for item in record.decisions):
        raise DecisionError(f"draft already has a decision: {decision.draft_id}")
    if decision.decision == "edit" and not decision.edited_text:
        raise DecisionError("an edit decision requires edited_text")
    if decision.decision == "reject" and not decision.reason:
        raise DecisionError("a reject decision requires a reason")
    record.decisions.append(decision)
    record.status = "decided"
    write(runs_dir, record)


def append_published(runs_dir: Path, run_id: str, published: Published) -> None:
    """Append publication evidence to an existing run record."""
    record = read(runs_dir, run_id)
    if not any(draft.draft_id == published.draft_id for draft in record.drafts):
        raise PublicationError(f"draft not found in run: {published.draft_id}")
    if any(item.draft_id == published.draft_id for item in record.published):
        raise PublicationError(f"draft is already published: {published.draft_id}")
    decision = next(
        (item for item in record.decisions if item.draft_id == published.draft_id),
        None,
    )
    if decision is None:
        raise PublicationError("draft requires human approval before publication")
    if decision.decision not in {"approve", "edit"}:
        raise PublicationError(
            f"draft cannot be published after a {decision.decision} decision"
        )
    record.published.append(published)
    record.status = "published"
    write(runs_dir, record)


def list_run_ids(runs_dir: Path) -> list[str]:
    """Return every stored run ID, newest first."""
    if not runs_dir.exists():
        return []
    return sorted((path.stem for path in runs_dir.glob("*/*.json")), reverse=True)


def list_records(runs_dir: Path, limit: int | None = None) -> list[RunRecord]:
    """Return durable run records newest first.

    The API history view deliberately reads these JSON records through this
    module rather than creating a second persistence path or index.
    """
    run_ids = list_run_ids(runs_dir)
    if limit is not None:
        if limit < 1:
            raise ValueError("limit must be positive")
        run_ids = run_ids[:limit]
    return [read(runs_dir, run_id) for run_id in run_ids]
