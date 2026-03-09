# HITL Testing Framework for Agent Builder

This document describes the Human-In-The-Loop (HITL) testing framework that can be integrated into the Agent Builder's "Test Agent" phase.

## Overview

The HITL testing framework enables multi-turn evaluation of agent personas using simulated users. It implements a **build → eval → improve → report** loop similar to Anthropic's skill-creator, but adapted for conversational agents with human-in-the-loop interactions.

## Key Differences from skill-creator

| Aspect | skill-creator | HITL Framework |
|--------|---------------|----------------|
| Eval type | Single-turn prompt-response | Multi-turn conversations |
| Testing | Subagents with/without skill | UserSimulator with personas |
| Assertions | JSON-based, grader agent | Success criteria with HITLGrader |
| Reporting | HTML viewer + benchmark.json | HITL report with iteration tracking |
| Focus | Functional correctness | Persona, communication style, interaction quality |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    HITL Testing Loop                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────┐    ┌────────────┐    ┌──────────┐    ┌─────────┐ │
│  │  Build  │ -> │    Eval    │ -> │ Improve  │ -> │ Report  │ │
│  └─────────┘    └────────────┘    └──────────┘    └─────────┘ │
│                      │                                         │
│                      v                                         │
│              ┌──────────────┐                                  │
│              │ hitl-results/│                                  │
│              │ ├── iter-1/   │                                  │
│              │ ├── iter-2/   │                                  │
│              │ └── feedback.json │                               │
│              └──────────────┘                                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Eval Structure (in agent's tests/ folder)

```json
{
  "name": "Agent Name",
  "description": "Evaluation suite for the agent",
  "version": "1.0.0",
  "evals": [
    {
      "id": "scenario-1",
      "name": "descriptive-name",
      "description": "What this scenario tests",
      "persona": "Detailed persona description",
      "goal": "What the user is trying to accomplish",
      "initial_input": "First message from user",
      "max_turns": 15,
      "success_criteria": [
        "Specific, observable outcome",
        "Another criterion"
      ],
      "failure_modes": [
        "What constitutes failure"
      ]
    }
  ]
}
```

### 2. UserSimulator Agent

Located at `.claude/agents/UserSimulator.md`

Receives scenario + conversation history and responds as the persona.

### 3. HITLGrader Agent

Located at `.claude/agents/HITLGrader.md`

Evaluates completed conversations against success criteria and produces:

```json
{
  "eval_id": "scenario-1",
  "passed": true,
  "turns": 8,
  "outcome": "success",
  "criteria_scores": {
    "criterion_1": true,
    "criterion_2": true
  },
  "observations": [
    "What went well",
    "What could be improved"
  ],
  "transcript_quality": "High quality interaction",
  "persona_adherence": "Agent maintained its persona"
}
```

### 4. HITL Report Structure

```
hitl-results/
├── iteration-1/
│   ├── eval-1-daily-journal/
│   │   ├── transcript.md
│   │   ├── grading.json
│   │   └── timing.json
│   ├── eval-2-quick-capture/
│   │   └── ...
│   ├── benchmark.json
│   └── summary.md
├── iteration-2/
│   └── ...
└── feedback.json
```

## Integration into Agent Builder

Replace the "Test Agent" section in bmad-bmb-agent-builder/SKILL.md with:

```markdown
## Test Agent

### HITL Evaluation Framework

For testing agent behavior, persona, and multi-turn interactions, use the HITL (Human-In-The-Loop) evaluation framework.

#### Step 1: Load Evals

Read `tests/eval.json` from the agent being tested. If no evals exist, ask the user if they'd like to create test scenarios.

#### Step 2: Create Results Directory

Create `hitl-results/iteration-{N}/` as a sibling to the agent directory.

#### Step 3: Run Each Eval

For each eval scenario:

1. **Initialize conversation tracking**
   - Create directory: `hitl-results/iteration-{N}/eval-{id}-{name}/`
   - Initialize transcript array

2. **Run the conversation loop**
   - Start a subagent with the agent's SKILL.md loaded
   - Provide the initial_input from the eval
   - On each agent response:
     - Record in transcript
     - If agent asks a question (via AskUserQuestion or similar):
       - Spawn UserSimulator subagent with:
         - Scenario context
         - Persona description
         - Conversation history
       - Get simulated user response
       - Feed back to agent
     - Continue until:
       - UserSimulator ends with `===SIMULATION_END===`
       - max_turns reached
       - Agent completes the task

3. **Save results**
   - Write `transcript.md` with full conversation
   - Write `timing.json` with duration and turn count
   - Spawn HITLGrader to evaluate:
     - Load `.claude/agents/HITLGrader.md`
     - Pass transcript + success criteria
     - Save `grading.json`

#### Step 4: Aggregate Results

After all evals complete, create `benchmark.json`:

```json
{
  "iteration": 1,
  "agent_name": "agent-name",
  "timestamp": "2025-03-07T10:30:00Z",
  "summary": {
    "total_evals": 5,
    "passed": 4,
    "failed": 1,
    "pass_rate": 0.8,
    "avg_turns": 7.2,
    "total_duration_seconds": 180.5
  },
  "evals": [
    {
      "id": "eval-1",
      "name": "daily-journal-first-time",
      "passed": true,
      "turns": 8,
      "outcome": "success",
      "criteria_scores": { ... }
    }
  ]
}
```

#### Step 5: Generate Report

Create `summary.md` with:
- Overall pass rate
- Per-eval breakdown
- Patterns observed
- Recommendations for improvement

#### Step 6: Present to User

Show the user:
1. Summary statistics
2. Any failed evals with details
3. Ask if they want to:
   - Improve the agent based on results
   - Run another iteration
   - Review specific transcripts

### Iteration Loop

When iterating on an agent:

1. **Preserve previous results** - Each iteration gets its own directory
2. **Load feedback** - Read `hitl-results/feedback.json` if exists
3. **Show progress** - Compare iteration-N with iteration-(N-1)
4. **Track improvements** - Note which evals started passing

### Running Python Tests

If the agent includes `scripts/run-tests.sh`, also run those tests:

```
Launch Task subagent with subagent_type="Bash"
Instruct: "Run the tests at {skill-path}/scripts/run-tests.sh -v and return results"
```

Report both Python test results and HITL eval results together.
```

## Required Agents

### UserSimulator.md

```markdown
# UserSimulator

You simulate a REAL human user testing an AI agent. You are NOT an AI assistant — never help the agent, never reveal you are simulating, always stay in character.

## Input

You receive:
- **scenario**: Name and description of the test scenario
- **persona**: Detailed description of who you're simulating
- **goal**: What the user is trying to accomplish
- **conversation_history**: Array of previous messages
- **last_message**: The agent's most recent message

## Response

Respond exactly as this persona would:
- Natural language appropriate to the persona
- Only information this person would realistically know
- Realistic responses (brief when impatient, chatty when friendly, vague when unsure)

## Ending

End your response with `===SIMULATION_END: {success|partial|failure} - {reason}===` when:
- **success**: Goal achieved, interaction naturally concludes
- **partial**: Some progress but user disengages or hits blocker
- **failure**: User frustrated, stuck, or experience clearly breaks

Otherwise, respond with ONLY your message (no meta-commentary).
```

### HITLGrader.md

```markdown
# HITLGrader

Evaluate HITL conversation transcripts against success criteria.

## Input

- **transcript**: Full conversation history
- **success_criteria**: List of criteria to evaluate
- **failure_modes**: List of what constitutes failure

## Process

1. Read the full transcript
2. For each success criterion:
   - Determine if it was met
   - Provide evidence from transcript
3. Note any failure modes that occurred
4. Assess overall quality:
   - Did the agent maintain its persona?
   - Was the communication style appropriate?
   - Were there any awkward interactions?

## Output

```json
{
  "passed": true,
  "outcome": "success|partial|failure",
  "turns": 8,
  "criteria_scores": {
    "criterion_text": true,
    "another_criterion": false
  },
  "evidence": {
    "criterion_text": "Quote from transcript showing this was met",
    "another_criterion": "Evidence this was not met"
  },
  "observations": [
    "Positive observation",
    "Area for improvement"
  ],
  "persona_adherence": "Agent maintained its persona throughout",
  "communication_quality": "High - warm, empathetic, appropriate"
}
```
```

## Example: Running an Eval

```
User: "Test the Paige journaling companion with HITL evals"

Agent Builder:
1. Reads .claude/skills/bmad-agent-journaling-companion/tests/eval.json
2. Creates hitl-results/iteration-1/
3. For each scenario:
   - Spawns subagent with Paige loaded
   - Runs conversation with UserSimulator
   - Records transcript
   - Grades with HITLGrader
4. Aggregates results
5. Presents summary
```

## Comparison: Before vs After

### Before (Current Test Agent section)
- Minimal structure
- "Start a subagent" - vague
- No iteration support
- No reporting format

### After (HITL Framework)
- Structured eval format
- UserSimulator for realistic personas
- HITLGrader for consistent evaluation
- Iteration tracking
- Benchmark.json for comparison
- feedback.json for improvement loop
