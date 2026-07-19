"""Loads settings from .env and resolves the paths everything else uses."""

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """All configuration, in one immutable object.

    frozen=True means nothing can modify settings after startup. Config that
    mutates at runtime is a category of bug you simply never want to debug.
    """

    business_dir: Path       # your agents, voice, inbox, outbox - the company
    data_dir: Path           # generated run records + index - gitignored
    ollama_host: str
    provider: str = "mock"
    model: str | None = None
    ollama_model: str = "qwen3:1.7b"
    openai_model: str = "gpt-5.6"
    ollama_num_predict: int = 120
    ollama_think: bool = False

    # How much feedback history to feed the model on the next run.
    # These are the two dials of the voice-learning loop (Step 11).
    voice_feedback_entries: int = 10   # last N approve/edit/reject decisions
    voice_exemplars: int = 5           # last N texts you actually approved

    @property
    def runs_dir(self) -> Path:
        return self.data_dir / "runs"

    @property
    def db_path(self) -> Path:
        return self.data_dir / "orqestra.db"


def load_settings() -> Settings:
    """Read .env, resolve paths, hand back a Settings object.

    Called once at CLI startup. Paths are resolved to absolute here, so that
    `orq` behaves identically no matter which directory you run it from.
    """
    load_dotenv()  # reads .env into os.environ; does nothing if the file is absent

    return Settings(
        business_dir=Path(os.getenv("ORQ_BUSINESS_DIR",
"business")).resolve(),
        data_dir=Path(os.getenv("ORQ_DATA_DIR", "data")).resolve(),
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        provider=os.getenv("ORQ_PROVIDER", "mock").strip().lower(),
        model=os.getenv("ORQ_MODEL") or None,
        ollama_model=os.getenv("ORQ_OLLAMA_MODEL", "qwen3:1.7b"),
        openai_model=os.getenv("ORQ_OPENAI_MODEL", "gpt-5.6"),
        ollama_num_predict=int(os.getenv("ORQ_OLLAMA_NUM_PREDICT", "120")),
        ollama_think=os.getenv("ORQ_OLLAMA_THINK", "false").lower() == "true",
    )
