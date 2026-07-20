"""HTTP API for the Orqestra Studio workflow."""

from dataclasses import asdict
import difflib

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from engine import runrecord
from engine.config import load_settings
from engine.errors import DecisionError, ProviderError
from engine.providers import get_provider
from studio.schemas import (
    CreateRunRequest,
    DecisionRequest,
    DecisionResponse,
    RunListResponse,
    RunResponse,
    run_response,
    run_summary,
)
from studio.workflow import ContentWorkflowRequest, run_content_workflow


settings = load_settings()
app = FastAPI(title="Orqestra Studio API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _error_code(status_code: int) -> str:
    if status_code == 400:
        return "bad_request"
    if status_code == 404:
        return "not_found"
    if status_code == 422:
        return "validation_error"
    if status_code == 502:
        return "provider_error"
    return "http_error"


def _error_response(
    *, status_code: int, detail: object, code: str | None = None, message: str | None = None
) -> JSONResponse:
    rendered_message = message or (detail if isinstance(detail, str) else "request failed")
    body = {
        "detail": detail,
        "error": {
            "code": code or _error_code(status_code),
            "message": rendered_message,
            "details": None if isinstance(detail, str) else detail,
        },
    }
    return JSONResponse(status_code=status_code, content=jsonable_encoder(body))


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exception: HTTPException) -> JSONResponse:
    """Keep FastAPI's legacy detail field while exposing one error envelope."""

    return _error_response(status_code=exception.status_code, detail=exception.detail)


@app.exception_handler(RequestValidationError)
async def request_validation_handler(
    _request: Request, exception: RequestValidationError
) -> JSONResponse:
    details = jsonable_encoder(exception.errors())
    return _error_response(
        status_code=422,
        detail=details,
        code="validation_error",
        message="request validation failed",
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
def create_run(request: CreateRunRequest) -> RunResponse:
    """Run architect → specialist → reviewer and persist the result."""

    try:
        result = run_content_workflow(
            settings.runs_dir,
            ContentWorkflowRequest(
                goal=request.goal,
                material=request.material,
                material_name=request.material_name,
                variants=tuple(request.variants),
                platform=request.platform,
                audience=request.audience,
                outcome=request.outcome,
                tone=request.tone,
                brief=request.brief,
            ),
            provider=_provider(),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except ProviderError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return run_response(result.record)


@app.post("/api/studio/runs/{run_id}/decisions", response_model=DecisionResponse)
def record_decision(run_id: str, request: DecisionRequest) -> DecisionResponse:
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
    return DecisionResponse.model_validate(asdict(decision))


@app.get("/api/studio/runs", response_model=RunListResponse)
def list_runs(limit: int = Query(default=50, ge=1, le=100)) -> RunListResponse:
    """Return newest durable runs in compact form for Studio history."""

    records = runrecord.list_records(settings.runs_dir, limit=limit)
    summaries = [run_summary(record) for record in records]
    return RunListResponse(runs=summaries, count=len(summaries), limit=limit)


@app.get("/api/studio/runs/{run_id}", response_model=RunResponse)
def get_run(run_id: str) -> RunResponse:
    """Return a previously persisted workflow run."""

    try:
        return run_response(runrecord.read(settings.runs_dir, run_id))
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="run not found") from error
