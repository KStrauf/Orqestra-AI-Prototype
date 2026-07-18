"""The ``orq`` command and its user-facing subcommands."""

import argparse
import sys

from engine import runrecord
from engine.config import load_settings
from engine.errors import OrqError
from studio.workflow import ContentWorkflowRequest, run_content_workflow

def cmd_log(settings, run_id: str | None) -> int:
    """Showonerun record, or list them all.  
    This is your window into the system. When a draft is bad, you come here
    and read the exact prompt that produced it. This command is also the thing you
    will screen-record and narrate."""
    if run_id is None:
        ids = runrecord.list_run_ids(settings.runs_dir)
        if not ids:
            print("no runs yet. try: orq run content")
            return 0
        for rid in ids:
            r = runrecord.read(settings.runs_dir, rid)
            cost = f"${r.usage.cost_usd:.4f}" if r.usage else "-"
            print(f"{rid}  {r.agent:<10} {len(r.drafts)} drafts  {cost}")
        return 0
    
    r = runrecord.read(settings.runs_dir, run_id)

    print(f"run      {r.run_id}")
    print(f"agent    {r.agent}")
    print(f"task     {r.task}")
    print(f"status   {r.status}")
    print(f"model    {r.provider}/{r.model}  (temp {r.temperature})")

    if r.usage:
        est = " (estimated)" if r.usage.cost_is_estimate else ""
        print(f"cost     ${r.usage.cost_usd:.4f}{est}   "
            f"{r.usage.input_tokens} in / {r.usage.output_tokens} out")
    if r.duration_ms:
        print(f"took     {r.duration_ms / 1000:.1f}s")

    if r.inputs:
        print("\nINPUTS")
        for i in r.inputs:
            print(f"  {i.source:<8} {i.path}  ({i.chars} chars)")

    print("\nSYSTEM PROMPT")
    print(_indent(r.system_prompt))
    print("\nUSER PROMPT")
    print(_indent(r.user_prompt))

    if r.error:
          print(f"\nERROR\n{_indent(r.error)}")

    for d in r.drafts:
        print(f"\nDRAFT {d.draft_id}   [{d.variant}]   {d.chars} chars")
        if d.constraint_violations:
            print(f"  warning: {', '.join(d.constraint_violations)}")
        print(_indent(d.text))

    if r.review:
        print("\nREVIEW")
        print(_indent(r.review))

    if r.decisions:
        print("\nDECISIONS")
        for d in r.decisions:
            line = f"  {d.draft_id}  {d.decision.upper()}"
            if d.reason_tag:
                line += f"  [{d.reason_tag}] {d.reason}"
            print(line)

    if r.published:
        print("\nPUBLISHED")
        for p in r.published:
            print(f"  {p.draft_id}  {p.platform}  {p.url}")

    return 0


def cmd_studio_demo(
    settings,
    goal: str,
    material: str,
    material_name: str,
) -> int:
    """Run the local Studio workflow and print its reviewable result."""
    result = run_content_workflow(
        settings.runs_dir,
        ContentWorkflowRequest(
            goal=goal,
            material=material,
            material_name=material_name,
        ),
    )
    record = runrecord.read(settings.runs_dir, result.record.run_id)

    print(f"run      {record.run_id}")
    print(f"saved    {result.path}")
    print(f"agents   architect -> specialist -> reviewer")
    print("\nAGENT PLAN")
    print(_indent(record.agent_plan or "(no plan recorded)"))
    for draft in record.drafts:
        print(f"\nDRAFT {draft.draft_id}   [{draft.variant}]")
        print(_indent(draft.text))
    print("\nREVIEW")
    print(_indent(record.review or "(no review recorded)"))
    next_action = (
        "human approval required"
        if record.status == "awaiting_approval"
        else record.status
    )
    print(f"\nNEXT     {record.status} ({next_action})")
    return 0

def _indent(text: str, prefix:str = " | ") -> str:
    """Indent a blockso promptsare visually distinct from. the. metadata."""
    return "\n".join(prefix + line for line in text.splitlines())
def main() -> int:
    """Entry point. `orq` runs this.

    Returns an exit code: 0 = success, 1 = a clean, expected failure.
    Shells care about exit codes; returning them properly is what makes a CLI
    usable inside a script later.
    """
    parser = argparse.ArgumentParser(
        prog="orq",
        description="OrqestraAI - a modular agent system that runs your business.",
    )

    # `dest="command"` stores which subcommand was chosen, so we can dispatch on it.
    # `required=True` means bare `orq` prints help instead of doing nothing.
    sub = parser.add_subparsers(dest="command", required=True)

    # --- Step 3: prove a model call works, end to end -----------------------
    p_ping = sub.add_parser("ping", help="Send one prompt to one model. Proves the wiring works.")
    p_ping.add_argument("model", help="e.g. claude-sonnet-5, gpt-4o, ollama/llama3")
    p_ping.add_argument("prompt", help="What to say to it")

    # --- Step 4-5: show what is configured ---------------------------------
    sub.add_parser("agents", help="List the agents defined in business/agents/")
    sub.add_parser("templates", help="List the output types in business/templates/")

    # --- Step 6-7: see the inputs before spending money ---------------------
    p_material = sub.add_parser("material", help="Show the raw material an agent would ingest")
    p_material.add_argument("agent")

    p_prompt = sub.add_parser("prompt", help="Show the exact prompt that would. be sent")
    p_prompt.add_argument("agent")
    p_prompt.add_argument("--dry-run", action="store_true", help="Print the prompt and send nothing. Costs zero.")

    # --- Step 8: the whole point -------------------------------------------
    p_run = sub.add_parser("run", help="Run an agent. Produces drafts and a run record.")
    p_run.add_argument("agent")
    p_run.add_argument("--output-type", help="Override the manifest's output_type")

    # --- Step 9-10: the human-in-the-loop ----------------------------------
    sub.add_parser("approve", help="Review pending drafts: approve, edit, or reject")
    sub.add_parser("pending", help="List drafts awaiting your decision")

    p_log = sub.add_parser("log", help="Show run records")
    p_log.add_argument("run_id", nargs="?", help="Omit to list all runs")

    p_studio = sub.add_parser("studio", help="Run Orqestra Studio workflows")
    studio_sub = p_studio.add_subparsers(dest="studio_command", required=True)
    p_studio_demo = studio_sub.add_parser(
        "demo", help="Run the local architect-specialist-reviewer workflow"
    )
    p_studio_demo.add_argument("goal", help="The outcome the workflow should produce")
    p_studio_demo.add_argument(
        "--material", required=True, help="Source material supplied to the workflow"
    )
    p_studio_demo.add_argument(
        "--material-name", default="cli-material", help="Display name for the source material"
    )

    # --- Step 13: close the loop -------------------------------------------
    p_publish = sub.add_parser("publish", help="Mark a draft as posted, with its URL")
    p_publish.add_argument("draft_id")
    p_publish.add_argument("--url", required=True)
    p_publish.add_argument("--platform", required=True)

    sub.add_parser("reindex", help="Rebuild the SQLite index from the run record files")

    args = parser.parse_args()
    settings = load_settings()

    try:
        if args.command == "log":
            return cmd_log(settings, args.run_id)
        if args.command == "studio" and args.studio_command == "demo":
            return cmd_studio_demo(
                settings,
                args.goal,
                args.material,
                args.material_name,
            )
        
        raise NotImplementedError(f"'{args.command}' is not built yet. See the build plan.")
    except OrqError as e:
        print(f"error:  {e}",file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
