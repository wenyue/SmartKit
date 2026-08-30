import json
import os
import re
import subprocess
import unittest
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

MATT_PROMOTED = {
    'ask-matt': 'skills/engineering/ask-matt',
    'diagnosing-bugs': 'skills/engineering/diagnosing-bugs',
    'grill-with-docs': 'skills/engineering/grill-with-docs',
    'triage': 'skills/engineering/triage',
    'improve-codebase-architecture': 'skills/engineering/improve-codebase-architecture',
    'setup-matt-pocock-skills': 'skills/engineering/setup-matt-pocock-skills',
    'tdd': 'skills/engineering/tdd',
    'to-spec': 'skills/engineering/to-spec',
    'to-tickets': 'skills/engineering/to-tickets',
    'wayfinder': 'skills/engineering/wayfinder',
    'implement': 'skills/engineering/implement',
    'prototype': 'skills/engineering/prototype',
    'research': 'skills/engineering/research',
    'domain-modeling': 'skills/engineering/domain-modeling',
    'codebase-design': 'skills/engineering/codebase-design',
    'code-review': 'skills/engineering/code-review',
    'resolving-merge-conflicts': 'skills/engineering/resolving-merge-conflicts',
    'wizard': 'skills/engineering/wizard',
    'grill-me': 'skills/productivity/grill-me',
    'grilling': 'skills/productivity/grilling',
    'handoff': 'skills/productivity/handoff',
    'teach': 'skills/productivity/teach',
    'to-questionnaire': 'skills/productivity/to-questionnaire',
    'wait-what': 'skills/productivity/wait-what',
    'writing-for-agents': 'skills/productivity/writing-for-agents',
}

