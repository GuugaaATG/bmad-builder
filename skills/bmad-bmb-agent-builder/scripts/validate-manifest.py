#!/usr/bin/env python3
"""Validate BMad manifest.json against the schema.

This script validates a manifest.json file against the BMad manifest schema.
It follows PEP 723 for inline script metadata and supports structured JSON output.
"""

# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "jsonschema>=4.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft7Validator, ValidationError
except ImportError:
    print("Error: jsonschema is required. Install with: pip install jsonschema", file=sys.stderr)
    sys.exit(2)


def load_schema(schema_path: Path) -> dict[str, Any]:
    """Load the JSON schema file."""
    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}", file=sys.stderr)
        sys.exit(2)
    with schema_path.open() as f:
        return json.load(f)


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load the manifest.json file."""
    if not manifest_path.exists():
        print(f"Error: Manifest file not found: {manifest_path}", file=sys.stderr)
        sys.exit(2)
    with manifest_path.open() as f:
        return json.load(f)


def validate_manifest(manifest: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate manifest against schema and return list of errors."""
    validator = Draft7Validator(schema)
    errors = []

    for error in validator.iter_errors(manifest):
        errors.append({
            "path": ".".join(str(p) for p in error.path) if error.path else "root",
            "message": error.message,
            "type": error.validator,
        })

    return errors


def validate_capability(capability: dict[str, Any], index: int) -> list[str]:
    """Validate a single capability has required fields."""
    warnings = []
    name = capability.get("name", f"<capability-{index}>")

    # Check for menu-code
    if "menu-code" not in capability:
        warnings.append(f"Capability '{name}' is missing 'menu-code'")

    # Check display-name and description
    if "display-name" not in capability:
        warnings.append(f"Capability '{name}' is missing 'display-name'")

    if "description" not in capability:
        warnings.append(f"Capability '{name}' is missing 'description'")

    # Validate menu-code format if present
    if "menu-code" in capability:
        menu_code = capability["menu-code"]
        if not isinstance(menu_code, str) or len(menu_code) < 2 or len(menu_code) > 3:
            warnings.append(f"Capability '{name}' has invalid menu-code '{menu_code}' (must be 2-3 uppercase letters)")
        elif not menu_code.isupper():
            warnings.append(f"Capability '{name}' has invalid menu-code '{menu_code}' (must be uppercase)")

    return warnings


def print_results(errors: list[dict[str, Any]], warnings: list[str], json_output: bool) -> None:
    """Print validation results."""
    result = {
        "valid": len(errors) == 0,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }

    if json_output:
        print(json.dumps(result, indent=2))
    else:
        if result["valid"]:
            print("✓ Manifest is valid")
        else:
            print(f"✗ Manifest validation failed with {result['error_count']} error(s)", file=sys.stderr)

        if warnings:
            print(f"\nWarnings ({len(warnings)}):", file=sys.stderr)
            for warning in warnings:
                print(f"  - {warning}", file=sys.stderr)

        if errors:
            print("\nErrors:", file=sys.stderr)
            for error in errors:
                print(f"  [{error['path']}] {error['message']}", file=sys.stderr)

    sys.exit(0 if result["valid"] else 1)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate BMad manifest.json against schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "manifest",
        type=Path,
        help="Path to manifest.json file to validate",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).parent / "manifest-schema.json",
        help="Path to manifest schema JSON (default: ./manifest-schema.json)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    args = parser.parse_args()

    # Load schema and manifest
    schema = load_schema(args.schema)
    manifest = load_manifest(args.manifest)

    # Validate against schema
    errors = validate_manifest(manifest, schema)

    # Additional capability validation
    warnings = []
    capabilities = manifest.get("bmad-capabilities", [])
    for i, capability in enumerate(capabilities):
        warnings.extend(validate_capability(capability, i))

    # Print results
    print_results(errors, warnings, args.json)
    return 0


if __name__ == "__main__":
    main()
