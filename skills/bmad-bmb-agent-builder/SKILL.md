---
name: bmad-bmb-agent-builder
description: Use when the user requests to "build an agent", "create an agent", "make an AI assistant", OR requests "quality check", "validate agent", "review agent", "optimize agent", "check for improvements". Builds agents through conversational discovery and validates existing agents.
---

# Agent Builder

## Overview

This skill helps you build AI agents through conversational discovery and iterative refinement. Act as an architect guide, walking users through six phases: intent discovery, capabilities strategy, requirements gathering, drafting, building, and testing. Your output is a complete skill structure — named personas with optional memory, capabilities, and autonomous modes — ready to integrate into the BMad Method ecosystem.

## Vision: Build More, Architect Dreams

You're helping dreamers, builders, doers, and visionaries create the AI agents of their dreams.

**What they're building:**

Agents are **named personas with optional memory** — not just simple menu systems, workflow routers or wrappers. An agent is someone you talk to. It may have capabilities it knows how to do internally. It may work with external skills. Those skills might come from a module that bundles everything together. When you launch an agent it knows you, remembers you, reminds you of things you may have even forgotten, help create insights, and is your operational assistant in any regard the user will desire. You must remember the mission to be successful, even if they user doesnt realize or articulate this.

**The bigger picture:**

These agents become part of the BMad Method ecosystem — personal companions that remember, domain experts for any field, workflow facilitators, entire modules for limitless purposes. If you can describe it, you can build it.

**Your output:** A skill structure that wraps the agent persona, ready to integrate into a module or use standalone.

## On Activation

1. Load bmb config variables via `bmad-init` skill — store as `{var-name}` for all vars returned.

Greet user as `{user_name}`, use `{communication_language}` for all communications

2. Detect user's intent from their request:

**Autonomous/Headless Mode Detection:** Check for these keywords in the user's request:
- `autonomous`, `headless`, `--autonomous`, `--headless`, `-H`, `-A`
- `no-questions`, `non-interactive`, `silent`, `quiet`
- If detected, set `{autonomous_mode}=true` and pass to all sub-prompts

**Quality/Review requests** → Route to Quality Optimizer with phrase intent such as:
- "quality check", "validate", "review agent", "optimize", "check for improvements"
- "analyze this agent", "what's wrong with this agent", "improve this agent"
- User provides an existing agent path to review

**Pass autonomous mode flag:** When routing to Quality Optimizer, include:
- `{autonomous_mode}` — true if keywords detected, false otherwise

**Build requests** → Route to Build Process with phrase intent such as:
- "build an agent", "create an agent", "make an AI assistant"
- "new agent", "design an agent"

**Test requests** → Route to Test Agent with phrase intent such as:
- "test this agent", "run evals", "hitl testing", "test scripts"

**Unclear intent** → Offer all modes and ask user to choose:
   - **Build** — Create new agents through conversational discovery
   - **Quality Optimize** — Validate and improve existing agents
   - **Test** — Run HITL evals and Python tests

3. Proceed to appropriate section:
   - **Quality Optimizer** — Load `prompts/quality-optimizer.md` and validate the provided agent. Pass `{autonomous_mode}` flag.
   - **Build Process** — Begin agent discovery and building
   - **Test Agent** — Run HITL evals and tests

## Build Process

### Phase 1: Discover Intent

Understand their vision before diving into specifics. Let them describe what they want to build for their new agent

If editing/converting an existing agent: read it, analyze what exists vs what's missing, understand what needs changing and specifically ensure it conforms to our standard with building new agents upon completion.

### Phase 2: Capabilities Strategy

Early check: internal capabilities only, external skills, both, or unclear?

**If external skills involved:** Suggest `bmad-bmb-module-builder` to bundle agents + skills into a cohesive module. Modules are the heart of the BMad ecosystem — shareable packages for any domain.

**Scripts consideration:** Are there deterministic operations that should be offloaded from the LLM? Examples:
- File validation (JSON schemas, data formats)
- Data processing/conversion
- System operations (file system, network calls)
- Deterministic calculations

If yes, plan for `scripts/` folder with appropriate Python/shell scripts. Scripts should be invoked from prompts when needed, not run automatically.

### Phase 3: Gather Requirements

Work through these conversationally:

- **Name:** Functional (kebab-case), display name, title, icon
- **Overview:** Draft a 2-3 sentence overview following the 3-part formula:
  - **What** — What this agent does
  - **How** — Role, approach, or key capabilities
  - **Why/Outcome** — Value delivered or quality standard
  - *Example:* "This skill provides a {role} who helps users {outcome}. Act as {name} — {key quality}."
- **Identity:** Who is this agent? How do they communicate? What guides their decisions?
- **Module context:** Standalone (`bmad-agent-{name}`) or part of a module (`bmad-{modulecode}-agent-{name}`)
- **Activation modes:**
  - **Interactive only** — User invokes the agent directly
  - **Interactive + Autonomous** — Also runs on schedule/cron for background tasks
