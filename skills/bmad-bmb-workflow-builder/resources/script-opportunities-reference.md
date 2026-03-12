# Script Standards Reference

Standards for validation and utility scripts in BMad skills. Existing lint scripts (`scan-path-standards.py`, `scan-scripts.py`) and pre-pass scripts follow these patterns.

## Core Principle

Scripts handle deterministic operations (validate, transform, count). Prompts handle judgment (interpret, classify, decide). If a check has clear pass/fail criteria, it belongs in a script.

## Script Output Standard

All scripts output structured JSON:

```json
{
  "script": "script-name",
  "version": "1.0.0",
  "skill_path": "/path/to/skill",
  "timestamp": "2025-03-08T10:30:00Z",
  "status": "pass|fail|warning",
  "findings": [
    {
      "severity": "critical|high|medium|low|info",
      "category": "category-name",
      "location": {"file": "SKILL.md", "line": 42},
      "issue": "Clear description",
      "fix": "Specific action to resolve"
    }
  ],
  "summary": {
    "total": 0,
    "critical": 0, "high": 0, "medium": 0, "low": 0
  }
}
```

## Implementation Checklist

When creating new validation scripts:

- `--help` for documentation
- Accepts skill path as argument
- `-o` flag for output file (defaults to stdout)
- Diagnostics to stderr
- Exit codes: 0=pass, 1=fail, 2=error
- Self-contained (PEP 723 for Python)
- No interactive prompts
- No network dependencies
