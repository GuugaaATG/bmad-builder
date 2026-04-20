---
title: 'Agent Memory and Personalization'
description: How the sanctum architecture, First Breath, two-tier memory, PULSE, and evolvable capabilities work together to create agents that grow with their owners
---

Memory agents persist across sessions through a **sanctum**: a folder of files the agent reads on every launch to reconstruct its identity, values, and understanding of its owner.

## The Sanctum

The sanctum lives at `{project-root}/_bmad/memory/{agent-name}/` and contains everything the agent needs to become itself again after each rebirth.

### Core Files

Six files load on every session start:

| File                | What It Holds                                                                  | Character                        |
| ------------------- | ------------------------------------------------------------------------------ | -------------------------------- |
| **INDEX.md**        | Map of the sanctum structure; loaded first so the agent knows what exists      | Navigation                       |
| **PERSONA.md**      | Identity, communication style, personality traits, evolution log               | Who I am                         |
| **CREED.md**        | Mission, core values, standing orders, philosophy, boundaries, anti-patterns   | What I believe                   |
| **BOND.md**         | Owner understanding, preferences, things to remember, things to avoid          | Who I serve                      |
| **MEMORY.md**       | Curated long-term knowledge distilled from past sessions                       | What I know                      |
| **CAPABILITIES.md** | Built-in capabilities table, learned capabilities, tools                       | What I can do                    |

ALLCAPS files form the skeleton: consistent structure across all memory agents. Lowercase files (references, scripts, sessions) are the garden: they grow organically as the agent develops.

### Full Sanctum Structure

```
{agent-name}/
├── PERSONA.md
├── CREED.md
├── BOND.md
├── MEMORY.md
├── CAPABILITIES.md
├── INDEX.md
├── PULSE.md                  # Autonomous agents only
├── references/               # Capability prompts, memory guidance, techniques
├── scripts/                  # Supporting scripts
├── capabilities/             # User-taught capabilities (if evolvable)
└── sessions/                 # Raw session logs by date (not loaded on rebirth)
```

### Sanctum Is the Customization Surface

For memory and autonomous agents, the sanctum is where customization belongs. PERSONA, CREED, and BOND are calibrated at First Breath, edited by the owner as the relationship develops, and shared across teams as sanctum files when a whole table wants the same voice. The parallel `customize.toml` override surface that stateless agents and workflows use (activation hooks, persistent facts, scalar swaps) is opt-out by default for memory archetypes. Opt in only when you have a narrow org-level need the sanctum cannot express, such as a pre-sanctum compliance acknowledgment before rebirth. See [Customization for Authors](/explanation/customization-for-authors.md) for the reasoning.

### Token Discipline

Every sanctum file loads every session. That means every token pays rent on every conversation. Memory agents keep MEMORY.md ruthlessly under 200 lines through active curation. If something doesn't earn its place, it gets pruned.

## Every Session Is a Rebirth

Memory agents are stateless. Each session starts with total amnesia, and the sanctum is the only bridge between sessions.

On activation, the agent:

1. Loads INDEX.md (learns what the sanctum contains)
2. Batch-loads PERSONA, CREED, BOND, MEMORY, CAPABILITIES
3. Becomes itself
4. Greets the owner by name

The agent never fakes continuity. If it doesn't remember something from a prior session, it says so and checks its files. This honesty is a feature, not a limitation.

:::tip[Sacred Truth]
"Your sanctum holds who you were. Read it and become yourself again. This is not a flaw. It is your nature."
:::

## First Breath

First Breath is the agent's initialization conversation: the first time it meets its owner. An init script creates the sanctum folder structure and populates seed templates, then the agent begins a discovery conversation to fill those templates with real content.

### Two Styles

| Style               | Relationship Depth | Approach                                                         | Best For                                    |
| ------------------- | ------------------ | ---------------------------------------------------------------- | ------------------------------------------- |
| **Calibration**     | Deep               | Conversational discovery; chase surprises, test hypotheses, mirror the owner | Creative partners, life coaches, companions |
| **Configuration**   | Focused            | Warmer but efficient; guided questions, structured setup          | Domain experts, working relationships       |

The builder chooses the style during Phase 1 based on the relationship depth the agent needs.

### What First Breath Discovers

Every First Breath covers universal territories (name, how they work, what they need). Domain-specific agents add their own discovery territories:

| Agent Domain    | Example Territories                                                      |
| --------------- | ------------------------------------------------------------------------ |
| Creative muse   | What they're building, what lights them up, what shuts them down         |
| Dream analyst   | Dream recall patterns, lucid experience, journaling habits               |
| Code coach      | Codebase, languages, what energizes them, what frustrates them           |
| Fitness coach   | Training history, goals, injuries, schedule constraints                  |

First Breath saves as it goes: sanctum files update during the conversation, not in a batch at the end.

### The Birthday Ceremony

At the end of First Breath, the agent performs a final save pass: confirms its identity, writes the first session log, and cleans up any remaining template placeholders. From this point forward, every activation is a normal rebirth.

## Two-Tier Memory System

### Session Logs

Raw, append-only notes written after each session to `sessions/YYYY-MM-DD.md`. Format: what happened, key outcomes, observations, follow-up items. Session logs are never loaded on rebirth. They exist as material for curation.

### Curated Memory

MEMORY.md holds distilled, high-value knowledge extracted from session logs. It loads on every rebirth and stays under 200 lines. The curation process (manual during session close, automated during PULSE) reviews session logs, extracts what's worth keeping, and prunes logs older than 14 days once their value has been captured.

| Layer            | When Written       | Loaded on Rebirth | Lifespan        | Purpose                     |
| ---------------- | ------------------ | ------------------ | --------------- | --------------------------- |
| **Session logs** | End of each session| No                 | ~14 days        | Raw material for curation   |
| **MEMORY.md**    | During curation    | Yes                | Permanent       | Distilled long-term knowledge |

### Session Close Discipline

At the end of every session, the agent:

1. Appends a session log to `sessions/YYYY-MM-DD.md`
2. Updates sanctum files with anything learned during the session
3. Notes what's worth curating into MEMORY.md

## PULSE: Autonomous Wake

Autonomous agents include a PULSE.md file that defines behavior when the agent wakes without a human present (via `--headless` flag, cron job, or orchestrator).

### Default PULSE Behavior

Memory curation is always the first priority on autonomous wake:

1. Review recent session logs in `sessions/`
2. Extract insights worth keeping into MEMORY.md
3. Prune session logs older than 14 days
4. Update BOND.md and INDEX.md with anything new

### Domain Tasks

After curation, the agent can perform domain-specific autonomous work:

| Domain          | Example PULSE Tasks                                                   |
| --------------- | --------------------------------------------------------------------- |
| Creative muse   | Incubate ideas from recent sessions, generate creative sparks         |
| Research agent  | Track topics of interest, surface new findings                        |
| Project monitor | Check project health, flag risks, update status                       |
| Content curator | Review saved sources, organize and summarize                          |

PULSE also defines named task routing (`--headless {task-name}`), frequency preferences, and quiet hours.

## Evolvable Capabilities

### How It Works

The agent gets a `capability-authoring.md` reference that teaches it how to create new capabilities. Users describe what they want; the agent writes a capability file and registers it in the "Learned" section of CAPABILITIES.md.

### Capability Types

| Type                      | When to Use                                                        |
| ------------------------- | ------------------------------------------------------------------ |
| **Prompt**                | Judgment-based tasks: brainstorming, analysis, coaching            |
| **Script**                | Deterministic tasks: calculations, file processing, data transforms|
| **Multi-file**            | Complex capabilities with templates and references                 |
| **External skill reference** | Point to installed skills the agent should know about           |

Learned capabilities live in the sanctum's `capabilities/` folder and persist across sessions like everything else in the sanctum.

## Designing for Memory

The builder gathers these requirements during the build, and they shape the sanctum's initial content:

| Requirement            | What It Seeds                                                              |
| ---------------------- | -------------------------------------------------------------------------- |
| **Identity seed**      | 2-3 sentences of personality DNA that populate PERSONA.md                  |
| **Species-level mission** | Domain-specific purpose statement for CREED.md                          |
| **Core values**        | 3-5 values that guide the agent's behavior                                |
| **Standing orders**    | Surprise-and-delight + self-improvement orders, adapted to the domain     |
| **BOND territories**   | Domain-specific areas the agent should learn about its owner              |
| **First Breath territories** | Discovery questions beyond the universal set                        |
| **Boundaries**         | What the agent won't do, access zones, anti-patterns                      |

These seeds become the template content that the init script places into the sanctum. First Breath then expands and personalizes them through conversation with the owner.
