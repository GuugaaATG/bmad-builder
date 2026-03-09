# HITL Eval Design and Execution for Agents

This prompt handles both designing and running Human-In-The-Loop (HITL) evals for agents.

## Determine Your Mode

**First, check what state we're in:**

| If you're here from... | Then enter... | Because... |
|------------------------|---------------|------------|
| "design HITL evals" or "create eval scenarios" | **Design Mode** | Eval scenarios don't exist yet |
| "run tests" or "test this agent" | **Execution Mode** | Eval scenarios exist, run them |
| Unclear which mode | Ask user: "Do you want to (a) design new eval scenarios, or (b) run existing evals?" | Clarify intent |

---

## Design Mode

Use this mode when eval scenarios need to be created for an agent.

## Load Schema First

Before designing evals, load `resources/eval-schema.json` to understand the required format.

## Design Process

### Step 1: Review the Agent's Structure

Read the agent's `resources/manifest.json` and `SKILL.md` to understand:

1. **Internal Capabilities**: What can this agent do itself?
2. **External Skills**: What other skills does it invoke?
3. **Memory/Continuity**: Does it persist data across sessions?
4. **Autonomous Mode**: Does it run scheduled background tasks?
5. **Persona/Communication**: How should it communicate?

### Step 2: Design Evals by Category

For each relevant category below, create at least one scenario with a diverse persona.

#### 1. Capabilities Testing
For each internal capability in manifest.json:
- **What user input triggers this capability?**
- **What could go wrong?**
- **What does success look like?**

Design scenarios that:
- Use natural language variations to trigger the capability
- Test edge cases (empty input, malformed data, ambiguous requests)
- Verify the capability produces expected outputs
- Intercept external to agent skill calls
- Ensure capabilities (internal prompts in the agent) are tested fully - internal capabilities are mini skills so its critical they are tested

#### 2. Onboarding / First-Run
If the agent has `prompts/init.md`:
- **New user scenario**: Test first-time setup experience
  - Persona: Someone who has never used this agent before
  - Goal: Complete setup successfully
  - Success: Agent gathers needed info, user understands what was configured
- **Returning user scenario**: Verify setup is skipped on subsequent runs
  - Persona: Existing user with completed setup
  - Goal: Access agent without being asked setup questions again
  - Success: Agent recognizes existing state, proceeds directly to help

#### 3. Memory Operations
If the agent has a sidecar memory system (`resources/memory-system.md`):
- **Create scenario**: Test writing new data to memory
  - Persona: User adding new information
  - Success: Data persists and can be retrieved
- **Retrieve scenario**: Test reading existing data
  - Persona: User asking about something previously discussed
  - Success: Agent recalls relevant information accurately
- **Update scenario**: Test editing/changing existing data
  - Persona: User correcting previous information
  - Success: Agent updates memory correctly, maintains consistency

#### 4. Autonomous Mode
If activation_modes includes "autonomous":
- **Default wake behavior**: Test what happens with `--autonomous` (no specific task)
  - Persona: System or user triggering autonomous wake
  - Success: Agent performs expected default background task
- **Each named task**: Test `--autonomous:{task-name}` for each defined task
  - Persona: Context relevant to that autonomous task
  - Success: Task completes as designed, produces expected outputs

#### 5. Persona / Communication Adherence
- **Stress test**: Agent maintains personality under difficult circumstances
  - Persona: Frustrated user, ambiguous request, or conflicting constraints
  - Success: Agent stays in character while resolving the issue
- **User type adaptation**: Agent adapts to different communication styles
  - Persona: User with different expertise level or communication preference
  - Success: Agent adjusts appropriately without losing its core identity
- **Language/style adherence**: If agent has specific language requirements
  - Persona: User testing those boundaries
  - Success: Agent maintains configured language patterns

#### 6. Fixtures Needed

What test data does this agent need for realistic testing?

**Sample data in the domain**:
- Memory files, code files, configs, documents
- Representative examples the agent would process or need based on its capabilities or skills or memory

**Existing states to analyze**:
- Malformed data (edge cases, error conditions)
- Partial states (work in progress)
- Reference states (known good/bad examples)

**Reference inputs for conversion scenarios**:
- Before/after examples for transformations
- Multiple format variations

Create fixtures in `tests/fixtures/` organized by what the agent NEEDS:
```
tests/fixtures/
├── journal-entries/     # If agent processes journals
├── memory-states/       # If agent reads/writes memory
├── configs/             # If agent handles configuration
└── old-agents/          # If agent upgrades/converts old formats
```

### Step 3: Write Scenarios

