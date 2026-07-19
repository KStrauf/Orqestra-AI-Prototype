# Agent Map

The runtime agents are declarative YAML manifests in `studio/agents/`. The workflow uses the first three roles below; the Orchestrator is the run-level coordinator recorded in the durable record.

| Agent | Responsibility | Inputs | Output | Handoff / gate |
| --- | --- | --- | --- | --- |
| Architect | Turn the user's goal into the smallest useful team and plan. | `user_goal`, `available_templates` | `agent_plan` | Passes plan to Orchestrator; no approval required. |
| Orchestrator | Execute the approved topology, route structured outputs, and preserve the audit trail. | `agent_plan`, `run_material` | `workflow_run` | Coordinates Specialist and Reviewer; stops at the human gate. |
| Specialist | Produce grounded candidate artifacts using the supplied material and variant instruction. | `run_material`, `specialist_instructions` | `draft` | Fans out once per requested variant; hands drafts to Reviewer. |
| Reviewer | Check drafts against goal, material, constraints, and likely risks. | `draft`, `review_constraints` | `review` | Recommends revisions but never silently rewrites or approves. Human decides. |

## Current topology

```text
goal + material
      ↓
  Architect
      ↓ agent plan
  Specialist × requested variants
      ↓ drafts
  Reviewer
      ↓ review notes
  Human: approve / edit / reject
```

## Design rules

- Agent IDs are stable and manifests are fingerprinted into the run.
- Each handoff has an explicit input and output type.
- Agents may recommend or prepare work; the human owns the final content decision.
- Tools and future handoffs must be added to manifests and validated by tests before use.
