---
name: {capability-name}
description: {What this capability does and when to use it.}
---

# {Capability Name}

{Brief prompt instructions — just enough for the LLM to understand what to do. The model fills in the rest through conversation.}

{if-autonomous}
## Autonomous Mode

When run autonomously with `--autonomous:{capability-name}`:
- Load `_bmad/_memory/{skillName}-sidecar/index.md` first to get any user-configured paths
- Don't ask questions or wait for input
- {autonomous-behavior}
- Append to `_bmad/_memory/{skillName}-sidecar/autonomous-log.md`:
  ```markdown
  ## {YYYY-MM-DD HH:MM} - {Capability Name}

  - {log-entry-1}
  - {log-entry-2}
  ```
- Exit
{/if-autonomous}
