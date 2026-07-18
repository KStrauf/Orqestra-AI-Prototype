# Codex Adaptation for a Claude-Code-Style Hyper-Agent Team

Treat each agent profile as an instruction contract. When using Codex, paste the relevant profile, task scope, constraints, and acceptance criteria.

## Example Builder Prompt

```text
You are acting as elite-engineer for OrqestraAI.
Read docs/ARCHITECTURE.md and packages/agents/src/profiles/elite-engineer.md.
Task: implement the message bus.
Constraints: keep schemas stable, avoid paid dependencies, keep patch small, run typecheck.
```

## Example QA Prompt

```text
You are acting as deep-qa.
Read packages/agents/src/profiles/deep-qa.md and audit the agent runtime.
Do not write fixes. Return verdict, findings, evidence, and recommendations.
```

Replace Claude-specific NEXUS/SendMessage concepts with this repository's CLI, JSONL message bus, transcript, and handoff files.
