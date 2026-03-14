---
title: "What Are Skills?"
description: The universal building block underneath agents, workflows, and utilities in the BMad ecosystem
---

Skills are the universal packaging format for everything the BMad Builder produces. Agents are skills. Workflows are skills. Simple utilities are skills. The format follows the [Agent Skills open standard](https://agentskills.io/home).

## Skills in BMad

The BMad Builder produces skills that conform to the open standard and adds a few BMad-specific conventions on top.

| Component | Purpose |
| --------- | ------- |
| **SKILL.md** | The skill's instructions — persona, capabilities, and behavior rules |
| **bmad-manifest.json** | Metadata for installation, discovery, sequencing, and BMad Help integration |
| **prompts/** | Process prompts the skill loads at runtime |
| **resources/** | Reference data, templates, and guidance documents |
| **scripts/** | Deterministic validation and analysis scripts |
| **agents/** | LLM subagent definitions for parallel processing |
| **templates/** | Building blocks for generated output |

Not every skill needs all of these. A simple utility might be a single `SKILL.md` with a manifest. A complex workflow or agent may use the full structure.

## Ready to Use on Build

Unlike earlier BMad versions that produced YAML and XML files requiring compilation, the builders now output a complete skill folder. Place it in your tool's skills directory — `.claude/skills`, `.codex/skills`, `.agent/skills`, or wherever your tool looks — and it is immediately usable.

## Manifests and Sequencing

Every skill's `bmad-manifest.json` can declare where it fits in a larger process. You specify what it runs **before**, what it runs **after**, whether it is **required** or **optional**, and what **output artifact** it produces. The BMad Help system reads these manifests to recommend the right skill at the right time and flag missing prerequisites.

See [What Are Agents](/explanation/what-are-bmad-agents.md) and [What Are Workflows](/explanation/what-are-workflows.md) for how agents and workflows each use this foundation differently.
