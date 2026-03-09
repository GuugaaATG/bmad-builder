# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///

#!/usr/bin/env python3
"""
BMad Init — Project configuration bootstrap and config loader.

Dual-purpose skill script:
  1. Fast path: Config exists → return vars as JSON (replaces bmad-load-config-vars)
  2. Init path: Config missing → return questions for LLM to ask user

Config files:
  - _bmad/config.yaml (project settings, version controlled)
  - _bmad/user-config.yaml (user settings, git-ignored)

Legacy support:
  - _bmad/config/modules-project-config.yaml
  - _bmad/config/modules-user-config.yaml

Usage:
  # Fast path — load vars (default when no subcommand)
  python bmad_init.py load --module bmm --all --project-root /path
  python bmad_init.py load --module bmm --vars var1:default1,var2 --project-root /path
  python bmad_init.py load --all --project-root /path  # core only

  # Check if init is needed
  python bmad_init.py check --project-root /path
  python bmad_init.py check --module bmm --project-root /path

  # Resolve plugin defaults given core answers
  python bmad_init.py resolve-defaults --module bmm --answers '{"output_folder":"..."}' --project-root /path

  # Write config from answered questions
  python bmad_init.py write --answers '{"core": {...}, "bmm": {...}}' --project-root /path
"""

import argparse
import copy
import glob as glob_module
import json
import os
import sys
from pathlib import Path

import yaml


# =============================================================================
# Core Questions — loaded from module.json
# =============================================================================

def _load_core_manifest():
    """Load core module manifest from resources/module.json."""
    manifest_path = Path(__file__).resolve().parent.parent / 'resources' / 'module.json'
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def _get_core_manifest():
    """Get cached core manifest, loading on first access."""
    if not hasattr(_get_core_manifest, '_cache'):
        _get_core_manifest._cache = _load_core_manifest()
    return _get_core_manifest._cache


def get_core_questions():
    """Get core questions from module.json."""
    manifest = _get_core_manifest()
    if manifest:
        return manifest.get('questions', {})
    return {}


def get_core_init_intro():
    """Get core init intro message from module.json."""
    manifest = _get_core_manifest()
    if manifest:
        return manifest.get('init_intro', '')
    return ''


def get_core_init_outro():
    """Get core init outro message from module.json."""
    manifest = _get_core_manifest()
    if manifest:
        return manifest.get('init_outro', '')
    return ''


# =============================================================================
# Project Root Detection
# =============================================================================

def find_project_root(llm_provided=None):
    """
    Find project root by looking for _bmad folder.

    Args:
        llm_provided: Path explicitly provided by LLM via --project-root.

    Returns:
        Path to project root, or None if not found.
    """
    if llm_provided:
        candidate = Path(llm_provided)
        if (candidate / '_bmad').exists():
            return candidate
        # On first run _bmad won't exist yet — but the LLM-provided path
        # is still the project root. Return it so we can create _bmad there.
        if candidate.is_dir():
            return candidate

    for start_dir in [Path.cwd(), Path(__file__).resolve().parent]:
        current_dir = start_dir
        while current_dir != current_dir.parent:
            if (current_dir / '_bmad').exists():
                return current_dir
            current_dir = current_dir.parent

    return None


# =============================================================================
# Config Loading
# =============================================================================