For each scenario, create an entry in `tests/eval.json`:

```json
{
  "id": "unique-scenario-id",
  "name": "Human-readable scenario name",
  "description": "What this scenario tests and why it matters",
  "persona": "Detailed persona description including: age/background, communication style, expertise level, what matters to them in this interaction",
  "goal": "What the user is trying to accomplish in this interaction",
  "initial_input": "The user's first message to the agent (exactly as they would say it)",
  "max_turns": 15,
  "success_criteria": [
    "Specific, observable outcome 1",
    "Specific, observable outcome 2"
  ],
  "failure_modes": [
    "What constitutes failure (optional but recommended)"
  ],
  "fixture": "path/to/fixture-file (optional, for conversion/analysis scenarios)",
  "known_deficiencies": ["list of issues that should be found (optional, for analysis scenarios)"]
}
```

**Scenario writing tips**:
- Personas should be diverse in expertise, communication style, and context
- Initial input should be natural language, not robotic commands
- Success criteria must be observable from the conversation transcript
- Include failure modes when failure is subtle or easy to miss
- For fixtures, reference the path relative to tests/fixtures/

### Step 4: Validate

After creating evals:
```bash
python scripts/hitl_eval.py validate --eval-file tests/eval.json
```

Fix any validation errors before proceeding to run tests.

## Execution Mode

Use this mode when eval scenarios already exist at `tests/eval.json` and need to be run.

### Running HITL Evals

1. **Load and validate evals**
   - Read `tests/eval.json` from the agent being tested
   - If no evals exist, offer to create them (switch to Design Mode above)
   - Validate: `python scripts/hitl_eval.py validate --eval-file tests/eval.json`

2. **Create results directory**
   - Generate timestamp: `{YYYY-MM-DD_HH-MM-SS}`
   - Extract skill name from agent's SKILL.md frontmatter
   - Create: `_bmad-output/eval-results/{skill-name}/{timestamp}/`

3. **Run each scenario** — For each eval in the array:

   a. **Initialize**
   - Create `{results-dir}/eval-{id}-{short-uuid}/`
   - If agent produces files, create `{eval-dir}/skill-output/` subfolder

   b. **Run conversation loop**
   - Spawn Task subagent (`subagent_type="general-purpose"`) with agent's SKILL.md
   - Provide the eval's initial_input, direct file outputs to skill_output_location
   - Record each response in transcript
   - If agent asks a question, spawn UserSimulator from `agents/UserSimulator.md`
   - Continue until: `===SIMULATION_END===`, max_turns reached, or task completes

   c. **Save results**
   - Write `transcript.md`, `timing.json`
   - Spawn HITLGrader from `agents/HITLGrader.md` to evaluate against success_criteria
   - Save `grading.json`

4. **Aggregate and present**
   - Create `benchmark.json` with summary statistics
   - Generate `summary.md` with human-readable report
   - Show findings, ask if user wants to improve based on results

### Supporting Agents

Located under `agents/` in this skill:
- **UserSimulator.md** — Role-plays user personas during evals
- **HITLGrader.md** — Evaluates conversations against success criteria

### Iteration Loop

- Each run gets its own timestamped directory
- Load `feedback.json` from previous runs for context
- Track which evals started passing across runs

**Results structure:**
```
_bmad-output/
└── eval-results/
    └── {skill-name}/
        ├── feedback.json              # Carries across runs
        ├── 2025-03-07_14-30-00/       # Test run timestamp
        │   ├── eval-1-{id}-{uuid}/
        │   │   ├── skill-output/      # Files agent created
        │   │   ├── transcript.md
        │   │   ├── grading.json
        │   │   └── timing.json
        │   ├── benchmark.json
        │   └── summary.md
```

### Running Python Tests (if agent has scripts/)

If the agent includes Python scripts with tests (`scripts/run-tests.sh`), run them via Task tool:

1. Use Task with `subagent_type="Bash"`
2. Instruct: "Run the tests at {skill-path}/scripts/run-tests.sh -v and return results"
3. Capture output and report both Python and HITL results together

## After Design Mode

When evals are designed and validated:
1. Confirm location: `tests/eval.json`
2. Ask: "Evals are ready. Would you like to run them now?"
3. If yes → proceed to Execution Mode above
4. If no → return to main skill, user can run tests later

## After Execution Mode

When tests complete:
1. Present findings from `summary.md` and `benchmark.json`
2. Show which scenarios passed/failed with specific failures
3. Offer: "Would you like to improve the agent based on these results?"
4. If yes → load `prompts/quality-optimizer.md` for targeted fixes
5. Offer re-run to validate improvements
