# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///

#!/usr/bin/env python3
"""Unit tests for bmad_init.py"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bmad_init import (
    find_project_root,
    parse_var_specs,
    deep_merge,
    resolve_project_root_placeholder,
    load_config_vars,
    load_merged_configs,
    expand_template,
    discover_manifest_skills,
    load_plugin_manifest,
    CORE_QUESTIONS,
)


class TestCoreQuestions(unittest.TestCase):
    """Verify core questions are properly defined."""

    def test_core_questions_exist(self):
        self.assertIn('user_name', CORE_QUESTIONS)
        self.assertIn('communication_language', CORE_QUESTIONS)
        self.assertIn('document_output_language', CORE_QUESTIONS)
        self.assertIn('output_folder', CORE_QUESTIONS)

    def test_core_questions_have_defaults(self):
        for name, q in CORE_QUESTIONS.items():
            self.assertIn('default', q, f'{name} missing default')
            self.assertIn('prompt', q, f'{name} missing prompt')

    def test_user_settings_flagged(self):
        self.assertTrue(CORE_QUESTIONS['user_name'].get('user_setting'))
        self.assertTrue(CORE_QUESTIONS['communication_language'].get('user_setting'))
        self.assertFalse(CORE_QUESTIONS['document_output_language'].get('user_setting', False))
        self.assertFalse(CORE_QUESTIONS['output_folder'].get('user_setting', False))


class TestParseVarSpecs(unittest.TestCase):

    def test_vars_with_defaults(self):
        specs = parse_var_specs('var1:value1,var2:value2')
        self.assertEqual(len(specs), 2)
        self.assertEqual(specs[0]['name'], 'var1')
        self.assertEqual(specs[0]['default'], 'value1')
        self.assertFalse(specs[0]['required'])

    def test_vars_without_defaults(self):
        specs = parse_var_specs('var1,var2')
        self.assertEqual(len(specs), 2)
        self.assertTrue(specs[0]['required'])
        self.assertIsNone(specs[0]['default'])

    def test_mixed_vars(self):
        specs = parse_var_specs('required_var,var2:default2')
        self.assertTrue(specs[0]['required'])
        self.assertFalse(specs[1]['required'])

    def test_colon_in_default(self):
        specs = parse_var_specs('path:{project-root}/some/path')
        self.assertEqual(specs[0]['default'], '{project-root}/some/path')

    def test_empty_string(self):
        self.assertEqual(parse_var_specs(''), [])

    def test_none(self):
        self.assertEqual(parse_var_specs(None), [])


class TestResolveProjectRootPlaceholder(unittest.TestCase):

    def test_resolve_placeholder(self):
        result = resolve_project_root_placeholder('{project-root}/output', Path('/test'))
        self.assertEqual(result, '/test/output')

    def test_no_placeholder(self):
        result = resolve_project_root_placeholder('/absolute/path', Path('/test'))
        self.assertEqual(result, '/absolute/path')

    def test_none(self):
        self.assertIsNone(resolve_project_root_placeholder(None, Path('/test')))

    def test_non_string(self):
        self.assertEqual(resolve_project_root_placeholder(42, Path('/test')), 42)


class TestDeepMerge(unittest.TestCase):

    def test_simple_merge(self):
        result = deep_merge({'a': 1}, {'b': 2})
        self.assertEqual(result, {'a': 1, 'b': 2})

    def test_override(self):
        result = deep_merge({'a': 1}, {'a': 2})
        self.assertEqual(result['a'], 2)

    def test_nested_merge(self):
        base = {'a': {'x': 1, 'y': 2}}
        override = {'a': {'y': 10, 'z': 20}}
        result = deep_merge(base, override)
        self.assertEqual(result['a'], {'x': 1, 'y': 10, 'z': 20})

    def test_originals_unmodified(self):
        base = {'a': {'x': 1}}
        override = {'a': {'y': 2}}
        deep_merge(base, override)
        self.assertEqual(base, {'a': {'x': 1}})


class TestExpandTemplate(unittest.TestCase):

    def test_basic_expansion(self):
        result = expand_template('{project-root}/output', {'project-root': '/test'})
        self.assertEqual(result, '/test/output')

    def test_multiple_placeholders(self):
        result = expand_template(
            '{output_folder}/planning',
            {'output_folder': '_bmad-output', 'project-root': '/test'}
        )
        self.assertEqual(result, '_bmad-output/planning')

    def test_none_value(self):
        self.assertIsNone(expand_template(None, {}))

    def test_non_string(self):
        self.assertEqual(expand_template(42, {}), 42)


class TestFindProjectRoot(unittest.TestCase):

    def test_finds_bmad_folder(self):
        temp_dir = tempfile.mkdtemp()
        try:
            (Path(temp_dir) / '_bmad').mkdir()
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                result = find_project_root()
                self.assertEqual(result.resolve(), Path(temp_dir).resolve())
            finally:
                os.chdir(original_cwd)
        finally:
            shutil.rmtree(temp_dir)

    def test_llm_provided_with_bmad(self):
        temp_dir = tempfile.mkdtemp()
        try:
            (Path(temp_dir) / '_bmad').mkdir()
            result = find_project_root(llm_provided=temp_dir)
            self.assertEqual(result.resolve(), Path(temp_dir).resolve())
        finally:
            shutil.rmtree(temp_dir)

    def test_llm_provided_without_bmad_still_returns_dir(self):
        """First-run case: LLM provides path but _bmad doesn't exist yet."""
        temp_dir = tempfile.mkdtemp()
        try:
            result = find_project_root(llm_provided=temp_dir)
            self.assertEqual(result.resolve(), Path(temp_dir).resolve())
        finally:
            shutil.rmtree(temp_dir)


