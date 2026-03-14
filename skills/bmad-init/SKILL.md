---
name: bmad-init
description: Initialize BMad project configuration and load config variables. Use when any skill needs module-specific configuration values, or when setting up a new BMad project.
argument-hint: "[--module=module_code] or [--all]"
---

## Overview

This skill is the entry point for all BMad configuration. It has two modes:

- **Fast path**: Config exists and the requested module is configured — returns vars as JSON. Done.
- **Init path**: Config is missing or the requested module isn't set up — walks the user through configuration, writes config files, then returns vars.

Every BMad skill should call this skill on activation to get its config vars. The caller never needs to know whether init happened — they just get their config back.

## On Activation — Fast Path

Run the loader script. If a module code was provided by the calling skill or user, include it. Otherwise core vars are returned.

```bash
uv run scripts/bmad_init.py load --module {module_code} --all --project-root {project-root}
```

Or for core only (no module specified):

```bash
uv run scripts/bmad_init.py load --all --project-root {project-root}
```

**If the script returns JSON vars** — store them as `{var-name}` and continue. The skill is done.

**If the script returns an error or `init_required`** — proceed to `prompts/init-setup.md`

## Plugin Manifest Convention

Plugins that need config questions ship a manifest skill: `bmad-get-manifest-{module_code}`

The manifest skill contains `resources/manifest.json` with the module's questions, intro/outro messages, defaults, and directory declarations. See `bmad-get-manifest-bmm` for an example.
