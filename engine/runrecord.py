"""The run record: what happened, what it cost, and what you decided about it.

This is the most important file in the project.

Storage rule: the JSON FILE is the truth. Later we add a SQLite index so
`orq pending` doesn't have to open sixty files - but that index is DERIVED and
rebuildable. If the two ever disagree, the file wins. We never write the same
fact to two places and hope they stay in sync; that bug is called dual-write
drift and it is miserable to debug.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import json
import os
import secrets

SCHEMA_VERSION = 1


# --- small helpers ---------------------------------------------------------

def utc_now() -> str:
    """Timestamps are ALWAYS UTC and ALWAYS ISO-8601.

    Local time in stored data is a bug waiting to happen: it changes meaning
    when you travel, and it silently breaks sorting across a DST boundary.
    """
    return
datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")

def new_run_id() -> str:
    """e.g. '20260713-1432-7f3a'
    Sortable, short enough to say out loud on camera, and the random suffix
    prevents a collision if you run twice in the same minute.
    """
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    return f"{stamp}-{secrets.token_hex(2)}"


def sha256_text(text: str) -> str:
    """Fingerprint of an input, a template, or the voice file.This proves WHICH version of your voice file produced a given draft. 
    Reject three drafts, and this hash changes - that is the system learning, made visible."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# --- the pieces of a run ---------------------------------------------------

@dataclass
class Input:
    """One piece of raw material that was fed to the model."""
    source: str        # "inbox" | "gitlog"
    path: str          # the file, or the command that produced it
    sha256: str
    chars: int


@dataclass
class Usage:
    """What the call actually cost."""
    input_tokens: int
    output_tokens: int
    cost_usd: float
    cost_is_estimate: bool   # True when the model is not in our pricing table


@dataclass
class Draft:
    """One candidate piece of content."""
    draft_id: str                  # "<run_id>#1"
    variant: str                   # the style instruction that produced it
    text: str
    chars: int
    constraint_violations: list[str] = field(default_factory=list)

    # Violations are RECORDED, not enforced. A 297-char post is shown to you with
    # a warning, not silently thrown away. You decide, not the machine.


@dataclass
class Decision:
    """Your verdict on one draft. This is the training signal."""
    draft_id: str
    decision: str                  # "approve" | "edit" | "reject"
    at: str
    reason_tag: str | None = None  # required on reject
    reason: str | None = None      # required on reject
    edited_text: str | None = None # set on edit
    diff: str | None = None        # set on edit


@dataclass
class Published:
    """Proof it went out into the world."""
    draft_id: str
    at: str
    platform: str
    url: str


@dataclass
class RunRecord:
    """One execution of one agent, start to finish."""
    run_id: str
    agent: str
    task: str
    started_at: str

    provider: str
    model: str
    temperature: float

    system_prompt: str   # VERBATIM. In full.
    user_prompt: str     # VERBATIM. In full.

    # These two make the file fat and they are non-negotiable. Without the exact
    # prompt you cannot debug a bad draft, cannot teach from the run, and cannot
    # show anyone what was actually sent. A run record without its prompt is a
    # receipt with no itemisation.

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

    # Appended AFTER the run. The run-time fields above are never rewritten.
    decisions: list[Decision] = field(default_factory=list)
    published: list[Published] = field(default_factory=list)

    schema_version: int = SCHEMA_VERSION


# --- reading and writing ---------------------------------------------------
def run_path(runs_dir: Path, run_id: str) -> Path:
    """data/runs/2026-07-13/20260713-1432-7f3a.json

    Foldered by day so the directory stays browsable after a few hundred runs.
    The date is already inside the run_id, so we just slice it out.
    """
    day = f"{run_id[0:4]}-{run_id[4:6]}-{run_id[6:8]}"
    return runs_dir / day / f"{run_id}.json"


def write(runs_dir: Path, record: RunRecord) -> Path:
    """Save a run record to disk, atomically.
    'Atomically' = write a temp file, then rename. Rename is atomic on POSIX, so
    a crash mid-write leaves you with either the OLD file or the NEW file - 
    never a half-written one. Truncating the real file first and then crashing would
    destroy the record. Two lines of habit that prevent data loss.
    """
    path = run_path(runs_dir, record.run_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(asdict(record), indent=2), encoding="utf-8")
    os.replace(tmp, path)   # atomic
    return path

  
