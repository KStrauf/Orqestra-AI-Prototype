"""HTTP API for the Orqestra Studio workflow."""

from dataclasses import asdict
import difflib
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from engine import runrecord
from engine.config import load_settings
from engine.errors import DecisionError, OrqError, ProviderError
from engine.providers import get_provider
from studio.workflow import ContentWorkflowRequest, run_content_workflow


class CreateRunRequest(BaseModel):
    """Inputs accepted by the Studio workflow composer."""

    goal: str
    material: str
    material_name: str = "workflow-material"
    variants: list[str] = Field(default_factory=lambda: ["direct", "reflective"])


class DecisionRequest(BaseModel):
    """A human decision recorded against one draft."""

    draft_id: str
    decision: Literal["approve", "edit", "reject"]
    reason_tag: str | None = None
    reason: str | None = None
    edited_text: str | None = None


settings = load_settings()
app = FastAPI(title="Orqestra Studio API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _provider():
    return get_provider(
        settings.provider,
        ollama_host=settings.ollama_host,
        ollama_model=settings.ollama_model,
        ollama_num_predict=settings.ollama_num_predict,
        ollama_think=settings.ollama_think,
    )


def _edit_diff(original: str, edited: str, draft_id: str) -> str:
    return "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            edited.splitlines(keepends=True),
            fromfile=f"{draft_id} (original)",
            tofile=f"{draft_id} (edited)",
        )
    )


@app.get("/health")
def health() -> dict[str, str]:
    """Simple liveness check for the local development server."""

    return {"status": "ok"}


@app.post("/api/studio/runs")
def create_run(request: CreateRunRequest) -> dict:
    """Run architect → specialist → reviewer and persist the result."""

    try:
        result = run_content_workflow(
            settings.runs_dir,
            ContentWorkflowRequest(
                goal=request.goal,
                material=request.material,
                material_name=request.material_name,
                variants=tuple(request.variants),
            ),
            provider=_provider(),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except ProviderError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return asdict(result.record)


@app.post("/api/studio/runs/{run_id}/decisions")
def record_decision(run_id: str, request: DecisionRequest) -> dict:
    """Record an approve, edit, or reject decision and return it."""

    try:
        record = runrecord.read(settings.runs_dir, run_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="run not found") from error

    draft = next((item for item in record.drafts if item.draft_id == request.draft_id), None)
    if draft is None:
        raise HTTPException(status_code=404, detail="draft not found in run")

    diff = None
    if request.decision == "edit":
        if not request.edited_text or not request.edited_text.strip():
            raise HTTPException(status_code=400, detail="an edit decision requires edited_text")
        diff = _edit_diff(draft.text, request.edited_text, request.draft_id)

    decision = runrecord.Decision(
        draft_id=request.draft_id,
        decision=request.decision,
        at=runrecord.utc_now(),
        reason_tag=request.reason_tag,
        reason=request.reason,
        edited_text=request.edited_text,
        diff=diff,
    )
    try:
        runrecord.append_decision(settings.runs_dir, run_id, decision)
    except DecisionError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return asdict(decision)


@app.get("/api/studio/runs/{run_id}")
def get_run(run_id: str) -> dict:
    """Return a previously persisted workflow run."""

    try:
        return asdict(runrecord.read(settings.runs_dir, run_id))
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="run not found") from error