def deep_merge(base, override):
    """Deep merge two dicts. Override values take precedence."""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def load_merged_configs(project_root):
    """
    Load and merge project + user configs. User config takes precedence.
    Tries new paths first, falls back to legacy paths.

    Returns:
        Merged config dict, or dict with 'error' key on failure.
    """
    project_root = Path(project_root)

    # New paths
    new_project = project_root / '_bmad' / 'config.yaml'
    new_user = project_root / '_bmad' / 'user-config.yaml'

    # Legacy paths
    legacy_project = project_root / '_bmad' / 'config' / 'modules-project-config.yaml'
    legacy_user = project_root / '_bmad' / 'config' / 'modules-user-config.yaml'

    # Determine which project config to use
    if new_project.exists():
        project_config_path = new_project
        user_config_path = new_user
    elif legacy_project.exists():
        project_config_path = legacy_project
        user_config_path = legacy_user
    else:
        return {'error': f'No config found. Checked: {new_project} and {legacy_project}'}

    merged = {}

    # Load project config (base)
    try:
        with open(project_config_path, 'r', encoding='utf-8') as f:
            project_config = yaml.safe_load(f)
            if project_config:
                merged = deep_merge(merged, project_config)
    except Exception as e:
        return {'error': f'Error reading project config: {e}'}

    # Merge user config on top (overrides)
    if user_config_path.exists():
        try:
            with open(user_config_path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    merged = deep_merge(merged, user_config)
        except Exception as e:
            return {'error': f'Error reading user config: {e}'}

    return merged


def resolve_project_root_placeholder(value, project_root):
    """Replace {project-root} placeholder with actual path."""
    if not value or not isinstance(value, str):
        return value
    if '{project-root}' in value:
        return value.replace('{project-root}', str(project_root))
    return value


def parse_var_specs(vars_string):
    """
    Parse variable specs: var_name:default_value,var_name2:default_value2
    No default = required (returns null if missing).
    """
    if not vars_string:
        return []
    specs = []
    for spec in vars_string.split(','):
        spec = spec.strip()
        if not spec:
            continue
        if ':' in spec:
            parts = spec.split(':', 1)
            specs.append({
                'name': parts[0].strip(),
                'required': False,
                'default': parts[1].strip(),
            })
        else:
            specs.append({
                'name': spec,
                'required': True,
                'default': None,
            })
    return specs


def load_config_vars(module_code, var_specs, project_root, load_all=False):
    """
    Load config variables. Core vars are always included as base.
    Module vars override core on collision.
    """
    merged_config = load_merged_configs(project_root)
    if 'error' in merged_config:
        return merged_config

    modules = merged_config.get('modules', {})

    # If a specific module is requested, verify it exists
    if module_code and module_code != 'core' and module_code not in modules:
        return {'init_required': True, 'missing_module': module_code}

    # Start with core config as base
    core_config = modules.get('core', {})
    config_vars = core_config.get('config', {}).copy()

    # Overlay requested module config
    if module_code and module_code != 'core':
        module_config = modules.get(module_code, {})
        module_vars = module_config.get('config', {})
        config_vars.update(module_vars)

    result = {}
    if load_all:
        for key, value in config_vars.items():
            result[key] = value
    else:
        for spec in var_specs:
            var_name = spec['name']
            config_value = config_vars.get(var_name)
            if config_value is not None and config_value != '':
                result[var_name] = config_value
            elif spec['default'] is not None:
                result[var_name] = spec['default']
            else:
                result[var_name] = None

    return result


# =============================================================================
# Check Subcommand
# =============================================================================

def discover_manifest_skills(project_root):
    """
    Discover bmad-get-manifest-* skills by scanning known skill locations.

    Returns list of {"module_code": str, "skill_path": str} dicts.
    """
    project_root = Path(project_root)
    found = []

    # Search patterns for skill locations
    search_patterns = [
        project_root / '.claude' / 'skills' / 'bmad-get-manifest-*',
        project_root / '_bmad' / 'skills' / 'bmad-get-manifest-*',
    ]

    for pattern in search_patterns:
        for skill_dir in sorted(glob_module.glob(str(pattern))):
            skill_dir = Path(skill_dir)
            if skill_dir.is_dir():
                # Extract module code from skill name: bmad-get-manifest-{code}
                dir_name = skill_dir.name
                prefix = 'bmad-get-manifest-'
                if dir_name.startswith(prefix):
                    module_code = dir_name[len(prefix):]
                    if module_code:
                        found.append({
                            'module_code': module_code,
                            'skill_path': str(skill_dir),
                        })

    return found


def cmd_check(args):
    """Check if config exists and return status."""
    project_root = find_project_root(llm_provided=args.project_root)

    if not project_root:
        result = {
            'status': 'no_project',
            'message': 'No project root found. Provide --project-root to bootstrap.',
        }
        print(json.dumps(result, indent=2))
        return

    project_root = Path(project_root)
    bmad_dir = project_root / '_bmad'

    # No _bmad folder at all
    if not bmad_dir.exists():
        result = {
            'status': 'init_required',
            'project_root': str(project_root),
            'core_questions': get_core_questions(),
            'core_intro': get_core_init_intro(),
            'core_outro': get_core_init_outro(),
            'discovered_plugins': discover_manifest_skills(project_root),
        }
        print(json.dumps(result, indent=2))
        return

    # Check if config files exist
    merged = load_merged_configs(project_root)
    if 'error' in merged:
        result = {
            'status': 'init_required',
            'project_root': str(project_root),
            'core_questions': get_core_questions(),
            'core_intro': get_core_init_intro(),
            'core_outro': get_core_init_outro(),
            'discovered_plugins': discover_manifest_skills(project_root),
            'note': merged['error'],
        }
        print(json.dumps(result, indent=2))
        return

    modules = merged.get('modules', {})

    # If a specific module was requested, check if it's configured
    if args.module and args.module != 'core':
        if args.module not in modules:
            result = {
                'status': 'module_missing',
                'project_root': str(project_root),
                'missing_module': args.module,
                'discovered_plugins': discover_manifest_skills(project_root),
            }
            print(json.dumps(result, indent=2))
            return

    # Everything is ready
    result = {
        'status': 'ready',
        'project_root': str(project_root),
    }
    print(json.dumps(result, indent=2))


# =============================================================================
# Load Subcommand (Fast Path)
# =============================================================================

def cmd_load(args):
    """Load config vars — the fast path."""
    project_root = find_project_root(llm_provided=args.project_root)

    if not project_root:
        print(json.dumps({'error': 'Project root not found (_bmad folder not detected)'},
                         indent=2), file=sys.stderr)
        sys.exit(1)

    var_specs = parse_var_specs(args.vars)
    module_code = args.module  # Can be None — means core only

    result = load_config_vars(module_code, var_specs, project_root, load_all=args.all)

    if 'error' in result:
        print(json.dumps(result, indent=2), file=sys.stderr)
        sys.exit(1)
    elif 'init_required' in result:
        # Module not in config — return this so LLM knows to init
        print(json.dumps(result, indent=2), file=sys.stderr)
        sys.exit(1)
    else:
        print(json.dumps(result, indent=2))


# =============================================================================
# Resolve Defaults Subcommand
# =============================================================================

def expand_template(value, context):
    """
    Expand template placeholders in a value string.

    Supported placeholders:
      {project-root} — absolute project path
      {output_folder} — resolved output folder
      {directory_name} — project directory basename
      {value} — the user's answer (used in result transforms)
      Any other {var_name} — looked up in context
    """
    if not value or not isinstance(value, str):
        return value

    result = value
    for key, val in context.items():
        placeholder = '{' + key + '}'
        if placeholder in result and val is not None:
            result = result.replace(placeholder, str(val))

    return result


def cmd_resolve_defaults(args):
    """Given core answers, resolve plugin variable defaults."""
    project_root = find_project_root(llm_provided=args.project_root)
    if not project_root:
        print(json.dumps({'error': 'Project root not found'}, indent=2), file=sys.stderr)
        sys.exit(1)

    try:
        answers = json.loads(args.answers)
    except json.JSONDecodeError as e:
        print(json.dumps({'error': f'Invalid JSON in --answers: {e}'}, indent=2),
              file=sys.stderr)
        sys.exit(1)

    # Build context for template expansion
    context = {
        'project-root': str(project_root),
        'directory_name': Path(project_root).name,
    }
    context.update(answers)

    # Load manifest for the requested module
    manifest = load_plugin_manifest(args.module, project_root)
    if not manifest:
        print(json.dumps({'error': f'No manifest found for module: {args.module}'},
                         indent=2), file=sys.stderr)
        sys.exit(1)

    # Resolve defaults
    questions = manifest.get('questions', {})
    resolved = {}
    for var_name, var_def in questions.items():
        default = var_def.get('default', '')
        resolved_default = expand_template(str(default), context)
        resolved[var_name] = {
            'prompt': var_def.get('prompt', ''),
            'default': resolved_default,
            'user_setting': var_def.get('user_setting', False),
        }
        if 'single_select' in var_def:
            resolved[var_name]['single_select'] = var_def['single_select']
        if 'result' in var_def:
            resolved[var_name]['result'] = var_def['result']

    result = {
        'module_code': args.module,
        'module_name': manifest.get('name', args.module),
        'intro': manifest.get('init_intro', ''),
        'outro': manifest.get('init_outro', ''),
        'questions': resolved,
    }
    print(json.dumps(result, indent=2))


def load_plugin_manifest(module_code, project_root):
    """Load a plugin manifest from the bmad-get-manifest-{code} skill."""
    project_root = Path(project_root)

    # Search for manifest file
    search_paths = [
        project_root / '.claude' / 'skills' / f'bmad-get-manifest-{module_code}' / 'resources' / 'manifest.json',
        project_root / '_bmad' / 'skills' / f'bmad-get-manifest-{module_code}' / 'resources' / 'manifest.json',
    ]

    for manifest_path in search_paths:
        if manifest_path.exists():
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                continue

    return None


# =============================================================================
# Write Subcommand
# =============================================================================

def cmd_write(args):
    """Write config files from answered questions."""
    project_root = find_project_root(llm_provided=args.project_root)
    if not project_root:
        if args.project_root:
            project_root = Path(args.project_root)
        else:
            print(json.dumps({'error': 'Project root not found and --project-root not provided'},
                             indent=2), file=sys.stderr)
            sys.exit(1)

    project_root = Path(project_root)

    try:
        answers = json.loads(args.answers)
    except json.JSONDecodeError as e:
        print(json.dumps({'error': f'Invalid JSON in --answers: {e}'}, indent=2),
              file=sys.stderr)
        sys.exit(1)

    # Ensure _bmad directory exists
    bmad_dir = project_root / '_bmad'
    bmad_dir.mkdir(exist_ok=True)

    config_path = bmad_dir / 'config.yaml'
    user_config_path = bmad_dir / 'user-config.yaml'

    # Load existing configs if they exist
    project_config = {}
    user_config = {}

    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                project_config = yaml.safe_load(f) or {}
        except Exception:
            pass

    if user_config_path.exists():
        try:
            with open(user_config_path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f) or {}
        except Exception:
            pass

    # Ensure modules structure
    if 'modules' not in project_config:
        project_config['modules'] = {}
    if 'modules' not in user_config:
        user_config['modules'] = {}

    # Process answers per module
    # Expected format: {"core": {"var": {"value": "x", "user_setting": bool}}, "bmm": {...}}
    for module_code, module_answers in answers.items():
        proj_vars = {}
        user_vars = {}

        for var_name, var_data in module_answers.items():
            value = var_data.get('value', var_data) if isinstance(var_data, dict) else var_data
            is_user_setting = var_data.get('user_setting', False) if isinstance(var_data, dict) else False

            if is_user_setting:
                user_vars[var_name] = value
            else:
                proj_vars[var_name] = value

        # Merge into existing config
        if module_code not in project_config['modules']:
            project_config['modules'][module_code] = {}
        if 'config' not in project_config['modules'][module_code]:
            project_config['modules'][module_code]['config'] = {}
        project_config['modules'][module_code]['config'].update(proj_vars)

        if user_vars:
            if module_code not in user_config['modules']:
                user_config['modules'][module_code] = {}
            if 'config' not in user_config['modules'][module_code]:
                user_config['modules'][module_code]['config'] = {}
            user_config['modules'][module_code]['config'].update(user_vars)

    # Create directories if requested
    dirs_created = []
    if args.create_dirs:
        context = {'project-root': str(project_root)}
        # Gather all config values for template expansion
        for module_data in project_config.get('modules', {}).values():
            for k, v in module_data.get('config', {}).items():
                if isinstance(v, str):
                    context[k] = v
        for module_data in user_config.get('modules', {}).values():
            for k, v in module_data.get('config', {}).items():
                if isinstance(v, str):
                    context[k] = v

        for module_code_key in answers:
            manifest = load_plugin_manifest(module_code_key, project_root)
            if manifest and 'directories' in manifest:
                for dir_template in manifest['directories']:
                    dir_path = expand_template(dir_template, context)
                    if dir_path:
                        Path(dir_path).mkdir(parents=True, exist_ok=True)
                        dirs_created.append(dir_path)

    # Write config files
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write('# BMad project configuration (safe to commit)\n')
        yaml.safe_dump(project_config, f, default_flow_style=False, allow_unicode=True,
                       sort_keys=False)

    if user_config.get('modules'):
        with open(user_config_path, 'w', encoding='utf-8') as f:
            f.write('# BMad user configuration (git-ignored)\n')
            yaml.safe_dump(user_config, f, default_flow_style=False, allow_unicode=True,
                           sort_keys=False)

    result = {
        'status': 'written',
        'config_path': str(config_path),
        'user_config_path': str(user_config_path) if user_config.get('modules') else None,
        'dirs_created': dirs_created,
    }
    print(json.dumps(result, indent=2))


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='BMad Init — Project configuration bootstrap and config loader.'
    )
    subparsers = parser.add_subparsers(dest='command')

    # --- check ---
    check_parser = subparsers.add_parser('check', help='Check if init is needed')
    check_parser.add_argument('--module', help='Module code to check (optional)')
    check_parser.add_argument('--project-root', help='Project root path')

    # --- load ---
    load_parser = subparsers.add_parser('load', help='Load config vars (fast path)')
    load_parser.add_argument('--module', help='Module code (omit for core only)')
    load_parser.add_argument('--vars', help='Comma-separated vars with optional defaults')
    load_parser.add_argument('--all', action='store_true', help='Return all config vars')
    load_parser.add_argument('--project-root', help='Project root path')

    # --- resolve-defaults ---
    resolve_parser = subparsers.add_parser('resolve-defaults',
                                           help='Resolve plugin defaults given core answers')
    resolve_parser.add_argument('--module', required=True, help='Plugin module code')
    resolve_parser.add_argument('--answers', required=True, help='JSON string of core answers')
    resolve_parser.add_argument('--project-root', help='Project root path')

    # --- write ---
    write_parser = subparsers.add_parser('write', help='Write config files')
    write_parser.add_argument('--answers', required=True, help='JSON string of all answers')
    write_parser.add_argument('--project-root', help='Project root path')
    write_parser.add_argument('--create-dirs', action='store_true',
                              help='Create directories declared in manifests')

    # Detect if first arg is a known subcommand; if not, treat as legacy load mode
    known_commands = {'check', 'load', 'resolve-defaults', 'write'}
    if len(sys.argv) > 1 and sys.argv[1] not in known_commands and sys.argv[1] != '-h' and sys.argv[1] != '--help':
        # Legacy backward-compat: no subcommand, treat as load
        load_parser_compat = argparse.ArgumentParser(
            description='BMad Init — backward-compatible load mode'
        )
        load_parser_compat.add_argument('--module', help='Module code')
        load_parser_compat.add_argument('--vars', help='Comma-separated vars')
        load_parser_compat.add_argument('--all', action='store_true')
        load_parser_compat.add_argument('--project-root', help='Project root path')
        args = load_parser_compat.parse_args()
        args.command = 'load'

        if not args.vars and not getattr(args, 'all', False):
            load_parser_compat.error('Either --vars or --all must be specified')
    else:
        args = parser.parse_args()
        if args.command is None:
            parser.print_help()
            sys.exit(1)

    commands = {
        'check': cmd_check,
        'load': cmd_load,
        'resolve-defaults': cmd_resolve_defaults,
        'write': cmd_write,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
