# Agent Map

The runtime agents are declarative YAML manifests in `studio/agents/`. The workflow uses the first three roles below; the Orchestrator is the run-level coordinator recorded in the durable record.

| Agent | Responsibility | Inputs | Output | Handoff / gate |
| --- | --- | --- | --- | --- |
| Architect | Turn the user's idea into a useful content brief, assumptions, and smallest useful team plan. | `user_goal`, `content_context`, `available_templates` | `content_brief`, `agent_plan` | Passes plan to Orchestrator; no approval required. |
| Orchestrator | Execute the approved topology, route structured outputs, and preserve the audit trail. | `agent_plan`, `run_material` | `workflow_run` | Coordinates Specialist and Reviewer; stops at the human gate. |
| Specialist | Produce grounded, platform-aware candidate content using the supplied material, brief, hook direction, and variant instruction. | `run_material`, `content_brief`, `hook_candidates`, `specialist_instructions` | `draft` | Fans out once per requested variant; hands drafts to Reviewer. |
| Reviewer | Check drafts against goal, material, platform, creator context, and likely risks. | `draft`, `content_brief`, `review_constraints`, `brand_profile` | `review`, `quality_report` | Recommends revisions but never silently rewrites or approves. Human decides. |

## Current topology

```text
idea + optional material
      ↓
Architect + idea coach
      ↓ brief + plan
 hook strategist
      ↓ hook directions
  Specialist × requested variants
      ↓ drafts
Reviewer + editorial grader
      ↓ review notes + checks
  Human: approve / edit / reject
```

## Design rules

- Agent IDs are stable and manifests are fingerprinted into the run.
- Each handoff has an explicit input and output type.
- Agents may recommend or prepare work; the human owns the final content decision.
- Tools and future handoffs must be added to manifests and validated by tests before use.
- Content capabilities are stage-owned skills, not a proliferation of independent agents.
- Hook and quality outputs explain editorial choices; they do not predict or guarantee engagement.