class TestLoadMergedConfigs(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.bmad_dir = self.project_root / '_bmad'
        self.bmad_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_new_config_path(self):
        """Test loading from _bmad/config.yaml."""
        config_path = self.bmad_dir / 'config.yaml'
        config_path.write_text(
            'modules:\n  core:\n    config:\n      user_name: Test\n'
        )
        result = load_merged_configs(self.project_root)
        self.assertNotIn('error', result)
        self.assertEqual(result['modules']['core']['config']['user_name'], 'Test')

    def test_legacy_config_path(self):
        """Test fallback to legacy _bmad/config/ path."""
        config_dir = self.bmad_dir / 'config'
        config_dir.mkdir()
        (config_dir / 'modules-project-config.yaml').write_text(
            'modules:\n  core:\n    config:\n      user_name: Legacy\n'
        )
        result = load_merged_configs(self.project_root)
        self.assertNotIn('error', result)
        self.assertEqual(result['modules']['core']['config']['user_name'], 'Legacy')

    def test_new_path_preferred_over_legacy(self):
        """New path takes precedence when both exist."""
        # Create new path
        (self.bmad_dir / 'config.yaml').write_text(
            'modules:\n  core:\n    config:\n      user_name: New\n'
        )
        # Create legacy path
        config_dir = self.bmad_dir / 'config'
        config_dir.mkdir()
        (config_dir / 'modules-project-config.yaml').write_text(
            'modules:\n  core:\n    config:\n      user_name: Legacy\n'
        )
        result = load_merged_configs(self.project_root)
        self.assertEqual(result['modules']['core']['config']['user_name'], 'New')

    def test_user_config_overrides(self):
        """User config values override project config."""
        (self.bmad_dir / 'config.yaml').write_text(
            'modules:\n  core:\n    config:\n      user_name: Project\n'
        )
        (self.bmad_dir / 'user-config.yaml').write_text(
            'modules:\n  core:\n    config:\n      user_name: User\n'
        )
        result = load_merged_configs(self.project_root)
        self.assertEqual(result['modules']['core']['config']['user_name'], 'User')

    def test_no_config_returns_error(self):
        result = load_merged_configs(self.project_root)
        self.assertIn('error', result)


class TestLoadConfigVars(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.bmad_dir = self.project_root / '_bmad'
        self.bmad_dir.mkdir()
        (self.bmad_dir / 'config.yaml').write_text(
            'modules:\n'
            '  core:\n'
            '    config:\n'
            '      user_name: DefaultUser\n'
            '      communication_language: English\n'
            '      output_folder: "{project-root}/_bmad-output"\n'
            '  bmm:\n'
            '    config:\n'
            '      project_name: TestProject\n'
            '      user_name: BMMUser\n'
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_load_core_only(self):
        result = load_config_vars(None, [], self.project_root, load_all=True)
        self.assertNotIn('error', result)
        self.assertEqual(result['user_name'], 'DefaultUser')
        self.assertNotIn('project_name', result)

    def test_load_module_vars(self):
        result = load_config_vars('bmm', [], self.project_root, load_all=True)
        self.assertNotIn('error', result)
        self.assertEqual(result['project_name'], 'TestProject')
        # Module overrides core
        self.assertEqual(result['user_name'], 'BMMUser')
        # Core vars still available
        self.assertEqual(result['communication_language'], 'English')

    def test_project_root_resolved(self):
        result = load_config_vars('bmm', [], self.project_root, load_all=True)
        self.assertIn(str(self.project_root), result['output_folder'])

    def test_missing_module_returns_init_required(self):
        result = load_config_vars('nonexistent', [], self.project_root, load_all=True)
        self.assertTrue(result.get('init_required'))
        self.assertEqual(result['missing_module'], 'nonexistent')

    def test_specific_vars_with_defaults(self):
        specs = parse_var_specs('missing_var:fallback')
        result = load_config_vars('bmm', specs, self.project_root)
        self.assertEqual(result['missing_var'], 'fallback')

    def test_required_var_missing_returns_null(self):
        specs = parse_var_specs('nonexistent_var')
        result = load_config_vars('bmm', specs, self.project_root)
        self.assertIsNone(result['nonexistent_var'])


class TestDiscoverManifestSkills(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_discovers_skills(self):
        skill_dir = self.project_root / '.claude' / 'skills' / 'bmad-get-manifest-bmm'
        skill_dir.mkdir(parents=True)
        found = discover_manifest_skills(self.project_root)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]['module_code'], 'bmm')

    def test_ignores_non_manifest_skills(self):
        (self.project_root / '.claude' / 'skills' / 'bmad-init').mkdir(parents=True)
        (self.project_root / '.claude' / 'skills' / 'bmad-other').mkdir(parents=True)
        found = discover_manifest_skills(self.project_root)
        self.assertEqual(len(found), 0)

    def test_discovers_multiple(self):
        for code in ['bmm', 'cis', 'abn']:
            (self.project_root / '.claude' / 'skills' / f'bmad-get-manifest-{code}').mkdir(parents=True)
        found = discover_manifest_skills(self.project_root)
        self.assertEqual(len(found), 3)
        codes = [f['module_code'] for f in found]
        self.assertIn('bmm', codes)
        self.assertIn('cis', codes)


class TestLoadPluginManifest(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_loads_manifest(self):
        manifest_dir = self.project_root / '.claude' / 'skills' / 'bmad-get-manifest-bmm' / 'resources'
        manifest_dir.mkdir(parents=True)
        manifest = {
            'code': 'bmm',
            'name': 'BMad Method',
            'questions': {'project_name': {'prompt': 'Name?', 'default': 'test'}},
        }
        (manifest_dir / 'manifest.json').write_text(json.dumps(manifest))

        result = load_plugin_manifest('bmm', self.project_root)
        self.assertIsNotNone(result)
        self.assertEqual(result['code'], 'bmm')

    def test_returns_none_for_missing(self):
        result = load_plugin_manifest('nonexistent', self.project_root)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