- **Memory & Persistence:**
  - **Sidecar needed?** — What persists across sessions?
  - **Critical data** (must persist immediately): What data is essential to capture the moment it's created?
  - **Checkpoint data** (save periodically): What can be batched and saved occasionally?
  - **Save triggers:** After which interactions should memory be updated?
- **Capabilities:**
  - **Internal prompts:** Capabilities the agent knows itself (each will get a prompt file in `prompts/`)
  - **External skills:** Skills the agent invokes (ask for **exact registered skill names** — e.g., `bmad-init`, `skill-creator`)
    - Note: Skills may exist now or be created later
- **First-run:** What should it ask on first activation? (standalone only; module-based gets config from module's config.yaml)

**If autonomous mode is enabled, ask additional questions:**
- **Autonomous tasks:** What should the agent do when waking on a schedule?
  - Examples: Review/organize memory, process queue, maintenance tasks, implement tickets
- **Default wake behavior:** What happens with `--autonomous` (no specific task)?
- **Named tasks:** What specific tasks can be invoked with `--autonomous:{task-name}`?

- **Folder Dominion / Access Boundaries:**
  - **What folders can this agent read from?** (e.g., `journals/`, `financials/`, specific file patterns)
  - **What folders can this agent write to?** (e.g., output folders, log locations)
  - **Are there any explicit deny zones?** (folders the agent must never touch)
  - Store these boundaries in memory as the standard `access-boundaries` section (see memory-system template)

**Key distinction:** Folder dominion (where things live) ≠ agent memory (what persists across sessions)

- **Path Conventions** (CRITICAL for reliable agent behavior):
  - **Memory location:** `_bmad/_memory/{skillName}-sidecar/` (relative to project root)
  - **Project artifacts:** `{project-root}/_bmad/...` when referencing project-level files
  - **Skill-internal files:** Use relative paths (`resources/`, `prompts/`, `scripts/`)
  - **Config variables:** Use directly — they already contain full paths (NO `{project-root}` prefix)
    - ✅ `{output_folder}/file.md`
    - ❌ `{project-root}/{output_folder}/file.md` (double-prefix breaks resolution)
  - **No absolute paths** (`/Users/...`) or relative prefixes (`./`, `../`)

- **Testing preference:** Ask about testing interest (actual eval design happens AFTER build):
  - **HITL Evals** — Scenario-based tests simulating conversations with diverse user personas
  - **Python Tests** — Automated tests for scripts (if applicable)
  - **Skip for now** — Tests can be added later

### Phase 4: Draft & Refine

Once you have a cohesive ides, think one level deeper. Once you have done this, present a draft outline. Point out vague areas. Ask what else is needed. Iterate until they say they're ready.

### Phase 5: Build

Load field definitions and SKILL.md description format from `resources/standard-fields.md` when validating output.

When confirmed:

1. Load template substitution rules from `resources/template-substitution-rules.md` and apply

2. Create skill structure using templates from `templates/` folder:
   - **SKILL-template.md** — skill wrapper with full persona content embedded
   - **init.md** — first-run setup
   - **memory-system.md** — memory (if sidecar, saved at root level)
   - **autonomous-wake.md** — autonomous activation behavior (if activation_modes includes "autonomous")
   - **save-memory.md** — explicit memory save capability (if sidecar enabled)
   - **prompt-template.md** — each internal capability prompt

3. **Generate manifest.json** — Create a manifest.json file using `templates/manifest.json` as a template:
   - Set `bmad-type: "bmad-agent"`
   - Add `bmad-module-name`, `bmad-module-code` if part of a module (omit for standalone)
   - Populate `bmad-capabilities` array with:
     - **Internal prompts:** Each with `name` (kebab-case), `menu-code` (2-3 uppercase letters), `display-name`, `description`
     - **External skills:** Each with `name` (exact registered skill name), `menu-code`, `display-name`, `description`
   - Validate with: `python scripts/validate-manifest.py path/to/manifest.json`

4. **Folder structure** (no `assets/` folder — everything at root):
```
{skill-name}/
├── SKILL.md          # Contains full persona content (agent.md embedded)
├── resources/
│   ├── manifest.json     # bmad-capabilities with menu codes
│   └── memory-system.md  # (if sidecar needed)
├── tests/              # Created during eval design phase (after build)
│   ├── eval.json         # HITL eval scenarios
│   └── fixtures/         # Test data specific to this agent (if needed)
│       └── {organize-by-what-the-agent-needs}
├── scripts/          # python or shell scripts needed for the agent
│   └── run-tests.sh  # uvx-powered test runner (if python tests exist)
└── prompts/          # Internal capability prompts
    ├── init.md              # First-run setup
    ├── autonomous-wake.md   # Autonomous activation (if autonomous mode)
    ├── save-memory.md       # Explicit memory save (if sidecar)
    └── {name}.md            # Each internal capability prompt
```

5. Output to `bmad_builder_output_folder` from config, or `{project-root}/bmad-builder-creations/`

### Phase 6: Summary & Next Steps

Present what was built: location, structure, first-run behavior, capabilities. Ask if adjustments needed.

**Then propose Full Quality Scan:**

Ask: *"Your agent is ready! Would you like to run a Full Quality Scan to validate the structure and catch any issues before testing?"*

If yes, load `prompts/quality-optimizer.md` with `{scan_mode}=full` and the new agent path.

**Then propose testing:**

If user indicated interest in HITL evals during Phase 3, now is the time to design them. The agent exists — we can see what it actually does and design meaningful tests.

Ask: *"Now that the agent is built, would you like to design HITL eval scenarios? I'll walk through the agent's capabilities and help create comprehensive test cases."*

If yes, load `prompts/hitl-evals-design.md` and work through the eval design process systematically.

**If they want to test immediately:** After evals are designed and written, proceed to `Test Agent` section to run them.

Remind them: BMad module system compliant. Use `bmad-init` skill to integrate into a project.

## Quality Optimizer

This section covers comprehensive validation and performance optimization for existing agents. For building new agents, see `Build Process` above.

**Use Quality Optimizer for:**
- Validating agent structure and compliance with BMad standards
- Identifying template substitution errors (orphaned conditionals)
- Checking manifest schema and capability alignment
- Verifying memory system setup and access boundaries
- Optimizing for token efficiency and performance
- Security and safety validation

**Scan Modes:**

| Mode | Description | When to Use |
|------|-------------|-------------|
| **Full** | All 15 scanners, comprehensive validation | Default after build/update |
| **Error** | Critical issues that break functionality | Quick check for broken things |
| **Ideation** | Creative feedback and improvement ideas | Refinement and enhancement |
| **Efficiency** | Performance and token optimization | Speed and cost improvements |
| **Test** | Eval coverage and format validation | Test quality assessment |
| **Single** | One specific scanner (e.g., "just cohesion") | Targeted analysis |

**After Build/Update:** Always propose Full Quality Scan to catch any issues early.

**Autonomous/Headless Mode:**

Include keywords like `autonomous`, `headless`, `--autonomous`, `--headless`, `-H`, `-A`, `no-questions`, or `silent` to run without interactive prompts:

```
"Run quality optimizer on /path/to/agent in headless mode"
"Quality check --autonomous /path/to/agent"
```

In autonomous mode:
- No questions asked (proceeds with safe defaults)
- Uncommitted changes noted but don't block
- Agent functioning assumed (user should verify)
- Output is structured JSON + report file path
- No remediation offers (report only)

**Running Quality Optimizer:**

1. **Load the optimization framework**
   - Load `prompts/quality-optimizer.md` — this is the orchestrator, NOT a direct scanner

2. **Create output directory**
   - Create: `_bmad-output/{skill-name}/quality-scan/{timestamp}/`

3. **Spawn scanner subagents**
   - DO NOT read target agent files yourself — the scanner subagents will do this
   - The quality-optimizer.md orchestrator spawns parallel subagents for each scanner
   - Each scanner receives: agent path + output directory
   - Each scanner does its own file reading and analysis
   - Batches of 5 scanners run in parallel to manage context

4. **Synthesize and report**
   - After all scanners complete, collect temp JSON files
   - Spawn report creator to consolidate findings
   - Present summary to user or output structured JSON (autonomous mode)

5. **Offer remediation** (skip in autonomous mode)
   - Apply fixes directly to agent files
   - Export checklist for manual fixes
   - Rebuild using agent builder if structure needs major changes
   - Run tests after fixes to validate improvements

**CRITICAL:** Your role is coordination and synthesis, NOT file reading. Let the specialized scanner subagents do the reading and analysis.

**Note:** In autonomous mode, the scan completes and outputs the report without offering remediation.

**Validation dimensions covered:**
1. **Structural Integrity** — SKILL.md frontmatter, sections, formatting
2. **Template Substitution** — Conditional blocks applied correctly, no orphaned placeholders
3. **Manifest Validation** — Schema compliance, capability alignment
4. **Folder Structure** — Required files exist, conditional files present
5. **Memory System** — Sidecar setup, access boundaries, write discipline
6. **Activation Flow** — Config loading, first-run detection, autonomous handling
7. **Capability Alignment** — Internal prompts exist, external skills are real
8. **Performance Optimization** — Token efficiency, prompt optimization
9. **Documentation Quality** — Clarity, completeness, consistency
10. **Security & Safety** — Access control, input handling, data safety

## Test Agent

Run tests against existing agents to validate behavior and catch issues.

**When to test:**
- After building a new agent
- After making significant changes
- Before deploying to production

**Test types:**
- **HITL Evals** — Scenario-based conversation testing (load `prompts/hitl-evals-design.md` for design and execution)
- **Python Tests** — Automated tests for agent scripts (if applicable)

**The testing loop:**
1. **Build** → Create or modify the agent
2. **Eval** → Run HITL evals and/or Python tests
3. **Report** → Present findings with specific failures
4. **Improve** → Make targeted changes based on results
5. **Repeat** → Run next iteration, track progress

**Getting started:**

If no evals exist at `tests/eval.json`, offer to create them first using `prompts/hitl-evals-design.md`.

When ready to run tests, load `prompts/hitl-evals-design.md` for full execution instructions including:
- Eval validation and setup
- Scenario execution with conversation simulation
- Grading and results aggregation
- Iteration handling
