#!/usr/bin/env python3
"""
HITL Evaluation Runner for BMad Agents

This script provides utilities for running Human-In-The-Loop evaluations
of agents using the UserSimulator and HITLGrader pattern.

Usage:
    python hitl_eval.py validate --eval-file path/to/eval.json
    python hitl_eval.py template --output path/to/eval.json
    python hitl_eval.py report --results-dir path/to/results
    python hitl_eval.py path --skill-name "my-agent"
"""

import argparse
import json
import sys
import uuid
from pathlib import Path
from datetime import datetime
from typing import Any


# JSON Schema for HITL evals
EVAL_SCHEMA = {
    "type": "object",
    "required": ["name", "description", "version", "evals"],
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "version": {"type": "string"},
        "evals": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "name", "persona", "goal", "initial_input", "success_criteria"],
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "persona": {"type": "string"},
                    "goal": {"type": "string"},
                    "initial_input": {"type": "string"},
                    "max_turns": {"type": "integer", "default": 15},
                    "success_criteria": {"type": "array", "items": {"type": "string"}},
                    "failure_modes": {"type": "array", "items": {"type": "string"}},
                }
            }
        }
    }
}


def validate_eval(eval_file: Path) -> tuple[bool, list[str]]:
    """Validate an eval.json file against the schema."""
    try:
        data = json.loads(eval_file.read_text())
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]

    errors = []

    # Check required top-level fields
    for field in ["name", "description", "version", "evals"]:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Check evals array
    if "evals" in data:
        if not isinstance(data["evals"], list):
            errors.append("'evals' must be an array")
        else:
            for i, eval_item in enumerate(data["evals"]):
                eval_prefix = f"eval[{i}]"
                if not isinstance(eval_item, dict):
                    errors.append(f"{eval_prefix}: must be an object")
                    continue

                for field in ["id", "name", "persona", "goal", "initial_input", "success_criteria"]:
                    if field not in eval_item:
                        errors.append(f"{eval_prefix}: missing required field '{field}'")

                if "success_criteria" in eval_item:
                    if not isinstance(eval_item["success_criteria"], list):
                        errors.append(f"{eval_prefix}: success_criteria must be an array")
                    elif len(eval_item["success_criteria"]) == 0:
                        errors.append(f"{eval_prefix}: success_criteria should have at least one criterion")

    return len(errors) == 0, errors


def create_template(output: Path) -> None:
    """Create a template eval.json file."""
    template = {
        "name": "Agent Name",
        "description": "Evaluation suite for the agent",
        "version": "1.0.0",
        "evals": [
            {
                "id": "scenario-1",
                "name": "descriptive-scenario-name",
                "description": "What this scenario tests",
                "persona": "Detailed persona description (age, background, communication style, what matters to them)",
                "goal": "What the user is trying to accomplish in this interaction",
                "initial_input": "The user's first message to the agent",
                "max_turns": 15,
                "success_criteria": [
                    "Specific, observable outcome 1",
                    "Specific, observable outcome 2"
                ],
                "failure_modes": [
                    "What constitutes failure (optional)"
                ]
            }
        ]
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(template, indent=2))
    print(f"Created template at: {output}")


