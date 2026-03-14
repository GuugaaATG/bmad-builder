---
title: "BMad Skill Manifest Reference"
description: Complete field reference for bmad-manifest.json — the metadata file that powers discovery, sequencing, and BMad Help integration
---

Every BMad skill includes a `bmad-manifest.json` file that describes what the skill is, what it can do, and where it fits in a larger workflow sequence. Agents and workflows share a single unified schema; agents simply use additional fields.

## Skill Type Detection

The manifest determines whether a skill is treated as an agent or a workflow based on field presence.

| Condition | Skill Type |
| --------- | ---------- |
| `persona` field present | Agent |
| `persona` field absent | Workflow or utility |

## Root Fields

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `module-code` | string | No | Short code for the module this skill belongs to (e.g., `bmb`, `cis`). Omit for standalone skills. Pattern: `^[a-z][a-z0-9-]*$` |
| `replaces-skill` | string | No | Registered name of the BMad skill this replaces. During `bmad-init`, the replacement inherits the original's metadata |
| `persona` | string | No | Distillation of the agent's essence — who they are, how they operate, what drives them. Presence of this field marks the skill as an agent. Other skills and agents use this to understand who they are interacting with |
| `has-memory` | boolean | No | Whether this skill persists state across sessions via sidecar memory |
| `capabilities` | array | **Yes** | What this skill can do. Every skill must have at least one capability |

:::note[Agent-Specific Fields]
`persona` and `has-memory` are the fields that distinguish agents from workflows. A workflow manifest typically omits both.
:::

## Capability Fields

Each entry in the `capabilities` array describes one thing the skill can do.

### Identity

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `name` | string | **Yes** | Capability identifier. Pattern: `^[a-z][a-z0-9-]*$` |
| `menu-code` | string | **Yes** | 2-3 uppercase letter shortcut for interactive menus. Pattern: `^[A-Z]{2,3}$` |
| `description` | string | **Yes** | What this capability does and when to suggest it |

### Execution

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `supports-autonomous` | boolean | No | Whether this capability can run without user interaction |
| `prompt` | string | No | Relative path to the prompt file for internal capabilities (e.g., `prompts/build-process.md`). Omit if handled by SKILL.md directly or if this is an external skill call |
| `skill-name` | string | No | Registered name of an external skill this capability delegates to. Omit for internal capabilities |

:::caution[Prompt vs Skill-Name]
A capability should have `prompt` or `skill-name`, never both. The `prompt` field points to an internal prompt file; `skill-name` delegates to an external skill.
:::

### Sequencing

These fields control how BMad-Help orders skills within a module.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `phase-name` | string | No | Which module phase this capability belongs to (e.g., `planning`, `design`, `anytime`) |
| `after` | string[] | No | Skill names that should ideally run before this capability. If those skills have `is-required: true`, they block this one |
| `before` | string[] | No | Skill names this capability should ideally run before. Helps the module sequencer understand ordering |
| `is-required` | boolean | No | Whether this capability must complete before skills listed in its `before` array can proceed |
| `output-location` | string | No | Where this capability writes its output. May contain config variables (e.g., `{bmad_builder_output_folder}`) |

## Examples

**Agent manifest** (agent builder) — note the `persona` field:

```json
{
  "module-code": "bmb",
  "persona": "An architect guide who helps dreamers and builders create AI agents through conversational discovery.",
  "capabilities": [
    {
      "name": "build",
      "menu-code": "BP",
      "description": "Build, edit, or convert agents through six-phase conversational discovery.",
      "supports-autonomous": true,
      "prompt": "prompts/build-process.md",
      "phase-name": "anytime",
      "output-location": "{bmad_builder_output_folder}"
    }
  ]
}
```

**Workflow manifest** (workflow builder) — no persona, no memory:

```json
{
  "module-code": "bmb",
  "capabilities": [
    {
      "name": "build",
      "menu-code": "BP",
      "description": "Build, edit, or convert workflows and skills through six-phase conversational discovery.",
      "supports-autonomous": true,
      "prompt": "prompts/build-process.md",
      "phase-name": "anytime",
      "output-location": "{bmad_builder_output_folder}"
    }
  ]
}
```

## Validation

The `manifest.py` script handles all manifest operations and validates against the schema on every write.

```bash
# Validate an existing manifest
python3 scripts/manifest.py validate <skill-path>

# Create a new manifest
python3 scripts/manifest.py create <skill-path> --module-code mymod --persona "..."

# Add a capability
python3 scripts/manifest.py add-capability <skill-path> \
  --name build --menu-code BP \
  --description "Build things" \
  --supports-autonomous --prompt prompts/build.md

# Read manifest summary
python3 scripts/manifest.py read <skill-path>

# Update a field
python3 scripts/manifest.py update <skill-path> --set persona="New persona"

# Update a capability field
python3 scripts/manifest.py update <skill-path> \
  --set capability.build.description="Updated description"
```

Beyond schema validation, the script checks for duplicate `menu-code` values and capabilities that specify both `prompt` and `skill-name`.