def load_json(relative_path: str) -> dict:
    value = json.loads((REPO_ROOT / relative_path).read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise AssertionError(f'{relative_path} must contain an object')
    return value


def markdown_structure(text: str) -> tuple[str, ...]:
    blocks = re.split(r'\n[ \t]*\n', text.strip())
    structure = []
    for block in blocks:
        first_line = block.lstrip().splitlines()[0]
        if first_line == '---':
            structure.append('frontmatter')
        elif first_line.startswith('#'):
            structure.append(first_line.split(maxsplit=1)[0])
        elif first_line.startswith('```'):
            structure.append(first_line)
        elif first_line.startswith('- [ ] '):
            structure.append('checklist')
        elif first_line.startswith('- '):
            structure.append('unordered-list')
        elif re.match(r'\d+\. ', first_line):
            structure.append('ordered-list')
        elif first_line.startswith('|'):
            structure.append('table')
        else:
            structure.append('paragraph')
    return tuple(structure)


def fenced_code_blocks(text: str) -> tuple[str, ...]:
    return tuple(
        re.findall(
            r'^(?:```[^\n]*\n.*?^```\s*$|~~~[^\n]*\n.*?^~~~\s*$)',
            text,
            re.MULTILINE | re.DOTALL,
        )
    )


def without_fenced_code(text: str) -> str:
    return re.sub(
        r'^(?:```[^\n]*\n.*?^```\s*$|~~~[^\n]*\n.*?^~~~\s*$)',
        '',
        text,
        flags=re.MULTILINE | re.DOTALL,
    )


def inline_code_literals(text: str) -> Counter[str]:
    literals = re.findall(r'(?<!`)`([^`]+)`(?!`)', without_fenced_code(text))
    return Counter(literal.replace('\n', ' ') for literal in literals)


def markdown_link_targets(text: str) -> Counter[str]:
    return Counter(re.findall(r'\[[^\]]*\]\(([^)]+)\)', text))


class PluginManifestTest(unittest.TestCase):
    def test_repository_agents_entry_matches_public_template_around_rule_rows(self):
        template = (
            REPO_ROOT / 'setup-assets/templates/entry-files/AGENTS.md'
        ).read_text(encoding='utf-8')
        entry = (REPO_ROOT / 'AGENTS.md').read_text(encoding='utf-8')
        prefix, suffix = template.split('{{project_rule_rows}}')
        start = entry.index('## Project rules')
        end = entry.index('## Agent skills', start)
        project_rules = entry[start:end].rstrip() + '\n'

        self.assertTrue(project_rules.startswith(prefix))
        self.assertTrue(project_rules.endswith(suffix))
        rule_rows = project_rules[len(prefix) : len(project_rules) - len(suffix)]
        self.assertRegex(rule_rows, r'^(?:\|.*\|\n?)+$')

    def test_repository_local_rules_use_only_the_project_numbering_contract(self):
        self.assertEqual(
            {
                path.name
                for path in (REPO_ROOT / '.agents/rules').glob('*.md')
            },
            {
                '00-project-policy.md',
            },
        )

    def test_documentation_and_local_runtime_boundaries(self):
        self.assertFalse((REPO_ROOT / 'agents-zh').exists())

        chinese_docs = REPO_ROOT / 'docs' / 'zh-CN'
        self.assertTrue(chinese_docs.is_dir())
        self.assertTrue(any(chinese_docs.rglob('*.md')))
        self.assertFalse(any(path.suffix != '.md' for path in chinese_docs.rglob('*') if path.is_file()))

        self.assertEqual(
            {path.name for path in (REPO_ROOT / '.agents').iterdir()},
            {'plugins', 'rules', 'skills'},
        )

    def test_chinese_documentation_has_one_to_one_english_mirrors(self):
        chinese_root = REPO_ROOT / 'docs' / 'zh-CN'
        source_paths = set()
        for root_name in (
            '.agents',
            'agents/source',
            'rules/source',
            'setup-assets/blueprints',
            'skills/setup-project-agents',
        ):
            source_paths.update(
                path.relative_to(REPO_ROOT)
                for path in (REPO_ROOT / root_name).rglob('*.md')
            )
        for name in (
            'create-worktree', 'refactor-code', 'rename-code', 'diagnose-agent-session',
            'finish-worktree', 'implement-tickets', 'write-code-comment',
            'write-rules-and-skills',
        ):
            source_paths.update(
                path.relative_to(REPO_ROOT)
                for path in (REPO_ROOT / 'skills' / name).rglob('*.md')
            )

        translated_paths = {
            path.relative_to(chinese_root)
            for path in chinese_root.rglob('*.md')
        }
        self.assertEqual(translated_paths, source_paths)

        translation_pairs = [(Path('README.md'), REPO_ROOT / 'README.zh-CN.md')]
        translation_pairs.extend(
            (source_path, chinese_root / source_path)
            for source_path in sorted(source_paths)
        )
        for source_path, translation_path in translation_pairs:
            with self.subTest(path=source_path.as_posix()):
                source = (REPO_ROOT / source_path).read_text(encoding='utf-8')
                translation = translation_path.read_text(encoding='utf-8')
                self.assertEqual(
                    markdown_structure(translation),
                    markdown_structure(source),
                )

    def test_chinese_documentation_preserves_literal_markdown_surfaces(self):
        chinese_root = REPO_ROOT / 'docs' / 'zh-CN'
        for translation_path in sorted(chinese_root.rglob('*.md')):
            source_path = REPO_ROOT / translation_path.relative_to(chinese_root)
            source = source_path.read_text(encoding='utf-8')
            translation = translation_path.read_text(encoding='utf-8')
            with self.subTest(path=source_path.relative_to(REPO_ROOT).as_posix()):
                self.assertEqual(fenced_code_blocks(translation), fenced_code_blocks(source))
                self.assertEqual(inline_code_literals(translation), inline_code_literals(source))
                self.assertEqual(markdown_link_targets(translation), markdown_link_targets(source))

                if source.startswith('---\n'):
                    source_frontmatter = source.split('---\n', 2)[1]
                    translation_frontmatter = translation.split('---\n', 2)[1]
                    source_name = re.search(r'^name:\s*(.+)$', source_frontmatter, re.MULTILINE)
                    translation_name = re.search(
                        r'^name:\s*(.+)$', translation_frontmatter, re.MULTILINE
                    )
                    self.assertEqual(
                        translation_name.group(1) if translation_name else None,
                        source_name.group(1) if source_name else None,
                    )
                    if re.search(r'^description:', source_frontmatter, re.MULTILINE):
                        self.assertRegex(translation_frontmatter, r'(?m)^description:')

    def test_chinese_documentation_has_no_han_separating_ascii_spaces(self):
        chinese_root = REPO_ROOT / 'docs' / 'zh-CN'
        han_space = re.compile(
            r'[\u3400-\u9fff] +(?=(?:\*{1,2})?[\u3400-\u9fff])'
            r'|[\u3400-\u9fff] +\*'
            r'|\* +[\u3400-\u9fff]'
        )
        protected = re.compile(r'(`+[^`]*?`+|\]\([^)]*\))')

        for translation_path in sorted(chinese_root.rglob('*.md')):
            text = without_fenced_code(translation_path.read_text(encoding='utf-8'))
            prose = protected.sub('X', text)
            with self.subTest(path=translation_path.relative_to(chinese_root).as_posix()):
                self.assertIsNone(han_space.search(prose))

    def test_project_catalog_matches_native_plugin_version(self):
        catalog = load_json('setup-assets/catalog/assets.json')
        version = (REPO_ROOT / 'VERSION').read_text(encoding='utf-8').strip()
        self.assertEqual(catalog['plugin']['id'], 'smartkit')
        self.assertEqual(catalog['plugin']['version'], version)

    def test_rule_and_skill_authoring_has_one_public_and_three_private_skills(self):
        custom = load_json('skills/registry.json')['custom']
        public_root = REPO_ROOT / 'skills' / 'write-rules-and-skills'
        self.assertIn(
            {
                'id': 'smartkit/write-rules-and-skills',
                'path': 'write-rules-and-skills',
            },
            custom,
        )

        private_root = REPO_ROOT / '.agents' / 'skills'
        self.assertEqual(
            {path.name for path in private_root.iterdir() if path.is_dir()},
            {
                'translate-agent-artifacts',
                'write-setup-authoring-contracts',
                'write-shared-rules-and-skills',
            },
        )
        public_ids = {item['id'] for item in custom}
        self.assertNotIn('smartkit/write-setup-authoring-contracts', public_ids)
        self.assertNotIn('smartkit/write-shared-rules-and-skills', public_ids)
        self.assertNotIn('smartkit/translate-agent-artifacts', public_ids)

        private_names = (
            'translate-agent-artifacts',
            'write-setup-authoring-contracts',
            'write-shared-rules-and-skills',
        )
        authoring_roots = (public_root, *(private_root / name for name in private_names))
        expected_references = {
            'write-rules-and-skills': {
                'acceptance.md',
                'author.md',
                'evaluation.md',
                'job-design.md',
                'models.md',
                'reviews.md',
                'role-runtime.md',
            },
            'write-shared-rules-and-skills': {
                'portability.md',
            },
            'write-setup-authoring-contracts': set(),
            'translate-agent-artifacts': set(),
        }
        for skill_root in authoring_roots:
            with self.subTest(authoring_skill=skill_root.name):
                skill_text = (skill_root / 'SKILL.md').read_text(encoding='utf-8')
                self.assertRegex(
                    skill_text,
                    rf'(?m)^name:\s*{re.escape(skill_root.name)}\s*$',
                )
                for relative_path in re.findall(
                    r'\]\((references/[^)]+\.md)\)', skill_text
                ):
                    self.assertTrue((skill_root / relative_path).is_file())
                self.assertEqual(
                    {
                        path.name
                        for path in (skill_root / 'references').glob('*.md')
                    },
                    expected_references[skill_root.name],
                )

        for name in private_names:
            with self.subTest(private_skill=name):
                private_skill = private_root / name
                metadata = (private_skill / 'agents' / 'openai.yaml').read_text(
                    encoding='utf-8'
                )
                self.assertRegex(metadata, r'(?m)^interface:\s*$')
                self.assertRegex(metadata, r'(?m)^\s+display_name:\s+.+$')
                self.assertRegex(metadata, r'(?m)^\s+short_description:\s+.+$')
                self.assertRegex(metadata, r'(?m)^\s+default_prompt:\s+.+$')
                self.assertIn(f'${name}', metadata)

    def test_custom_skills_keep_invocation_metadata_aligned(self):
        custom = load_json('skills/registry.json')['custom']
        for item in custom:
            with self.subTest(skill=item['id']):
                skill_root = REPO_ROOT / 'skills' / item['path']
                skill = (skill_root / 'SKILL.md').read_text(encoding='utf-8')
                frontmatter = skill.split('---', 2)[1]
                metadata_path = skill_root / 'agents' / 'openai.yaml'

                self.assertTrue(metadata_path.is_file())
                metadata = metadata_path.read_text(encoding='utf-8')
                self.assertRegex(metadata, r'(?m)^interface:\s*$')
                self.assertRegex(metadata, r'(?m)^\s+display_name:\s+.+$')
                self.assertRegex(metadata, r'(?m)^\s+short_description:\s+.+$')
                self.assertNotIn('disable-model-invocation: false', frontmatter)

                model_invocation_disabled = (
                    'disable-model-invocation: true' in frontmatter
                )
                implicit_invocation_allowed = (
                    'allow_implicit_invocation: false' not in metadata
                )
                self.assertEqual(
                    model_invocation_disabled,
                    not implicit_invocation_allowed,
                )

    def test_repository_root_is_the_only_plugin_root(self):
        version = (REPO_ROOT / 'VERSION').read_text(encoding='utf-8').strip()
        self.assertRegex(
            version,
            r'^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)'
            r'(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$',
        )
        manifests = (
            REPO_ROOT / '.codex-plugin' / 'plugin.json',
            REPO_ROOT / '.cursor-plugin' / 'plugin.json',
            REPO_ROOT / 'plugin.json',
        )
        for manifest_path in manifests:
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            self.assertEqual(manifest['name'], 'smartkit')
            self.assertEqual(manifest['version'], version)
            self.assertEqual(manifest['skills'], './skills/')
        self.assertEqual(
            load_json('.codex-plugin/plugin.json')['interface']['displayName'],
            'WenYue SmartKit',
        )
        self.assertEqual(
            load_json('.cursor-plugin/plugin.json')['displayName'],
            'WenYue SmartKit',
        )
        self.assertFalse((REPO_ROOT / 'agents' / '.codex-plugin').exists())
        self.assertFalse((REPO_ROOT / 'agents' / 'skills').exists())

    def test_local_marketplaces_point_at_the_repository_root(self):
        version = (REPO_ROOT / 'VERSION').read_text(encoding='utf-8').strip()
        for relative in (
            '.cursor-plugin/marketplace.json',
            '.github/plugin/marketplace.json',
        ):
            marketplace = load_json(relative)
            self.assertEqual(marketplace['name'], 'wenyue')
            self.assertEqual(marketplace['metadata']['version'], version)
            self.assertEqual(marketplace['plugins'][0]['name'], 'smartkit')
            self.assertEqual(marketplace['plugins'][0]['source'], './')
            self.assertEqual(marketplace['plugins'][0]['version'], version)
        codex = load_json('.agents/plugins/marketplace.json')
        self.assertEqual(codex['name'], 'wenyue')
        self.assertEqual(codex['interface']['displayName'], 'WenYue SmartKit')
        self.assertEqual(codex['plugins'][0]['name'], 'smartkit')
        self.assertEqual(codex['plugins'][0]['source']['path'], './')

    def test_root_manifests_expose_plugin_owned_capabilities(self):
        codex = load_json('.codex-plugin/plugin.json')
        cursor = load_json('.cursor-plugin/plugin.json')
        copilot = load_json('plugin.json')

        self.assertEqual(codex['hooks'], './hooks/hooks.json')
        self.assertEqual(cursor['hooks'], './hooks/cursor.json')
        self.assertEqual(cursor['rules'], './rules/cursor/')
        self.assertEqual(copilot['hooks'], './hooks/copilot.json')
        self.assertEqual(codex['mcpServers'], './.mcp.json')
        self.assertEqual(cursor['mcpServers'], './mcp/cursor.json')
        self.assertEqual(copilot['mcpServers'], './mcp/copilot.json')
        self.assertNotIn('agents', codex)
        self.assertEqual(cursor['agents'], './agents/cursor/')
        self.assertEqual(copilot['agents'], './agents/copilot/')
        for manifest, expected in (
            (codex, '.mcp.json'),
            (cursor, 'mcp/cursor.json'),
            (copilot, 'mcp/copilot.json'),
        ):
            self.assertTrue((REPO_ROOT / expected).is_file())
        for manifest in (codex, cursor, copilot):
            self.assertTrue((REPO_ROOT / manifest['skills']).is_dir())
        for manifest in (cursor, copilot):
            self.assertTrue((REPO_ROOT / manifest['agents']).is_dir())
        self.assertNotIn('rules', codex)
        self.assertNotIn('rules', copilot)

        plugin_skills = {
            path.name
            for path in (REPO_ROOT / 'skills').iterdir()
            if path.is_dir()
        }
        custom = {
            'setup-project-agents', 'create-worktree', 'refactor-code', 'rename-code',
            'diagnose-agent-session', 'finish-worktree', 'implement-tickets', 'write-code-comment',
            'write-rules-and-skills',
        }
        self.assertEqual(plugin_skills, { *custom, *MATT_PROMOTED})
        lock = load_json('vendor/external-skills.lock.json')
        self.assertEqual(set(lock), {'sources'})
        matt = lock['sources'][0]
        self.assertEqual(matt['id'], 'mattpocock/skills')
        self.assertEqual(matt['requested_ref'], 'v1.2.3')
        self.assertEqual(
            matt['commit'],
            '6acc160e4e0cd062dbbbd7a1b26ae92855edf07e',
        )
        self.assertEqual(
            {skill['id'].split('/', 1)[1]: skill['source_path'] for skill in matt['skills']},
            MATT_PROMOTED,
        )
        for name in MATT_PROMOTED:
            with self.subTest(skill=name):
                skill_root = REPO_ROOT / 'skills' / name
                skill_text = (skill_root / 'SKILL.md').read_text(encoding='utf-8')
                self.assertRegex(skill_text, rf'(?m)^name:\s*{re.escape(name)}\s*$')
                self.assertTrue((skill_root / 'agents' / 'openai.yaml').is_file())
        self.assertFalse((REPO_ROOT / 'skills/debug-mode').exists())
        self.assertTrue(
            (
                REPO_ROOT
                / 'skills/setup-project-agents/scripts/_vendor/tomli/__init__.py'
            ).is_file()
        )
        self.assertTrue((REPO_ROOT / 'agents/registry.json').is_file())
        self.assertTrue((REPO_ROOT / 'agents/source/change-set-verifier.md').is_file())
        self.assertTrue((REPO_ROOT / 'scripts/sync_agent_adapters.py').is_file())
        self.assertTrue((REPO_ROOT / 'rules/registry.json').is_file())
        self.assertFalse(any((REPO_ROOT / 'runtime').rglob('SKILL.md')))
        self.assertEqual(
            {
                path.name
                for path in (REPO_ROOT / 'setup-assets').iterdir()
                if path.is_dir()
                and any(
                    item.is_file() and '__pycache__' not in item.parts
                    for item in path.rglob('*')
                )
            },
            {'blueprints', 'catalog', 'templates'},
        )
        for retired_root in ('project', 'blueprints', 'catalog', 'config', 'templates'):
            self.assertFalse((REPO_ROOT / retired_root).exists())

        hook_paths = {
            'codex': REPO_ROOT / 'hooks/hooks.json',
            'cursor': REPO_ROOT / cursor['hooks'],
            'copilot': REPO_ROOT / copilot['hooks'],
        }
        for harness, path in hook_paths.items():
            with self.subTest(harness=harness):
                self.assertTrue(path.is_file())
                content = path.read_text(encoding='utf-8')
                expected_entry = (
                    'run_recommended_tools'
                    if harness == 'cursor'
                    else 'check_recommended_tools'
                )
                self.assertIn(expected_entry, content)
                self.assertIn('runtime/recommended-tools', content.replace('\\', '/'))
                self.assertIn(f'--harness {harness}', content)
                self.assertNotIn('.agents/', content)
                self.assertNotIn('.agents\\', content)
                self.assertNotIn(' install', content.lower())
                self.assertNotIn(' upgrade', content.lower())

        self.assertEqual(
            set(load_json('hooks/hooks.json')['hooks']),
            {'SessionStart', 'UserPromptSubmit', 'PreToolUse'},
        )
        self.assertEqual(
            set(load_json('hooks/cursor.json')['hooks']),
            {'sessionStart'},
        )
        cursor_hooks = load_json('hooks/cursor.json')['hooks']
        self.assertIn(
            '--delivery context',
            cursor_hooks['sessionStart'][0]['command'],
        )
        self.assertEqual(
            set(load_json('hooks/copilot.json')['hooks']),
            {
                'sessionStart',
                'userPromptTransformed',
                'preCompact',
                'preToolUse',
                'agentStop',
            },
        )

    def test_cursor_hook_uses_cross_platform_dispatcher(self):
        cursor_hooks = load_json('hooks/cursor.json')['hooks']
        commands = {cursor_hooks['sessionStart'][0]['command']}
        dispatcher = REPO_ROOT / 'runtime/recommended-tools/run_recommended_tools.cmd'

        self.assertTrue(dispatcher.is_file())
        for command in commands:
            self.assertIn('run_recommended_tools.cmd', command)
            self.assertNotRegex(command, r'\bpython3?\b')

        if os.name == 'nt':
            invocation = ['cmd.exe', '/d', '/c', str(dispatcher), '--help']
        else:
            self.assertTrue(os.access(dispatcher, os.X_OK))
            invocation = [
                'sh', '-c', '"$1" --help', 'smartkit-cursor-hook', str(dispatcher)
            ]
        result = subprocess.run(
            invocation,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('usage:', result.stdout.lower())

    def test_hook_harness_contract(self):
        contract_path = REPO_ROOT / 'setup-assets/catalog/harnesses.json'
        self.assertTrue(contract_path.is_file())
        contract = load_json('setup-assets/catalog/harnesses.json')

        self.assertEqual(set(contract), {'requiredOperatingSystems', 'harnesses'})
        self.assertEqual(
            contract['requiredOperatingSystems'],
            ['windows', 'linux'],
        )
        self.assertEqual(
            set(contract['harnesses']),
            {'codex', 'cursor', 'copilot'},
        )

        for harness, spec in contract['harnesses'].items():
            with self.subTest(harness=harness):
                manifest = load_json(spec['hookManifest'])
                entry = manifest['hooks'][spec['hookEvent']][0]
                if 'hooks' in entry:
                    entry = entry['hooks'][0]
                for route in spec['hookRoutes'].values():
                    if route == 'dispatcher':
                        self.assertIn('run_recommended_tools.cmd', entry['command'])
                    else:
                        self.assertIn(route, entry)

    def test_internal_json_contracts_use_only_the_plugin_version(self):
        internal_documents = (
            'agents/registry.json',
            'mcp/registry.json',
            'rules/registry.json',
            'skills/registry.json',
            'setup-assets/catalog/harnesses.json',
            'setup-assets/templates/harness-config/agents.config.json',
            'vendor/external-skills.lock.json',
        )
        for relative in internal_documents:
            with self.subTest(relative=relative):
                self.assertNotIn('version', load_json(relative))

    def test_agent_registry_has_generated_host_adapters_without_model_pins(self):
        registry = load_json('agents/registry.json')
        self.assertEqual(set(registry), {'agents'})
        self.assertEqual([item['id'] for item in registry['agents']], ['change-set-verifier'])

        paths = {
            'codex': REPO_ROOT / 'agents/codex/change-set-verifier.toml',
            'cursor': REPO_ROOT / 'agents/cursor/change-set-verifier.md',
            'copilot': REPO_ROOT / 'agents/copilot/change-set-verifier.agent.md',
        }
        for harness, path in paths.items():
            with self.subTest(harness=harness):
                self.assertTrue(path.is_file())
                content = path.read_text(encoding='utf-8')
                self.assertIn('change-set-verification/SKILL.md', content)
                self.assertNotRegex(content, r'(?m)^model\s*[:=]')


if __name__ == '__main__':
    unittest.main()
