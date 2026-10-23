from __future__ import annotations
import importlib.util
import json
import os
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from urllib.parse import unquote


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER_SPEC = importlib.util.spec_from_file_location(
    'check_candidate', REPO_ROOT / 'skills/write-rules-and-skills/scripts/check_candidate.py'
)
assert CHECKER_SPEC is not None and CHECKER_SPEC.loader is not None
CHECKER = importlib.util.module_from_spec(CHECKER_SPEC)
CHECKER_SPEC.loader.exec_module(CHECKER)

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
    'implement-spec': 'skills/engineering/implement-spec',
    'pr': 'skills/engineering/pr',
    'retro': 'skills/engineering/retro',
    'prototype': 'skills/engineering/prototype',
    'research': 'skills/engineering/research',
    'domain-modeling': 'skills/engineering/domain-modeling',
    'codebase-design': 'skills/engineering/codebase-design',
    'code-review': 'skills/engineering/code-review',
    'wizard': 'skills/engineering/wizard',
    'grill-me': 'skills/productivity/grill-me',
    'grilling': 'skills/productivity/grilling',
    'handoff': 'skills/productivity/handoff',
    'teach': 'skills/productivity/teach',
    'to-questionnaire': 'skills/productivity/to-questionnaire',
    'wait-what': 'skills/productivity/wait-what',
    'writing-for-agents': 'skills/productivity/writing-for-agents',
}

PONYTAIL_PROMOTED = {'ponytail', 'ponytail-review', 'ponytail-audit', 'ponytail-debt'}

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


def markdown_link_targets(
    text: str, document_path: Path, mirrors: Mapping[Path, Path]
) -> Counter[tuple[Path | str, str]]:
    targets: Counter[tuple[Path | str, str]] = Counter()
    for _, line in CHECKER.content_lines(text):
        for target in CHECKER.link_targets(line):
            if CHECKER.SCHEME.match(target) or target.startswith(('/', '#')):
                targets[(target, '')] += 1
                continue
            path = re.split(r'[?#]', target, maxsplit=1)[0]
            if not path:
                targets[(target, '')] += 1
                continue
            destination = (document_path.parent / unquote(path)).resolve()
            destination = mirrors.get(destination, destination)
            if not destination.exists():
                raise AssertionError(f'{document_path}: link target does not exist: {target}')
            targets[(destination, target[len(path):])] += 1
    return targets


