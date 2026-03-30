---
title: Welcome
description: BMad Builder - Build More, Architect Dreams
---

# BMad Builder - A BMad Method EcoSystem Module

**Build More, Architect Dreams.**

## The Dream

Imagine AI that truly knows you — a fitness coach that remembers every PR, a writing partner that knows your characters better than you do, a research assistant that learns your preferences.

BMad Builder lets you create:

- **Personal AI Companions** — Agents with memory that evolve with you over time
- **Domain Experts** — Specialists for any field: legal, medical, creative, technical
- **Workflow Automations** — Structured processes that guide you through complex tasks
- **Custom Modules** — Bundle agents and workflows into shareable packages

## What Makes It Different

| Feature               | Why It Matters                                              |
| --------------------- | ----------------------------------------------------------- |
| **Persistent Memory** | Agents remember across sessions — they learn and grow       |
| **Composable**        | Your creations work alongside the entire BMad ecosystem     |
| **Skill-Compliant**   | Built on open standards that work with any AI tool          |
| **Shareable**         | Package your modules for the BMad Marketplace (coming soon) |

## Quick Start

### 1. Register the Module

On first use, run `bmad-bmb-setup` to register BMad Builder in your project. This collects your preferences (name, language, output paths) and registers the builder's capabilities with the help system so `bmad-help` can guide you.

:::tip[Single-Skill Modules]
If you install a module that contains only one skill, that skill handles its own registration on first run — no separate setup step needed.
:::

### 2. Build Something

Invoke the **Agent Builder** or **Workflow Builder** and describe what you want to create. Both guide you through conversational discovery and produce a ready-to-use skill folder.

| Goal                      | Builder          | Menu Code |
| ------------------------- | ---------------- | --------- |
| AI companion with memory  | Agent Builder    | BA        |
| Structured process / tool | Workflow Builder | BW        |
| Package skills as module  | Module Builder   | CM        |

### 3. Use Your Skill

The builders produce a complete skill folder. To use it, copy the folder into your AI tool's skills directory — for Claude Code that's `.claude/skills/` at project scope or `~/.claude/skills/` at user scope. For other tools, ask your AI agent where skills are installed or consult the tool's documentation.

:::tip[No Module Required]
If you're building something for personal use or just testing it out, you don't need to package it as a module. Copy the skill folder, use it directly. Module packaging (with `bmad-help` registration and configuration) is for when you want to share or need richer discoverability.
:::

### 4. Learn More

See the [Builder Commands Reference](/reference/builder-commands.md) for all capabilities, modes, and phases.

## What You Can Build

| Domain           | Example                                                                                    |
| ---------------- | ------------------------------------------------------------------------------------------ |
| **Personal**     | Journal companion, habit coach, learning tutor, friendly personal companions that remember |
| **Professional** | Code reviewer, documentation specialist, workflow automator                                |
| **Creative**     | Story architect, character developer, campaign designer                                    |
| **Any Domain**   | If you can describe it, you can build it                                                   |

## Design Patterns

Build better skills with these guides distilled from real-world BMad development.

| Guide                                                                                | What You'll Learn                                                    |
| ------------------------------------------------------------------------------------ | -------------------------------------------------------------------- |
| **[Progressive Disclosure](/explanation/progressive-disclosure.md)**                 | Structure skills so they load only the context needed at each moment |
| **[Subagent Patterns](/explanation/subagent-patterns.md)**                           | Six orchestration patterns for parallel and hierarchical work        |
| **[Skill Authoring Best Practices](/explanation/skill-authoring-best-practices.md)** | Core principles, quality dimensions, and anti-patterns               |

## Documentation

| Section                                              | Purpose                                                                  |
| ---------------------------------------------------- | ------------------------------------------------------------------------ |
| **[Concepts](/explanation/)**                        | What agents, workflows, and skills are — and how they relate             |
| **[Design Patterns](/explanation/#design-patterns)** | Progressive disclosure, subagent orchestration, authoring best practices |
| **[Reference](/reference/)**                         | Builder commands, workflow patterns                                      |

## Community

- **[Discord](https://discord.gg/gk8jAdXWmj)** — Get unstuck, share what you built
- **[GitHub](https://github.com/bmad-code-org/bmad-builder)** — Source code
- **[BMad Method](https://docs.bmad-method.org)** — Core framework
