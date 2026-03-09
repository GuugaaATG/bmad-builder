# Init Path — First-Time Setup

When config is missing or a module isn't configured yet, run the init flow. Use the AskUserQuestions tool if available. If not, just ask the questions in a way that gives the user numbered choices when there are options. if its free text, then obviously they can enter anything. if its a boolean, offer it like `Enter [T]rue or [F]alse`. But the preference would be the AskUserQuestions tool.

### Step 1: Check what needs setup

```bash
uv run {skill-path}/scripts/bmad_init.py check --module {module_code} --project-root {project-root}
```

The response tells you what's needed:

- `"status": "init_required"` — No config exists. Core questions and discovered plugins are included in the response.
- `"status": "module_missing"` — Config exists but the requested module isn't set up. Discovered plugins are included.
- `"status": "no_project"` — Can't find project root. Ask user to confirm the project path.
- `"status": "ready"` — Config is fine (shouldn't get here if fast path failed, but handle gracefully).

### Step 2: Ask core questions (if init_required)

The check response includes `core_questions` loaded from the script's `module.json` manifest, with prompts, defaults, and user-setting flags. Also includes `core_intro` and `core_outro` messages.

1. Show the `core_intro` message to the user
2. For each question in `core_questions`, present the prompt and default. For `single_select` questions, show the options. Let the user accept the default or provide a value.
3. Show the `core_outro` message

### Step 3: Ask module questions (if module was requested)

If a specific module was requested and its manifest skill exists (`bmad-get-manifest-{module_code}`), resolve its defaults using the core answers:

```bash
uv run {skill-path}/scripts/bmad_init.py resolve-defaults --module {module_code} --answers '{core_answers_json}' --project-root {project-root}
```

The response includes the module's `intro`, `outro`, and `questions` with resolved defaults.

1. Show the module's `intro` message
2. For each question, present the prompt with the resolved default. For `single_select` questions, show the options.
3. Show the module's `outro` message

### Step 4: Write config

Collect all answers and write them:

```bash
uv run {skill-path}/scripts/bmad_init.py write --answers '{all_answers_json}' --project-root {project-root} --create-dirs
```

The `--answers` JSON format — use the question keys and `user_setting` flags exactly as returned by the `check` and `resolve-defaults` commands:

```json
{
  "core": {
    "<var_name>": {"value": "<user_answer>", "user_setting": <from_question_def>},
    ...
  },
  "<module_code>": {
    "<var_name>": {"value": "<user_answer>", "user_setting": <from_question_def>},
    ...
  }
}
```

Variables with `"user_setting": true` go to `_bmad/user-config.yaml` (git-ignored). Others go to `_bmad/config.yaml` (committed).

### Step 5: Return vars

After writing, run the fast-path loader again to return the resolved vars to the calling skill:

```bash
uv run {skill-path}/scripts/bmad_init.py load --module {module_code} --all --project-root {project-root}
```

## Full Init (User-Invoked)

When the user calls `bmad-init` directly without a module argument, run a full project setup:

1. Run `check` with no module
2. Ask core questions
3. The check response includes `discovered_plugins` — for each discovered plugin, run `resolve-defaults` and ask those questions too
4. Write all answers at once
5. Confirm setup is complete

## Loading Specific Variables

Skills can request specific variables instead of all:

```bash
uv run {skill-path}/scripts/bmad_init.py load --module bmm --vars project_name,planning_artifacts:default/path --project-root {project-root}
```

Variables with `:default` use that value if not found in config. Variables without a default return `null` if missing.

## Config Files

- **`_bmad/config.yaml`** — Project settings, safe to commit to version control
- **`_bmad/user-config.yaml`** — User-specific settings, should be git-ignored

Both use the same structure:

```yaml
modules:
  core:
    config:
      document_output_language: English
      output_folder: "{project-root}/_bmad-output"
  bmm:
    config:
      project_name: My Project
```