class PluginManifestTest(unittest.TestCase):
    def test_repository_agents_entry_matches_public_template_around_rule_items(self):
        template = (
            REPO_ROOT / 'setup-assets/templates/entry-files/AGENTS.md'
        ).read_text(encoding='utf-8')
        entry = (REPO_ROOT / 'AGENTS.md').read_text(encoding='utf-8')
        prefix, suffix = template.split('{{project_rule_index}}')
        start = entry.index('## Project rules')
        end = entry.index('## Agent skills', start)
        project_rules = entry[start:end].rstrip() + '\n'

        self.assertTrue(project_rules.startswith(prefix))
        self.assertTrue(project_rules.endswith(suffix))
        index = project_rules[len(prefix) : len(project_rules) - len(suffix)]
        required_template = (
            REPO_ROOT / 'setup-assets/templates/entry-files/required-rules.md'
        ).read_text(encoding='utf-8')
        required_prefix, _ = required_template.split('{{rule_items}}')
        self.assertTrue(index.startswith(required_prefix))
        self.assertNotIn('### On-demand rules', index)
        self.assertNotIn('| Rule | Strength |', index)
        self.assertIn('- `.agents/rules/self-hosting-authority.md`', index)
        self.assertIn('- `.agents/rules/project-policy.md`', index)
        self.assertIn('- `.agents/rules/structure.md`', index)

    def test_repository_local_rules_match_required_paths(self):
        self.assertEqual(
            {
                path.name
                for path in (REPO_ROOT / '.agents/rules').glob('*.md')
            },
            {
                'self-hosting-authority.md',
                'project-policy.md',
                'structure.md',
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
            'rules',
            'setup-assets/blueprints',
            'skills/setup-project-agents',
        ):
            source_paths.update(
                path.relative_to(REPO_ROOT)
                for path in (REPO_ROOT / root_name).rglob('*.md')
            )
        for name in (
            'maintain-project-config', 'create-worktree', 'refactor-code', 'rename-code', 'diagnose-agent-session',
            'what-changes', 'review-for-humans', 'collect-todos', 'what-if',
            'finish-worktree',
            'write-rules-and-skills',
            'rule-code', 'rule-error-handling', 'rule-code-comment',
            'rule-cpp', 'rule-flutter', 'rule-go', 'rule-python',
        ):
            source_paths.update(
                path.relative_to(REPO_ROOT)
                for path in (REPO_ROOT / 'skills' / name).rglob('*.md')
            )
        source_paths.update(
            path.relative_to(REPO_ROOT)
            for path in (REPO_ROOT / 'runtime').glob('*/prompts/**/*.md')
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
        mirrors = {
            (REPO_ROOT / path.relative_to(chinese_root)).resolve(): path.resolve()
            for path in chinese_root.rglob('*.md')
        }
        for translation_path in sorted(chinese_root.rglob('*.md')):
            source_path = REPO_ROOT / translation_path.relative_to(chinese_root)
            source = source_path.read_text(encoding='utf-8')
            translation = translation_path.read_text(encoding='utf-8')
            with self.subTest(path=source_path.relative_to(REPO_ROOT).as_posix()):
                self.assertEqual(fenced_code_blocks(translation), fenced_code_blocks(source))
                self.assertEqual(inline_code_literals(translation), inline_code_literals(source))
                self.assertEqual(
                    markdown_link_targets(translation, translation_path, {}),
                    markdown_link_targets(source, source_path, mirrors),
                )

                if source_path.match('runtime/*/prompts/*.md'):
                    self.assertEqual(
                        sorted(re.findall(r'\{[^{}]+\}', translation)),
                        sorted(re.findall(r'\{[^{}]+\}', source)),
                    )

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

    def test_translation_link_targets_resolve_mirrors_and_preserve_literals(self):
        source_path = REPO_ROOT / '.agents/skills/upgrade-smartkit/SKILL.md'
        canonical = REPO_ROOT / 'skills/setup-project-agents/references/ownership.md'
        mirror = REPO_ROOT / 'docs/zh-CN/skills/setup-project-agents/references/ownership.md'
        text = '''[Mirror](../../../skills/setup-project-agents/references/ownership.md?view=plain#owner)
[Source](../../../VERSION?raw=1#release)
[Reference]: ../../../skills/setup-project-agents/references/ownership.md
[Web](https://example.com/path?q=1#section) [Root](/docs/page.md#section)
[Network](//example.com/path) [Self](#section) [Mail](mailto:example@example.com)
`[Literal](missing.md)`
```markdown
[Example](also-missing.md)
```
'''
        self.assertEqual(
            markdown_link_targets(text, source_path, {canonical: mirror}),
            Counter({
                (mirror, '?view=plain#owner'): 1,
                (mirror, ''): 1,
                (REPO_ROOT / 'VERSION', '?raw=1#release'): 1,
                ('https://example.com/path?q=1#section', ''): 1,
                ('/docs/page.md#section', ''): 1,
                ('//example.com/path', ''): 1,
                ('#section', ''): 1,
                ('mailto:example@example.com', ''): 1,
            }),
        )
        with self.assertRaisesRegex(AssertionError, 'link target does not exist'):
            markdown_link_targets('[Missing](missing.md)', source_path, {})

    def test_chinese_documentation_has_no_han_separating_ascii_spaces(self):
        chinese_root = REPO_ROOT / 'docs' / 'zh-CN'
        han_space = re.compile(
            r'[\u3400-\u9fff] +[\u3400-\u9fff]'
            r'|[\u3400-\u9fff] +\*(?!\*)'
            r'|(?<!\*)\* +[\u3400-\u9fff]'
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

    def test_project_private_skill_inventory_is_not_public(self):
        private_root = REPO_ROOT / '.agents' / 'skills'
        private_names = {
            'translate-agent-artifacts',
            'upgrade-smartkit',
            'maintain-third-party-skills',
            'write-setup-authoring-blueprints',
            'write-shared-rules-and-skills',
        }
        self.assertEqual(
            {path.name for path in private_root.iterdir() if path.is_dir()},
            private_names,
        )
        custom = load_json('skills/registry.json')['custom']
        public_ids = {item['id'] for item in custom}
        for name in sorted(private_names):
            with self.subTest(private_skill=name):
                self.assertNotIn(f'smartkit/{name}', public_ids)

    def test_rule_and_skill_authoring_entries_and_resources_are_consistent(self):
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
        private_names = (
            'translate-agent-artifacts',
            'write-setup-authoring-blueprints',
            'write-shared-rules-and-skills',
        )
        authoring_roots = (public_root, *(private_root / name for name in private_names))
        expected_references = {
            'write-rules-and-skills': {
                'author.md',
                'change-reviewer.md',
                'controller.md',
                'correctness-reviewer.md',
                'openai-metadata.md',
                'quality-reviewer.md',
                'reviewer.md',
                'runner.md',
                'shared-terms.md',
            },
            'write-shared-rules-and-skills': set(),
            'write-setup-authoring-blueprints': set(),
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

    def test_custom_skill_entry_inventory_matches_registry(self):
        custom = load_json('skills/registry.json')['custom']
        skill_roots = [REPO_ROOT / 'skills' / item['path'] for item in custom]
        declared_entries = {
            (root / 'SKILL.md').relative_to(REPO_ROOT).as_posix()
            for root in skill_roots
        }
        observed_entries = {
            entry.relative_to(REPO_ROOT).as_posix()
            for root in skill_roots
            for entry in root.rglob('SKILL.md')
            if entry.is_file()
        }
        self.assertEqual(observed_entries, declared_entries)

    def test_all_skills_have_chinese_interface_metadata(self):
        for parent in ('skills', '.agents/skills'):
            for entry in sorted((REPO_ROOT / parent).glob('*/SKILL.md')):
                with self.subTest(skill=entry.parent.name):
                    metadata = (entry.parent / 'agents/openai.yaml').read_text(
                        encoding='utf-8'
                    )
                    self.assertRegex(metadata, r'(?m)^interface:\s*$')
                    self.assertRegex(metadata, r'(?m)^\s+display_name:\s+.+$')
                    description = re.search(
                        r'(?m)^  short_description: "([^"\n]+)"$', metadata
                    )
                    self.assertIsNotNone(description)
                    self.assertRegex(description.group(1), r'[\u4e00-\u9fff]')
                    prompt = re.search(
                        r'(?m)^  default_prompt: "([^"\n]+)"$', metadata
                    )
                    self.assertIsNotNone(prompt)
                    self.assertRegex(prompt.group(1), r'[\u4e00-\u9fff]')
                    self.assertRegex(
                        prompt.group(1),
                        r'\$' + re.escape(entry.parent.name) + r'(?![a-z0-9-])',
                    )
                    self.assertRegex(
                        metadata, r'(?m)^  brand_color: "#[0-9A-Fa-f]{6}"$'
                    )
                    for field in ('icon_small', 'icon_large'):
                        icon = re.search(
                            r'(?m)^  ' + field + r': "([^"\n]+)"$', metadata
                        )
                        self.assertIsNotNone(icon)
                        relative = Path(icon.group(1))
                        self.assertFalse(relative.is_absolute())
                        path = (entry.parent / relative).resolve()
                        self.assertIn(entry.parent.resolve(), path.parents)
                        self.assertTrue(path.is_file(), str(path))
                        if path.suffix == '.svg':
                            image = ET.parse(path).getroot()
                            self.assertEqual(
                                image.tag, '{http://www.w3.org/2000/svg}svg'
                            )
                            self.assertTrue(image.get('viewBox'))
                    frontmatter = entry.read_text(encoding='utf-8').split('---', 2)[1]
                    self.assertEqual(
                        'disable-model-invocation: true' in frontmatter,
                        'allow_implicit_invocation: false' in metadata,
                    )

    def test_readme_invocation_groups_match_skill_metadata(self):
        for filename, headings in (
            ('README.md', ('Requires manual invocation', 'User-invokable task Skills', 'Generally invoked automatically by the Agent')),
            ('README.zh-CN.md', ('必须由用户手动调用', '用户可主动调用的任务 Skill', '一般由 Agent 自动调用')),
        ):
            readme = (REPO_ROOT / filename).read_text(encoding='utf-8')
            listed_names = []
            usage_names = []
            for heading, manual in zip(headings, (True, False, False)):
                with self.subTest(readme=filename, heading=heading):
                    section = re.search(
                        r'^### ' + re.escape(heading) + r'\n(.*?)(?=^#{1,3} |\Z)',
                        readme,
                        re.MULTILINE | re.DOTALL,
                    )
                    self.assertIsNotNone(section)
                    names = re.findall(r'^\| `([^`]+)` \|', section.group(1), re.MULTILINE)
                    self.assertTrue(names)
                    listed_names.extend(names)
                    if heading != headings[2]:
                        usage_names.extend(re.findall(
                            r'^\| `([^`]+)` \| \[SmartKit\]', section.group(1), re.MULTILINE,
                        ))
                    for name in names:
                        with self.subTest(skill=name):
                            entry = REPO_ROOT / 'skills' / name / 'SKILL.md'
                            self.assertTrue(entry.is_file(), str(entry))
                            frontmatter = entry.read_text(encoding='utf-8').split('---', 2)[1]
                            self.assertEqual('disable-model-invocation: true' in frontmatter, manual)
            self.assertEqual(len(listed_names), len(set(listed_names)), filename)
            self.assertEqual(re.findall(r'^### `([^`]+)`$', readme, re.MULTILINE), usage_names, filename)

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
            REPO_ROOT / '.qoder-plugin' / 'plugin.json',
            REPO_ROOT / '.claude-plugin' / 'plugin.json',
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
        self.assertEqual(
            load_json('.qoder-plugin/plugin.json')['displayName'],
            'WenYue SmartKit',
        )
        self.assertFalse((REPO_ROOT / 'agents' / '.codex-plugin').exists())
        self.assertFalse((REPO_ROOT / 'agents' / 'skills').exists())
        for obsolete_manifest in (
            'plugin.json', '.plugin/plugin.json', '.github/plugin/plugin.json',
        ):
            self.assertFalse((REPO_ROOT / obsolete_manifest).exists())

    def test_local_marketplaces_point_at_the_repository_root(self):
        version = (REPO_ROOT / 'VERSION').read_text(encoding='utf-8').strip()
        for relative in (
            '.cursor-plugin/marketplace.json',
            '.qoder-plugin/marketplace.json',
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
        copilot = load_json('.claude-plugin/plugin.json')
        qoder = load_json('.qoder-plugin/plugin.json')

        self.assertEqual(codex['hooks'], './hooks/codex.json')
        self.assertEqual(cursor['hooks'], './hooks/cursor.json')
        self.assertNotIn('rules', cursor)
        self.assertEqual(copilot['hooks'], './hooks/copilot.json')
        self.assertEqual(qoder['hooks'], './hooks/qoder.json')
        self.assertEqual(codex['mcpServers'], './mcp/codex.json')
        self.assertEqual(cursor['mcpServers'], './mcp/cursor.json')
        self.assertEqual(copilot['mcpServers'], './mcp/copilot.json')
        self.assertEqual(qoder['mcpServers'], './mcp/qoder.json')
        self.assertNotIn('agents', codex)
        self.assertEqual(cursor['agents'], './agents/cursor/')
        self.assertEqual(copilot['agents'], './agents/copilot/')
        self.assertEqual(qoder['agents'], './agents/qoder/')
        for manifest, expected in (
            (codex, 'mcp/codex.json'),
            (cursor, 'mcp/cursor.json'),
            (copilot, 'mcp/copilot.json'),
            (qoder, 'mcp/qoder.json'),
        ):
            self.assertTrue((REPO_ROOT / expected).is_file())
        for manifest in (codex, cursor, copilot, qoder):
            self.assertTrue((REPO_ROOT / manifest['skills']).is_dir())
        for manifest in (cursor, copilot, qoder):
            self.assertTrue((REPO_ROOT / manifest['agents']).is_dir())
        self.assertNotIn('rules', codex)
        self.assertNotIn('rules', copilot)
        self.assertNotIn('rules', qoder)

        plugin_skills = {
            path.name
            for path in (REPO_ROOT / 'skills').iterdir()
            if path.is_dir()
        }
        custom = {
            'setup-project-agents', 'maintain-project-config', 'create-worktree', 'refactor-code', 'rename-code',
            'diagnose-agent-session', 'what-changes', 'review-for-humans', 'collect-todos',
            'what-if', 'finish-worktree',
            'write-rules-and-skills',
            'rule-code', 'rule-error-handling', 'rule-code-comment',
            'rule-cpp', 'rule-flutter', 'rule-go', 'rule-python',
        }
        self.assertEqual(
            plugin_skills,
            {*custom, *MATT_PROMOTED, *PONYTAIL_PROMOTED, 'diagram-design'},
        )
        lock = load_json('vendor/external-skills.lock.json')
        self.assertEqual(set(lock), {'sources'})
        matt = lock['sources'][0]
        self.assertEqual(matt['id'], 'mattpocock/skills')
        self.assertEqual(matt['requested_ref'], 'v1.3.1')
        self.assertEqual(
            matt['commit'],
            '24fe0ef7737efae15c87225755e9f6f5965e4888',
        )
        self.assertEqual(
            {skill['id'].split('/', 1)[1]: skill['source_path'] for skill in matt['skills']},
            MATT_PROMOTED,
        )
        ponytail = next(source for source in lock['sources'] if source['id'] == 'DietrichGebert/ponytail')
        self.assertEqual(ponytail['commit'], '9cc65d03aa2da1db7121b912d03596409ee340b8')
        self.assertEqual({skill['id'].split('/', 1)[1] for skill in ponytail['skills']},
                         PONYTAIL_PROMOTED)
        for record in ponytail['skills']:
            name = record['id'].split('/', 1)[1]
            self.assertRegex((REPO_ROOT / 'skills' / name / 'SKILL.md').read_text(encoding='utf-8'),
                             rf'(?m)^name:\s*{re.escape(name)}\s*$')
            self.assertTrue(record['patches'])
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
                / 'runtime/project_state/_vendor/tomli/__init__.py'
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
            'codex': REPO_ROOT / 'hooks/codex.json',
            'cursor': REPO_ROOT / cursor['hooks'],
            'copilot': REPO_ROOT / copilot['hooks'],
            'qoder': REPO_ROOT / qoder['hooks'],
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
                self.assertNotRegex(content, r'\bpython(?:3)?\b')

        self.assertEqual(
            set(load_json('hooks/codex.json')['hooks']),
            {'SessionStart'},
        )
        self.assertEqual(
            set(load_json('hooks/cursor.json')['hooks']),
            {'sessionStart', 'preCompact', 'preToolUse', 'stop'},
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
        self.assertEqual(
            set(load_json('hooks/qoder.json')['hooks']),
            {'SessionStart'},
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

    def test_shared_http_session_hooks_use_plugin_owned_launchers(self):
        for harness in ('codex', 'cursor', 'copilot', 'qoder'):
            content = (REPO_ROOT / ('hooks/' + harness + '.json')).read_text()
            self.assertIn('runtime/local_web/dispatch.', content.replace('\\\\', '/').replace('\\', '/'))
            self.assertIn('hook --harness ' + harness, content)
            self.assertNotIn('register', content.lower())
        codex = load_json('hooks/codex.json')['hooks']['SessionStart']
        self.assertTrue(any('fork' in group['matcher'] and any('runtime/local_web/' in handler['command'] for handler in group['hooks']) for group in codex))
        launcher = REPO_ROOT / 'runtime/local_web/dispatch.cmd'
        command = ['cmd.exe', '/d', '/c', str(launcher), '--help'] if os.name == 'nt' else ['sh', '-c', '"$1" --help', 'smartkit-web-test', str(launcher)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('usage:', result.stdout.lower())

    def test_rule_hooks_use_cross_platform_python_launchers(self):
        codex = load_json('hooks/codex.json')['hooks']
        codex_handlers = [
            handler
            for groups in codex.values()
            for group in groups
            for handler in group['hooks']
            if 'runtime/rules/dispatch.' in handler['command']
        ]
        self.assertTrue(codex_handlers)
        for handler in codex_handlers:
            self.assertIn('runtime/rules/dispatch.sh', handler['command'])
            self.assertIn('runtime\\rules\\dispatch.ps1', handler['commandWindows'])

        copilot = load_json('hooks/copilot.json')['hooks']
        copilot_handlers = [
            handler
            for handlers in copilot.values()
            for handler in handlers
            if 'runtime/rules/dispatch.' in handler['bash']
        ]
        self.assertTrue(copilot_handlers)
        for handler in copilot_handlers:
            self.assertIn('runtime/rules/dispatch.sh', handler['bash'])
            self.assertIn('runtime\\rules\\dispatch.ps1', handler['powershell'])

        copilot_powershell_handlers = [
            handler['powershell']
            for handlers in copilot.values()
            for handler in handlers
            if 'powershell' in handler
        ]
        self.assertTrue(copilot_powershell_handlers)
        for command in copilot_powershell_handlers:
            self.assertIn('$env:CLAUDE_PLUGIN_ROOT', command)
            self.assertNotIn('${PLUGIN_ROOT}', command)
        for handlers in copilot.values():
            for handler in handlers:
                self.assertIn('${CLAUDE_PLUGIN_ROOT}', handler['bash'])
                self.assertNotIn('${PLUGIN_ROOT}', handler['bash'])

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
            {'codex', 'cursor', 'copilot', 'qoder'},
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
            'qoder': REPO_ROOT / 'agents/qoder/change-set-verifier.md',
        }
        for harness, path in paths.items():
            with self.subTest(harness=harness):
                self.assertTrue(path.is_file())
                content = path.read_text(encoding='utf-8')
                self.assertIn('change-set-verification/SKILL.md', content)
                self.assertNotRegex(content, r'(?m)^model\s*[:=]')


if __name__ == '__main__':
    unittest.main()
