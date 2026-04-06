# Changelog

## [1.5.0] - 2026-04-06

### 💥 Breaking Changes

* **Agent builder output structure** — Builder now produces three distinct agent types (stateless, memory, autonomous) with different scaffolding per type. Stateless agents retain the familiar full-identity SKILL.md; memory and autonomous agents use a lean bootloader with sanctum architecture
* **bmad- prefix reserved** — The `bmad-` prefix is now reserved for official BMad ecosystem skills only. User-created skills use `agent-{name}` (standalone) or `{code}-agent-{name}` (module). Convert mode preserves existing prefixes unless the user requests a rename

### 🎁 Features

* **Agent personalization architecture** — Three agent types along a spectrum: stateless (no memory), memory (sanctum with First Breath initialization), and autonomous (memory + PULSE for background operation). Builder detects the right type through natural conversation during Phase 1
* **Sanctum memory system** — Memory agents persist through six core files (INDEX, PERSONA, CREED, BOND, MEMORY, CAPABILITIES) loaded on every session rebirth. Two-tier memory: raw session logs for capture, curated MEMORY.md (capped at 200 lines) for long-term knowledge
* **First Breath initialization** — Two styles for agent onboarding: calibration (deep conversational discovery for creative partners) and configuration (efficient guided setup for domain experts). Saves to sanctum files during the conversation, not in batch
* **PULSE autonomous wake** — Autonomous agents wake on schedule to curate memory, prune old session logs, and run domain-specific tasks. Supports named task routing via `--headless {task-name}`
* **Evolvable capabilities** — Memory agents can optionally learn new capabilities over time. Users teach the agent new prompt-based, script-based, or multi-file capabilities that persist in the sanctum
* **Template processing script** — New `process-template.py` for parameterized sanctum template seeding with agent type conditionals and init script parameters
* **New sample agents** — bmad-agent-creative-muse (memory, calibration), bmad-agent-code-coach (autonomous), bmad-agent-sentinel (autonomous), bmad-agent-diagram-reviewer (stateless)

### 🐛 Bug Fixes

* Fix quality scanner false positives on memory agents — prepass now detects bootloader architecture via Sacred Truth markers and sanctum templates, outputs `is_memory_agent` flag for all five LLM scanners
* Fix report creator for bootloader agents — reads identity seed and CREED philosophy from sanctum templates instead of missing SKILL.md sections
* Fix naming validation in workflow builder — remove enforced `bmad-` prefix check that rejected valid user-created skill names

### ♻️ Refactoring

* Move builder process and quality scan files into `references/` subdirectory for both agent and workflow builders
* Unify agent memory terminology — replace "sidecar" with direct memory references across all builders, docs, and samples. Memory path convention updated from `{skillName}-sidecar/` to `{skillName}/` for new builds
* Restructure builder discovery phases for agent type awareness with new sequencing: type detection, relationship depth, evolvable capabilities, full memory requirements

### 📚 Documentation

* New explanation doc: "Agent Memory and Personalization" covering sanctum architecture, First Breath, two-tier memory, PULSE, and evolvable capabilities
* Rewrite "What Are BMad Agents" for the three agent types with comparison tables and decision guidance
* Expand "Builder Commands Reference" with agent type detection in Phase 1, persona memory requirements in Phase 2-3, and per-type build output structures
* Add installer coming-soon notices — manual copy instructions as current path, BMad installer as upcoming
* Update module docs to reference agent type spectrum and new naming conventions
* Add module contribution guide with ecosystem cross-links

### 🔧 Maintenance

* Bump version to 1.5.0 across package.json and marketplace.json
* Update docs theme to Ghost blog design tokens (Inter/Space Grotesk/JetBrains Mono, dark palette)
* Add Python 3.10+ and `uv` as documented prerequisites

## [1.4.0] - 2026-03-29

### 🎁 Features

* **Standalone self-registering modules** — Single-skill modules no longer need a dedicated `-setup` skill. The Module Builder auto-detects single vs multi-skill input and embeds registration directly in the skill via `assets/module-setup.md`. First-run init hooks into existing agent memory detection for a unified setup experience
* **Module Builder skill** — New `bmad-module-builder` with three capabilities: Ideate Module (IM) for creative brainstorming, Create Module (CM) for scaffolding both standalone and multi-skill modules, and Validate Module (VM) for structural and quality validation with `--headless` CI support
* **BMB Setup skill** — Extracted and regenerated as `bmad-bmb-setup` using the Module Builder itself. Manages config.yaml, config.user.yaml, and module-help.csv with anti-zombie merge pattern and legacy migration
* **Workflow Convert capability (CW)** — One-command skill modernization via `--convert <path-or-url>`. Produces a clean BMad-compliant equivalent with an interactive HTML before/after comparison report including token metrics, categorized changes, and dark/light mode
* **Script creation standards** — Formalized Python-first policy with PEP 723 metadata, cross-platform portability via `uv run`, and explicit user approval for external dependencies

### 🐛 Bug Fixes

* Fix HTML quality report data injection — template used `const RAW` but generator looked for `const DATA`, causing broken report rendering in both builders
* Fix merge-help-csv.py HEADER schema — synced from 15 columns to canonical 13-column schema, preventing silent CSV corruption during module setup
* Fix `{project-root}` path validation overcorrection — scanner incorrectly rejected valid project-scope paths like `{project-root}/docs/report.md`
* Add bmad-module-builder to marketplace.json — skill was merged but not registered in the plugin manifest

### ♻️ Refactoring

* **Outcome-driven builder overhaul** — Reframe both builders around discovery-first design: existing skill input treated as reference material, 3-way routing (Analyze/Edit/Rebuild), pruning check in Phase 4, "Quality Optimizer" renamed to "Quality Analysis". Net 44% token reduction in Workflow Builder Phase 5 context
* **Ideation restructured into 7 phases** — Module identity locked in Phase 1, new Phase 6 capability review with user, mandatory config section, self-contained skill briefs, writing discipline (raw ideas in phases 1-2, structured from phase 3+)
* Consolidate plugin.json metadata into marketplace.json — single source of truth for plugin metadata
* Remove npm publishing pipeline — distribution now via `.claude-plugin/` manifest

### 📚 Documentation

* **Comprehensive docs overhaul** — Quick start guide with `bmad-bmb-setup` registration, full 13-column CSV guide explaining how `bmad-help` uses each column, "Distribution: Plugins and Marketplaces" section covering 43+ skills platforms, standalone vs multi-skill patterns throughout all docs
* Add personal-use guidance — users can copy skill folders directly to their tool's skills directory without module packaging
* Remove deprecated bmad-init references from workflow-patterns docs
* New explanation doc: Scripts in Skills — design patterns for deterministic scripting

### 🔧 Maintenance

* Bump version to 1.4.0 across package.json and marketplace.json
* Remove npm release scripts and publishConfig from package.json

## [1.1.0] - 2026-03-19

### Changed

- Flatten skill folder structure to align with Agent Skills spec
- Replace bmad-init dependency with direct config loading
- Optimize workflow-builder and agent-builder skills

### Improved

- Optimizer now captures all fragments in report and produces a final HTML report

### Removed

- Obsolete sample files from old skill structure
- Unneeded images from project root

## [1.0.0] - 2026-03-15

### Release

First official v1 release of BMad Builder — a standard skill-compliant factory for creating BMad Agents, Workflows, and Modules.
The module specific skill is coming soon pending alignment on final format with skill transition.