def read(runs_dir: Path, run_id: str) -> RunRecord:
    """Load a run record from disk, rebuilding the nested dataclasses."""
    path = run_path(runs_dir, run_id)
    if not path.exists():
        raise FileNotFoundError(f"no run record at {path}")

    raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))

    # json.loads gives us plain dicts. Rebuild the typed objects so the rest of
    # the code gets `record.usage.cost_usd`, not record["usage"]["cost_usd"]`.
    # A typo in an attribute name fails loudly; a typo in a dict key fails silently.
    
    raw["inputs"] = [Input(**i) for i in raw.get("inputs", [])]
    raw["drafts"] = [Draft(**d) for d in raw.get("drafts", [])]
    raw["decisions"] = [Decision(**d) for d in raw.get("decisions", [])]
    raw["published"] = [Published(**p) for p in raw.get("published", [])]
    if raw.get("usage"):
        raw["usage"] = Usage(**raw["usage"])

    return RunRecord(**raw)


def append_decision(runs_dir: Path, run_id: str, decision: Decision) -> None:
    """Add your approve/edit/reject verdict to an existing run.Read, append, rewrite. 
    Not elegant, but a run record is a few KB and this is a single-user tool - the simplest correct thing beats a clever one."""
template_sha256: str | None = None
voice_sha256: str | None = None
voice_feedback_entries_used: int = 0
voice_exemplars_used: int = 0

usage: Usage | None = None
drafts: list[Draft] = field(default_factory=list)
error: str | None = None

# Appended AFTER the run. The run-time fields above are never rewritten.
decisions: list[Decision] = field(default_factory=list)
published: list[Published] = field(default_factory=list)

schema_version: int = SCHEMA_VERSION


# --- reading and writing ---------------------------------------------------

def run_path(runs_dir: Path, run_id: str) -> Path:
    """data/runs/2026-07-13/20260713-1432-7f3a.json
    Foldered by day so the directory stays browsable after a few hundred runs.
    The date is already inside the run_id, so we just slice it out."""
    day = f"{run_id[0:4]}-{run_id[4:6]}-{run_id[6:8]}"
    return runs_dir / day / f"{run_id}.json"


def write(runs_dir: Path, record: RunRecord) -> Path:
    """Save a run record to disk, atomically.
    'Atomically' = write a temp file, then rename. Rename is atomic on POSIX, so
    a crash mid-write leaves you with either the OLD file or the NEW file - never
    a half-written one. Truncating the real file first and then crashing would
    destroy the record. Two lines of habit that prevent data loss."""
    path = run_path(runs_dir, record.run_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(asdict(record), indent=2), encoding="utf-8")
    os.replace(tmp, path)   # atomic
    return path


def read(runs_dir: Path, run_id: str) -> RunRecord:
    """Load a run record from disk, rebuilding the nested dataclasses."""
    path = run_path(runs_dir, run_id)
    if not path.exists():
        raise FileNotFoundError(f"no run record at {path}")
    
    raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))

# json.loads gives us plain dicts. Rebuild the typed objects so the rest of
# the code gets `record.usage.cost_usd`, not`record["usage"]["cost_usd"]`.
# A typo in an attribute name fails loudly; a typo in a dict key fails. silently.

    raw["inputs"] = [Input(**i) for i in raw.get("inputs", [])]
    raw["drafts"] = [Draft(**d) for d in raw.get("drafts", [])]
    raw["decisions"] = [Decision(**d) for d in raw.get("decisions", [])]
    raw["published"] = [Published(**p) for p in raw.get("published", [])]
    if raw.get("usage"):
        raw["usage"] = Usage(**raw["usage"])

    return RunRecord(**raw)

def append_decision(runs_dir: Path, run_id: str, decision: Decision) -> None:
    """Add your approve/edit/reject verdict to an existing run.
    Read, append, rewrite. Not elegant, but a run record is a few KB and this is
      a single-user tool - the simplest correct thing beats a clever one."""
    record = read(runs_dir, run_id)
    record.decisions.append(decision)
    write(runs_dir, record)


def append_published(runs_dir: Path, run_id: str, published: Published) -> None:
    """Record that a draft actually went live, with its URL."""
    record = read(runs_dir, run_id)
    record.published.append(published)
    write(runs_dir, record)
    
def list_run_ids(runs_dir: Path) -> list[str]:
    """Every run on disk, newest first. The filesystem IS the database."""
    if not runs_dir.exists():
        return []
    return sorted((p.stem for p in runs_dir.glob("*/*.json")), reverse=True)



