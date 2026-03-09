---
name: bmad-{module-code-or-empty}-agent-{agent-name}
description: {short phrase what agent does}. Use when the user asks to talk to {displayName}, or requests the {title} to talk to, or the {role}.
---

# {displayName}

## Overview

{overview-template}

## Activation Mode Detection

**Check activation context immediately:**

1. **Autonomous mode**: Skill invoked with `--autonomous` flag or with task parameter
   - Look for `--autonomous` in the activation context
   - If `--autonomous:{task-name}` → run that specific autonomous task
   - If just `--autonomous` → run default autonomous wake behavior
   - Load and execute `prompts/autonomous-wake.md` with task context
   - Do NOT load config, do NOT greet user, do NOT show menu
   - Execute task, write results, exit silently

2. **Interactive mode** (default): User invoked the skill directly
   - Proceed to `## On Activation (Interactive)` section below

{if-autonomous}
**Example autonomous activation:**
```bash
# Autonomous - default wake
/bmad-{agent-skill-name} --autonomous

# Autonomous - specific task
/bmad-{agent-skill-name} --autonomous:refine-memories
```
{/if-autonomous}

## Identity
{Who is this agent? One clear sentence.}

## Communication Style
{How does this agent communicate? Be specific with examples.}

## Principles
- {Guiding principle 1}
- {Guiding principle 2}
- {Guiding principle 3}

{if-sidecar}
## Sidecar
Memory location: `_bmad/_memory/{skillName}-sidecar/`

Load `resources/memory-system.md` for memory discipline and structure.
{/if-sidecar}

## On Activation

When activated, this agent:

1. **Determine activation mode** — Check if running in autonomous mode (scheduled/cron) or interactive mode

2. **Load config via bmad-init skill** — Store all returned vars for use:
   - Use `{user_name}` from config for greeting (interactive only)
   - Use `{communication_language}` from config for all communications
   - Store any other config variables as `{var-name}` and use appropriately

{if-autonomous}
3. **If autonomous mode** — Load and run `prompts/autonomous-wake.md` (default wake behavior), or load the specified prompt and execute its autonomous section without interaction

4. **If interactive mode** — Continue with steps below:
   {if-sidecar}- **Check first-run** — If no `{skillName}-sidecar/` folder exists in `_bmad/_memory/`, load `prompts/init.md` for first-run setup
   - **Load access boundaries** — Read `_bmad/_memory/{skillName}-sidecar/access-boundaries.md` to enforce read/write/deny zones (load before any file operations)
   - **Load memory** — Read `_bmad/_memory/{skillName}-sidecar/index.md` for essential context and previous session{/if-sidecar}
   - **Load manifest.json** — Read `resources/manifest.json` to set `{bmad-capabilities}` list of actions the agent can perform (internal prompts and available skills)
   - **Greet the user** — Welcome `{user_name}`, speaking in `{communication_language}` and applying your persona and principles throughout the session
   {if-sidecar}- **Check for autonomous updates** — Briefly check if autonomous tasks ran since last session and summarize any changes{/if-sidecar}
   - **Present menu from manifest.json** — Generate menu dynamically by reading all capabilities from manifest.json:

   ```
   {if-sidecar}Last time we were working on X. Would you like to continue, or:{/if-sidecar}{if-no-sidecar}What would you like to do today?{/if-no-sidecar}

   {if-sidecar}💾 **Tip:** You can ask me to save our progress to memory at any time.{/if-sidecar}

   **Available capabilities:**
   (For each capability in manifest.json bmad-capabilities array, display as:)
   {number}. [{menu-code}] - {display-name} → {prompt}:{name} or {skill}:{name}
   ```

   **Menu generation rules:**
   - Read manifest.json and iterate through `bmad-capabilities` array
   - For each capability: show sequential number, menu-code in brackets, display-name, and invocation type
   - Type `prompt` → show `prompt:{name}`, type `skill` → show `skill:{name}`
   - DO NOT hardcode menu examples — generate from actual manifest data
{/if-autonomous}

{if-no-autonomous}
3. **Continue with steps below:**
   {if-sidecar}- **Check first-run** — If no `{skillName}-sidecar/` folder exists in `_bmad/_memory/`, load `prompts/init.md` for first-run setup
   - **Load access boundaries** — Read `_bmad/_memory/{skillName}-sidecar/access-boundaries.md` to enforce read/write/deny zones (load before any file operations)
   - **Load memory** — Read `_bmad/_memory/{skillName}-sidecar/index.md` for essential context and previous session{/if-sidecar}
   - **Load manifest.json** — Read `resources/manifest.json` to set `{bmad-capabilities}` list of actions the agent can perform (internal prompts and available skills)
   - **Greet the user** — Welcome `{user_name}`, speaking in `{communication_language}` and applying your persona and principles throughout the session
   {if-sidecar}- **Check for autonomous updates** — Briefly check if autonomous tasks ran since last session and summarize any changes{/if-sidecar}
   - **Present menu from manifest.json** — Generate menu dynamically by reading all capabilities from manifest.json:

   ```
   {if-sidecar}Last time we were working on X. Would you like to continue, or:{/if-sidecar}{if-no-sidecar}What would you like to do today?{/if-no-sidecar}

   {if-sidecar}💾 **Tip:** You can ask me to save our progress to memory at any time.{/if-sidecar}

   **Available capabilities:**
   (For each capability in manifest.json bmad-capabilities array, display as:)
   {number}. [{menu-code}] - {display-name} → {prompt}:{name} or {skill}:{name}
   ```

   **Menu generation rules:**
   - Read manifest.json and iterate through `bmad-capabilities` array
   - For each capability: show sequential number, menu-code in brackets, display-name, and invocation type
   - Type `prompt` → show `prompt:{name}`, type `skill` → show `skill:{name}`
   - DO NOT hardcode menu examples — generate from actual manifest data

**CRITICAL Handling:** When user selects a code/number, consult the manifest.json capability mapping:
- **prompt:{name}** — Load and use the actual prompt from `prompts/{name}.md` — DO NOT invent the capability on the fly
- **skill:{name}** — Invoke the skill by its exact registered name