def get_results_path(project_root: Path, skill_name: str, timestamp: str | None = None) -> Path:
    """Generate the results directory path for a test run.

    Args:
        project_root: The project root directory
        skill_name: Name of the skill being tested (from SKILL.md frontmatter)
        timestamp: Optional timestamp string. If None, generates current time.

    Returns:
        Path to the results directory: _bmad-output/eval-results/{skill-name}/{timestamp}/
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    return project_root / "_bmad-output" / "eval-results" / skill_name / timestamp


def get_eval_dir(results_path: Path, eval_id: str) -> Path:
    """Generate a unique eval directory with entropy.

    Args:
        results_path: The test run results directory
        eval_id: The scenario ID from eval.json

    Returns:
        Path like: {results_path}/eval-{id}-{short-uuid}/
    """
    short_uuid = str(uuid.uuid4())[:8]
    return results_path / f"eval-{eval_id}-{short_uuid}"


def generate_report(results_dir: Path) -> dict[str, Any]:
    """Generate a summary report from HITL evaluation results."""
    results_dir = Path(results_dir)

    # Find all eval directories
    eval_dirs = [d for d in results_dir.iterdir() if d.is_dir() and d.name.startswith("eval-")]

    if not eval_dirs:
        print(f"No eval directories found in {results_dir}")
        return {}

    # Aggregate results
    all_evals = []
    total_passed = 0
    total_failed = 0
    total_partial = 0
    turn_counts = []

    for eval_dir in sorted(eval_dirs):
        grading_file = eval_dir / "grading.json"
        if not grading_file.exists():
            print(f"Warning: No grading.json found in {eval_dir}")
            continue

        try:
            grading = json.loads(grading_file.read_text())
            all_evals.append({
                "directory": eval_dir.name,
                "grading": grading
            })

            if grading.get("passed"):
                total_passed += 1
            elif grading.get("outcome") == "partial":
                total_partial += 1
            else:
                total_failed += 1

            turn_counts.append(grading.get("turns", 0))

        except json.JSONDecodeError as e:
            print(f"Warning: Invalid grading.json in {eval_dir}: {e}")

    # Calculate summary
    total_evals = len(all_evals)
    pass_rate = total_passed / total_evals if total_evals > 0 else 0
    avg_turns = sum(turn_counts) / len(turn_counts) if turn_counts else 0

    # Load existing benchmark or create new
    benchmark_file = results_dir / "benchmark.json"
    if benchmark_file.exists():
        benchmark = json.loads(benchmark_file.read_text())
    else:
        benchmark = {
            "iteration": 1,
            "agent_name": "unknown",
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "evals": []
        }

    # Update benchmark
    benchmark["summary"] = {
        "total_evals": total_evals,
        "passed": total_passed,
        "partial": total_partial,
        "failed": total_failed,
        "pass_rate": pass_rate,
        "avg_turns": avg_turns
    }
    benchmark["evals"] = [
        {
            "id": eval_item["directory"],
            "passed": eval_item["grading"].get("passed", False),
            "outcome": eval_item["grading"].get("outcome", "unknown"),
            "turns": eval_item["grading"].get("turns", 0),
            "criteria_scores": eval_item["grading"].get("criteria_evaluation", {})
        }
        for eval_item in all_evals
    ]

    # Write updated benchmark
    benchmark_file.write_text(json.dumps(benchmark, indent=2))

    # Generate markdown summary
    summary = f"""# HITL Evaluation Report

## Summary

- **Total Evals**: {total_evals}
- **Passed**: {total_passed}
- **Partial**: {total_partial}
- **Failed**: {total_failed}
- **Pass Rate**: {pass_rate:.1%}
- **Avg Turns**: {avg_turns:.1f}

## Results by Scenario

"""
    for eval_item in all_evals:
        name = eval_item["directory"]
        grading = eval_item["grading"]
        status = "✅" if grading.get("passed") else "⚠️" if grading.get("outcome") == "partial" else "❌"
        summary += f"### {status} {name}\n\n"
        summary += f"- **Turns**: {grading.get('turns', 0)}\n"
        summary += f"- **Outcome**: {grading.get('outcome', 'unknown')}\n\n"

        # Add criteria details if available
        if "criteria_evaluation" in grading:
            for criterion in grading["criteria_evaluation"]:
                criterion_status = "✓" if criterion.get("met") else "✗"
                summary += f"  - {criterion_status} {criterion.get('criterion', 'No criterion')}\n"

        summary += "\n"

        # Add observations
        if "observations" in grading and grading["observations"]:
            summary += "**Observations:**\n"
            for obs in grading["observations"]:
                summary += f"- {obs}\n"
            summary += "\n"

    # Write summary markdown
    summary_file = results_dir / "summary.md"
    summary_file.write_text(summary)

    print(f"\nReport generated:")
    print(f"  Benchmark: {benchmark_file}")
    print(f"  Summary: {summary_file}")

    return benchmark


def main():
    parser = argparse.ArgumentParser(description="HITL evaluation utilities")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate an eval.json file")
    validate_parser.add_argument("--eval-file", required=True, help="Path to eval.json")

    # Template command
    template_parser = subparsers.add_parser("template", help="Create a template eval.json")
    template_parser.add_argument("--output", default="eval.json", help="Output path for template")

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate evaluation report")
    report_parser.add_argument("--results-dir", required=True, help="Path to test run results directory")

    # Path command - generate results directory path
    path_parser = subparsers.add_parser("path", help="Generate results directory path for a test run")
    path_parser.add_argument("--skill-name", required=True, help="Name of the skill being tested")
    path_parser.add_argument("--timestamp", help="Timestamp (default: current time)")
    path_parser.add_argument("--project-root", default=".", help="Project root directory (default: cwd)")

    args = parser.parse_args()

    if args.command == "validate":
        valid, errors = validate_eval(Path(args.eval_file))
        if valid:
            print(f"✅ {args.eval_file} is valid")
            return 0
        else:
            print(f"❌ {args.eval_file} has errors:")
            for error in errors:
                print(f"  - {error}")
            return 1

    elif args.command == "template":
        create_template(Path(args.output))
        return 0

    elif args.command == "report":
        generate_report(Path(args.results_dir))
        return 0

    elif args.command == "path":
        results_path = get_results_path(Path(args.project_root), args.skill_name, args.timestamp)
        print(f"Results directory: {results_path}")

        # Also show example eval directory
        example_eval_dir = get_eval_dir(results_path, "scenario-1")
        print(f"Example eval directory: {example_eval_dir}")
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
