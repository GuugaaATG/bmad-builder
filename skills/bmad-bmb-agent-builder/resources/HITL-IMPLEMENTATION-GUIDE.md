# HITL Testing Framework - Implementation Guide

## Overview

This framework adds Human-In-The-Loop (HITL) testing capabilities to the BMad Agent Builder, enabling **build → eval → improve → report** loops for conversational agents with multi-turn interactions.

## What's Included

| File | Purpose |
|------|---------|
| `.claude/agents/UserSimulator.md` | Agent that role-plays user personas during evals |
| `.claude/agents/HITLGrader.md` | Agent that evaluates conversations against success criteria |
| `resources/hitl-testing-framework.md` | Full framework documentation |
| `scripts/hitl_eval.py` | CLI utilities for validation and reporting |

## Quick Start

### 1. Create Evals for Your Agent

Add `tests/eval.json` to your agent:

```json
{
  "name": "My Agent",
  "description": "Evaluation suite",
  "version": "1.0.0",
  "evals": [
    {
      "id": "scenario-1",
      "name": "new-user-onboarding",
      "persona": "Jamie, 28, new to this tool, excited but needs guidance",
      "goal": "Successfully complete first task",
      "initial_input": "Hi, I want to try this",
      "max_turns": 12,
      "success_criteria": [
        "User completes the task",
        "User feels supported (not frustrated)",
        "Agent maintains its persona"
      ]
    }
  ]
}
```

### 2. Run HITL Evaluation

When using Agent Builder, choose "Test Agent" and specify HITL mode. The builder will:
1. Load your agent's eval.json
2. Run each scenario with UserSimulator
3. Grade results with HITLGrader
4. Generate benchmark report

### 3. Iterate and Improve

Review the results:
- `hitl-results/iteration-1/summary.md` - Human-readable summary
- `hitl-results/iteration-1/benchmark.json` - Machine-readable results
- `hitl-results/feedback.json` - Feedback for next iteration

Make improvements to your agent based on findings, then run again.

## Integration with Agent Builder

To add HITL testing to `bmad-bmb-agent-builder`, replace the "Test Agent" section in SKILL.md with the content from `resources/hitl-testing-framework.md`.

## CLI Utilities

```bash
# Validate an eval.json
python scripts/hitl_eval.py validate --eval-file path/to/eval.json

# Create a template
python scripts/hitl_eval.py template --output path/to/eval.json

# Generate report from results
python scripts/hitl_eval.py report --results-dir hitl-results/iteration-1
```

## Comparison: skill-creator vs HITL Framework

| Aspect | skill-creator | HITL Framework |
|--------|---------------|----------------|
| **Eval type** | Single-turn | Multi-turn conversations |
| **Testing** | With/without skill subagents | UserSimulator with personas |
| **Assertions** | JSON-based | Success criteria |
| **Grading** | Grader agent | HITLGrader agent |
| **Reporting** | HTML viewer | Markdown + JSON |
| **Iteration** | feedback.json | feedback.json |
| **Best for** | Skills, tools, workflows | Agents, personas, conversations |

## Example: Full Eval Run

```
User: "Test the Paige journaling companion with HITL"

Agent Builder:
1. Loading evals from tests/eval.json...
   Found 8 scenarios

2. Running HITL iteration 1...
   [1/8] daily-journal-first-time
   └─ Running conversation with UserSimulator...
   └─ Grading with HITLGrader...
   └─ Result: ✅ PASS (8 turns)

   [2/8] quick-capture-minimal
   └─ Running conversation...
   └─ Result: ✅ PASS (2 turns)

   ...

3. Generating report...
   └─ Pass rate: 87.5% (7/8 passed)
   └─ Avg turns: 6.4

4. Summary:
   ✅ daily-journal-first-time
   ✅ quick-capture-minimal
   ⚠️ search-and-find (partial: user got results but format unclear)
   ✅ never-write-for-me
   ...

Review full results in: hitl-results/iteration-1/summary.md

Would you like to improve the agent based on these results?
```

## File Structure After Evaluation

```
my-agent/
├── SKILL.md
├── tests/
│   └── eval.json              # Eval scenarios
└── (other agent files)

hitl-results/                    # Created during testing
├── iteration-1/
│   ├── eval-1-daily-journal/
│   │   ├── transcript.md       # Full conversation
│   │   ├── grading.json        # HITLGrader results
│   │   └── timing.json         # Duration, turns
│   ├── eval-2-quick-capture/
│   │   └── ...
│   ├── benchmark.json          # Aggregated results
│   └── summary.md              # Human-readable report
├── iteration-2/
│   └── ...
└── feedback.json               # User feedback for iteration
```

## Design Decisions

### Why Personas Instead of Fixed Responses?

Real users have diverse communication styles. Testing with personas (Sarah the eager beginner, Alex the impatient expert) catches issues that fixed responses miss.

### Why Grading Agent Instead of Automated Tests?

Conversational quality is hard to parse automatically. HITLGrader can assess nuance like "agent was supportive" better than regex on output.

### Why Separate UserSimulator Agent?

- Reusability: Same simulator works for any agent
- Isolation: Simulator doesn't see agent's internal state
- Consistency: Same persona across multiple evals

## Next Steps

1. **Integrate into Agent Builder**: Add the HITL testing section to bmad-bmb-agent-builder/SKILL.md
2. **Add Evals to Paige**: Convert tests/eval.json to HITL format
3. **Run First Evaluation**: Test the framework end-to-end
4. **Refine Based on Results**: Improve personas, criteria, and grading
