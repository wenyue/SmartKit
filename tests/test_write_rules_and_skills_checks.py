from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
import io
from unittest import mock


REPOSITORY = Path(__file__).resolve().parents[1]
SKILL = REPOSITORY / "skills/write-rules-and-skills"
SCRIPT = SKILL / "scripts/check_candidate.py"
SPEC = importlib.util.spec_from_file_location("check_candidate", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
CHECKER = importlib.util.module_from_spec(SPEC)
with mock.patch.object(sys, "dont_write_bytecode", True):
    SPEC.loader.exec_module(CHECKER)


def run_cli(directory, *arguments):
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPT), *map(str, arguments)],
        cwd=directory, text=True, capture_output=True, check=False,
    )


class ParagraphLinesTest(unittest.TestCase):
    def test_reports_every_soft_continuation_at_its_source_line(self):
        cases = (
            ("ordinary", "First line\nsecond line\nthird line\n", [(2, 1), (3, 1)]),
            ("list", "- First line\n  second line\n- New item\n", [(2, 1)]),
            ("nested list", "1. Parent\n   - Child\n     continuation\n", [(3, 2)]),
            ("checklist", "- [ ] First line\n  second line\n", [(2, 1)]),
            ("lazy list", "- First line\ncontinuation\n", [(2, 1)]),
            ("quoted", "> First line\n> second line\n", [(2, 1)]),
            ("lazy quote", "> First line\nsecond line\n", [(2, 1)]),
            ("nested quote", "> > First line\n> > second line\n", [(2, 1)]),
            ("quoted list", "> - First line\n>   second line\n", [(2, 1)]),
            ("list quote", "- > First line\n  > second line\n", [(2, 1)]),
            ("pipe prose", "Use a | b expression\nand then continue\n", [(2, 1)]),
            ("escaped hard break", "First line\\\\\nsecond line\n", [(2, 1)]),
            ("trailing tab", "First line\t\nsecond line\n", [(2, 1)]),
            ("indented continuation", "First line\n    still a paragraph\n", [(2, 1)]),
            ("after hard break", "First line  \nsecond line\nthird line\n", [(3, 1)]),
            ("non-1 ordered continuation", "First prose line\n2. is the continuation\n", [(2, 1)]),
        )
        for label, source, expected in cases:
            with self.subTest(label=label):
                self.assertEqual(CHECKER.wrapped_lines(source), expected)

    def test_preserves_meaningful_markdown_boundaries(self):
        cases = (
            ("paragraphs", "First paragraph\n\nSecond paragraph\n"),
            ("headings", "## Heading\nParagraph\n### Next heading\nOther paragraph\n"),
            ("setext", "Heading\n=======\nParagraph\n\nSecond heading\n---\n"),
            ("multiline setext", "First heading line\nsecond heading line\n===\n\nParagraph.\n"),
            ("multiline dash setext", "First heading line\nsecond heading line\n---\n\nParagraph.\n"),
            ("list boundaries", "- First\n- Second\n  - Child\n- Third\n"),
            ("ordered boundaries", "1. First\n2. Second\n3. Third\n"),
            ("rules", "Paragraph\n***\nOther paragraph\n___\nLast paragraph\n"),
            ("quote boundary", "Paragraph\n> Quoted paragraph\n\n> Next paragraph\n"),
            ("space hard break", "First line  \nsecond line  \nthird line\n"),
            ("slash hard break", "First line\\\nsecond line\n"),
            ("frontmatter", "---\ndescription: >\n  wrapped metadata\n  is preserved\n---\nParagraph\n"),
            ("BOM frontmatter", "\ufeff---\ndescription: |\n  first\n  second\n...\nParagraph\n"),
            ("backtick fence", "```python\nFirst\nsecond\n```\nParagraph\n"),
            ("literal quotes in fence", "```text\n> First example line\n> Second example line\n```\n\nParagraph.\n"),
            ("literal lists in fence", "```text\n- First example line\n  > Second example line\n```\n\nParagraph.\n"),
            ("literal nested quote in fence", "> ```text\n> > First example line\n> > Second example line\n> ```\n"),
            ("tilde fence", "~~~~\nFirst\n~~~\nsecond\n~~~~~\nParagraph\n"),
            ("list fence", "- Item\n\n  ```text\n  First\n  second\n  ```\n\n  Paragraph\n"),
            ("nested fence", "> 1. Item\n>\n>    ~~~\n>    First\n>    second\n>    ~~~\n"),
            ("list quote fence", "- > ```\n  > First\n  > second\n  > ```\n"),
            ("indented code", "    First\n    second\n\nParagraph\n"),
            ("list indented code", "- Item\n\n      First\n      second\n"),
            ("tab code", "\tFirst\n\tsecond\n"),
            ("table", "A | B\n--- | :---:\none | two\nthree | four\n\nParagraph\n"),
            ("quoted table", "> | A | B |\n> | --- | --- |\n> | one | two |\n"),
            ("link definition", '[label]: https://example.com\n  "A title"\n\nParagraph\n'),
            ("unindented link title", '[guide]: https://example.com\n"A title"\nParagraph.\n'),
            ("multiline link title", '[guide]: https://example.com\n"First title line\nsecond title line"\nParagraph.\n'),
            ("parenthesized link title", '[guide]: https://example.com\n(A title)\nParagraph.\n'),
            ("HTML comment", "<!--\nfirst\nsecond\n-->\nParagraph\n"),
            ("HTML block", "<div>\nfirst\nsecond\n</div>\n\nParagraph\n"),
            ("HTML raw", "<pre>\nfirst\n\nsecond\n</pre>\nParagraph\n"),
            ("HTML CDATA", "<![CDATA[\nfirst\nsecond\n]]>\nParagraph\n"),
            ("standalone HTML tags", "<user-story-example>\n1. An example\n</user-story-example>\n\nParagraph\n"),
        )
        for label, source in cases:
            with self.subTest(label=label):
                self.assertEqual(CHECKER.wrapped_lines(source), [])

    def test_code_exemption_ends_before_following_prose(self):
        source = "```\ncode\n```\nFirst\nsecond\n\n~~~\ncode\n~~~\nOther\ncontinuation\n"
        self.assertEqual(CHECKER.wrapped_lines(source), [(5, 4), (11, 10)])

    def test_unclosed_leading_rule_is_not_frontmatter(self):
        self.assertEqual(CHECKER.wrapped_lines("---\nFirst\nsecond\n"), [(3, 2)])


class RelativeLinksTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="link check ")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "references").mkdir()
        (self.root / "references/guide.md").write_text(
            "# Guide\n\n## Run `tool.py` --help!\n\n## Repeat\n\n## Repeat\n\n"
            "Café menu\n---\n\n<a id=\"custom-anchor\"></a>\n\n"
            "```text\n## Not a heading\n```\n",
            encoding="utf-8",
        )
        (self.root / "image.png").write_bytes(b"png")
        (self.root / "my file.md").write_text("# Spaced\n", encoding="utf-8")

    def findings(self, source):
        document = self.root / "doc.md"
        document.write_text(source, encoding="utf-8")
        cache = {}

        def anchors(path):
            if path not in cache:
                cache[path] = CHECKER.heading_anchors(CHECKER.read_markdown(path))
            return cache[path]

        return [
            (finding.line, finding.message)
            for finding in CHECKER.check_relative_links(CHECKER.Document(document, source, anchors))
        ]

    def test_resolves_files_directories_and_github_anchors(self):
        source = "\n".join((
            "# Local heading",
            "[Guide](references/guide.md) and [section](references/guide.md#run-toolpy---help).",
            "[Repeat](references/guide.md#repeat) [again](references/guide.md#repeat-1).",
            "[Setext](references/guide.md#café-menu) [encoded](references/guide.md#caf%C3%A9-menu).",
            "[HTML](references/guide.md#custom-anchor) [dir](references/) [image](image.png)",
            "![Image](image.png \"title\") [spaced](my%20file.md) [angle](<my file.md#spaced>)",
            "[self](#local-heading) [top](#) [query](references/guide.md?plain=1#guide)",
            "| [In table](references/guide.md) | cell |",
            "[label]: references/guide.md#guide",
            "[^note]: Footnote text is not a target.",
            "[External](https://example.com/missing.md) [mail](mailto:a@example.com) [net](//example.com/x)",
            "[Root](/not/resolved.md)",
        )) + "\n"
        self.assertEqual(self.findings(source), [])

    def test_reports_missing_targets_and_anchors_at_their_lines(self):
        source = "\n".join((
            "# Title",
            "[Missing](references/missing.md)",
            "[Bad anchor](references/guide.md#absent) [Code heading](references/guide.md#not-a-heading)",
            "[Self](#nowhere)",
            "[Empty]()",
            "[ref]: missing-reference.md",
        )) + "\n"
        self.assertEqual(self.findings(source), [
            (2, "link target does not exist: references/missing.md"),
            (3, "anchor #absent matches no heading or HTML anchor in references/guide.md"),
            (3, "anchor #not-a-heading matches no heading or HTML anchor in references/guide.md"),
            (4, "anchor #nowhere matches no heading or HTML anchor in this file"),
            (5, "link has an empty target"),
            (6, "link target does not exist: missing-reference.md"),
        ])

    def test_skips_code_frontmatter_and_unverifiable_fragments(self):
        (self.root / "tool.py").write_text("print()\n", encoding="utf-8")
        source = "\n".join((
            "---",
            "description: see [x](missing-in-frontmatter.md)",
            "---",
            "Use `[x](missing-in-span.md)` literally.",
            "```markdown",
            "[x](missing-in-fence.md)",
            "```",
            "> ~~~",
            "> [x](missing-in-quoted-fence.md)",
            "> ~~~",
            "[Code line](tool.py#L1) [Dir fragment](references/#anything)",
            "Escaped \\[x\\](missing-escaped.md) and wrapped [x](continues",
            "onto-next-line.md)",
        )) + "\n"
        self.assertEqual(self.findings(source), [])

    def test_unreadable_link_target_is_an_input_error(self):
        (self.root / "bad.md").write_bytes(b"\xff")
        document = self.root / "doc.md"
        document.write_text("[Bad](bad.md#x) [Missing](gone.md)\n", encoding="utf-8")
        result = run_cli(self.root, "--", document.name)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("doc.md:1: relative-links: link target does not exist: gone.md", result.stdout)
        self.assertIn("doc.md:1: relative-links: cannot read link target bad.md to resolve #x", result.stderr)

    def test_uninspectable_link_target_is_an_input_error(self):
        document = CHECKER.Document(self.root / "doc.md", "", lambda path: set())
        with mock.patch.object(Path, "exists", side_effect=PermissionError("permission denied")):
            finding = CHECKER.check_link(document, 3, "locked/target.md")
        self.assertEqual(finding, CHECKER.Finding(
            3, "cannot inspect link target locked/target.md: permission denied", True
        ))

    def test_unmapped_self_anchor_reads_the_same_symlink_parent_path_as_input(self):
        outside = self.root / "outside"
        (outside / "child").mkdir(parents=True)
        (outside / "review.md").write_text("# Outside\n\n[Self](#outside).\n", encoding="utf-8")
        (self.root / "review.md").write_text("# Candidate\n", encoding="utf-8")
        try:
            (self.root / "alias").symlink_to(outside / "child", target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        paths = (outside / "review.md", Path("alias/../review.md"),
                 self.root / "alias/../review.md")
        for path in paths:
            with self.subTest(path=path):
                result = run_cli(self.root, "--", path)
                self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))

    def test_unclosed_leading_rule_is_not_frontmatter(self):
        self.assertEqual(self.findings("---\n[x](missing.md)\n"), [
            (2, "link target does not exist: missing.md"),
        ])

    def test_slug_rules(self):
        cases = (
            ("Manage checks and repairs", "manage-checks-and-repairs"),
            ("Write agents/openai.yaml", "write-agentsopenaiyaml"),
            ("Use `snake_case` names", "use-snake_case-names"),
            ("A [linked](x.md) heading", "a-linked-heading"),
            ("Résumé — notes", "résumé--notes"),
            ("  Trailing #  ", "trailing-"),
        )
        for heading, slug in cases:
            with self.subTest(heading=heading):
                self.assertEqual(CHECKER.github_slug(heading), slug)


class MappedLinksTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mapped links ")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.candidate = self.root / "generated"
        self.target = self.root / "business"
        self.candidate.mkdir()
        self.target.mkdir()
        self.document = ".agents/rules/example.md"

    def write(self, root, relative, text):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def check(self, source, *scope):
        document = self.write(self.candidate, self.document, source)
        arguments = ["--candidate-root", self.candidate, "--target-root", self.target]
        for path in (self.document, *scope):
            arguments.extend(("--candidate-path", path))
        return run_cli(self.root, *arguments, "--", document)

    def test_retained_targets_supply_anchors_without_scanning_their_prose(self):
        retained = self.write(self.target, "docs/guide.md", "# Guide\n\nWrapped\nprose\n")
        source = "# Candidate\n\n[Guide](../../docs/guide.md?plain=1#guide) [Self](#candidate).\n"
        self.write(self.target, self.document, "# Stale target\n")
        result = self.check(source)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))
        self.assertEqual(retained.read_text(), "# Guide\n\nWrapped\nprose\n")
        missing_anchor = self.check(source.replace("#guide", "#missing"))
        self.assertEqual(missing_anchor.returncode, 1, missing_anchor.stderr)
        self.assertIn("anchor #missing", missing_anchor.stdout)

    def test_scoped_content_and_absence_override_stale_target_files(self):
        guide = ".agents/rules/guide.md"
        self.write(self.target, guide, "# Stale\n")
        self.write(self.candidate, guide, "# Current\n")
        source = "[Guide](guide.md#current).\n"
        self.assertEqual(self.check(source, guide).returncode, 0)
        stale = self.check("[Guide](guide.md#stale).\n", guide)
        self.assertEqual(stale.returncode, 1, stale.stderr)
        self.assertIn("anchor #stale", stale.stdout)
        (self.candidate / guide).unlink()
        deleted = self.check("[Guide](guide.md#stale).\n", guide)
        self.assertEqual(deleted.returncode, 1, deleted.stderr)
        self.assertIn("link target does not exist", deleted.stdout)
        missing = self.check("[Missing](missing.md).\n", ".agents/rules/missing.md")
        self.assertEqual(missing.returncode, 1, missing.stderr)

    def test_unscoped_staging_files_cannot_supply_retained_targets(self):
        self.write(self.candidate, "docs/guide.md", "# Unscoped\n")
        result = self.check("[Guide](../../docs/guide.md#unscoped).\n")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.write(self.target, "docs/guide.md", "# Retained\n")
        result = self.check("[Guide](../../docs/guide.md#retained).\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_scoped_surviving_descendants_supply_new_directory_targets(self):
        resource = ".agents/rules/resources/image.png"
        self.write(self.candidate, resource, "image")
        result = self.check("[Resources](resources/).\n", resource)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = self.check("[Resources](resources/).\n")
        self.assertEqual(result.returncode, 1, result.stderr)

    def test_mapping_keeps_all_document_checks_and_input_error_precedence(self):
        target = self.write(self.target, "docs/bad.md", "")
        target.write_bytes(b"\xff")
        result = self.check("First\nsecond [Bad](../../docs/bad.md#x).\n")
        self.assertEqual(result.returncode, 2)
        self.assertIn("paragraph-lines", result.stdout)
        self.assertIn("cannot read link target", result.stderr)
        self.document = ".agents/skills/example/SKILL.md"
        result = self.check("# Missing metadata\n")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("skill-frontmatter", result.stdout)

    def test_mapping_rejects_namespace_escape_and_incomplete_options(self):
        self.write(self.root, "outside.md", "# Outside\n")
        escaped = self.check("[Outside](../../../outside.md#outside).\n")
        self.assertEqual(escaped.returncode, 2)
        self.assertIn("link leaves --target-root", escaped.stderr)
        encoded = self.check("[Outside](%2e%2e/%2e%2e/%2e%2e/outside.md).\n")
        self.assertEqual(encoded.returncode, 2)
        document = self.candidate / self.document
        for option, value in (("--candidate-root", self.candidate),
                              ("--target-root", self.target),
                              ("--candidate-path", self.document)):
            with self.subTest(option=option):
                result = run_cli(self.root, option, value, "--", document)
                self.assertEqual(result.returncode, 2)
                self.assertIn("mapping requires", result.stderr)
        for invalid in ("../outside.md", "/absolute", "C:outside.md", "a\\b", "."):
            with self.subTest(path=invalid):
                result = self.check("# Good\n", invalid)
                self.assertEqual(result.returncode, 2)
                self.assertIn("relative POSIX file path", result.stderr)

    def test_explicit_inputs_must_belong_to_candidate_scope(self):
        document = self.write(self.candidate, self.document, "# Good\n")
        outside = self.write(self.target, "outside.md", "# Outside\n")
        for path in (document, outside):
            with self.subTest(path=path):
                result = run_cli(self.root, "--candidate-root", self.candidate,
                                 "--target-root", self.target, "--candidate-path", "other.md",
                                 "--", path)
                self.assertEqual(result.returncode, 2)
                self.assertIn("input is outside", result.stderr)

    def test_mapped_input_reads_the_validated_path_after_parent_normalization(self):
        outside = self.root / "outside"
        (outside / "child").mkdir(parents=True)
        try:
            (self.candidate / "alias").symlink_to(outside / "child", target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        cases = (
            ("broken link", "# Candidate\n\n[Self](#candidate) [Missing](missing.md).\n",
             "# Outside\n", 1),
            ("self anchor", "# Candidate\n\n[Self](#candidate).\n",
             "# Outside\n\n[Self](#outside).\n", 0),
        )
        for label, source, outside_source, expected in cases:
            with self.subTest(case=label):
                document = self.write(self.candidate, "review.md", source)
                self.write(outside, "review.md", outside_source)
                arguments = ["--candidate-root", self.candidate, "--target-root", self.target,
                             "--candidate-path", "review.md", "--"]
                direct = run_cli(self.root, *arguments, document)
                aliased = run_cli(self.root, *arguments, self.candidate / "alias/../review.md")
                self.assertEqual(direct.returncode, expected, direct.stdout + direct.stderr)
                self.assertEqual(aliased.returncode, expected, aliased.stdout + aliased.stderr)
                self.assertEqual(aliased.stderr, "")
                if expected:
                    self.assertIn("link target does not exist: missing.md", aliased.stdout)
                    self.assertNotIn("anchor #candidate", aliased.stdout)
                else:
                    self.assertEqual(aliased.stdout, "")

    def test_mapped_symlinks_cannot_escape_or_alias_stale_candidate_content(self):
        outside = self.write(self.root, "outside.md", "# Outside\n")
        for root in (self.candidate, self.target):
            link = root / "docs/guide.md"
            link.parent.mkdir(parents=True, exist_ok=True)
            try:
                link.symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"symlinks unavailable: {exc}")
            scope = ("docs/guide.md",) if root == self.candidate else ()
            result = self.check("[Guide](../../docs/guide.md#outside).\n", *scope)
            self.assertEqual(result.returncode, 2)
            self.assertIn("traverses a link", result.stderr)
            link.unlink()

    # Setup reviews each generated artifact separately and applies them together later.
    def check_with_context(self, source, *context):
        document = self.write(self.candidate, self.document, source)
        arguments = ["--candidate-root", self.candidate, "--target-root", self.target,
                     "--candidate-path", self.document]
        for path in context:
            arguments.extend(("--context-path", path))
        return run_cli(self.root, *arguments, "--", document)

    def test_context_paths_supply_accepted_sibling_candidates(self):
        sibling = ".agents/skills/sibling/SKILL.md"
        self.write(self.candidate, sibling, "# Sibling\n\n## New Section\n")
        source = "[Sibling](../skills/sibling/SKILL.md#new-section).\n"
        without_context = self.check(source)
        self.assertEqual(without_context.returncode, 1, without_context.stderr)
        result = self.check_with_context(source, sibling)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))
        directory = self.check_with_context("[Sibling](../skills/sibling/).\n", sibling)
        self.assertEqual(directory.returncode, 0, directory.stdout + directory.stderr)

    def test_context_content_and_absence_override_stale_target_files(self):
        sibling = ".agents/skills/sibling/SKILL.md"
        self.write(self.target, sibling, "# Sibling\n\n## Old Section\n")
        self.write(self.candidate, sibling, "# Sibling\n\n## Current\n")
        current = self.check_with_context("[Now](../skills/sibling/SKILL.md#current).\n", sibling)
        self.assertEqual(current.returncode, 0, current.stdout + current.stderr)
        stale = self.check_with_context("[Old](../skills/sibling/SKILL.md#old-section).\n", sibling)
        self.assertEqual(stale.returncode, 1, stale.stderr)
        self.assertIn("anchor #old-section", stale.stdout)
        (self.candidate / sibling).unlink()
        deleted = self.check_with_context("[Sibling](../skills/sibling/SKILL.md).\n", sibling)
        self.assertEqual(deleted.returncode, 1, deleted.stderr)
        self.assertIn("link target does not exist", deleted.stdout)

    def test_context_paths_are_read_only_link_context_not_inputs(self):
        sibling = self.write(self.candidate, ".agents/rules/sibling.md", "Wrapped\nprose\n")
        result = self.check_with_context("[Sibling](sibling.md).\n", ".agents/rules/sibling.md")
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))
        as_input = run_cli(self.root, "--candidate-root", self.candidate, "--target-root", self.target,
                           "--candidate-path", self.document,
                           "--context-path", ".agents/rules/sibling.md", "--", sibling)
        self.assertEqual(as_input.returncode, 2)
        self.assertIn("input is outside", as_input.stderr)
        self.assertEqual(sibling.read_text(), "Wrapped\nprose\n")

    def test_context_paths_need_mapping_and_valid_paths_disjoint_from_scope(self):
        document = self.write(self.candidate, self.document, "# Good\n")
        alone = run_cli(self.root, "--context-path", "other.md", "--", document)
        self.assertEqual((alone.returncode, alone.stdout), (2, ""))
        self.assertNotIn("unrecognized arguments", alone.stderr)
        for invalid in ("../outside.md", "/absolute", "a\\b", ".", self.document):
            with self.subTest(path=invalid):
                result = self.check_with_context("# Good\n", invalid)
                self.assertEqual((result.returncode, result.stdout), (2, ""))
                self.assertIn("--context-path", result.stderr)
                self.assertNotIn("unrecognized arguments", result.stderr)

    def test_context_path_link_traversal_names_the_option(self):
        outside = self.write(self.root, "outside.md", "# Outside\n")
        link = self.candidate / "docs"
        try:
            link.symlink_to(outside.parent)
        except OSError as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        result = self.check_with_context("# Good\n", "docs/outside.md")
        self.assertEqual((result.returncode, result.stdout), (2, ""))
        self.assertIn("--context-path", result.stderr)
        self.assertIn("traverses a link", result.stderr)


class SkillFrontmatterTest(unittest.TestCase):
    def findings(self, text, directory="my-skill", name="SKILL.md"):
        path = Path("/virtual") / directory / name
        document = CHECKER.Document(path, text, lambda target: set())
        return [(finding.line, finding.message) for finding in CHECKER.check_skill_frontmatter(document)]

    def test_accepts_supported_scalar_forms(self):
        cases = (
            "---\nname: my-skill\ndescription: Do one task.\n---\n# Body\n",
            "---\nname: \"my-skill\" # comment\ndescription: 'It''s quoted.'\n---\n",
            "---\nname: my-skill\ndescription: >-\n  Folded text\n  continues.\nmetadata:\n  owner: x\n...\n",
            "---\nname: my-skill\ndescription: |\n  Literal\n---\n",
            "---\nname: my-skill\ndescription: Plain text\n  continued on the next line.\n---\n",
            "---\nname: my-skill\ndescription: \"Escaped \\\"quote\\\"\"\ndisable-model-invocation: true\n---\n",
            "---\nname: my-skill\ndescription: x\nallowed-tools:\n- Bash\n- Read\n---\n",
            "---\nname: my-skill\nallowed-tools: # tools\n- Bash\n# more\n- Read\ndescription: x\n---\n",
            "---\n\"name\": my-skill\nallowed tools: Bash\ndescription: 'Use when: a colon appears.'\n---\n",
            "---\nname: my-skill\ndescription:\n  Plain text on the next line.\nlicense: MIT\nlicense: MIT\n---\n",
        )
        for source in cases:
            with self.subTest(source=source):
                self.assertEqual(self.findings(source), [])

    def test_ignores_files_not_named_skill_md(self):
        self.assertEqual(self.findings("No frontmatter\n", name="example.md"), [])

    def test_reports_frontmatter_problems(self):
        cases = (
            ("missing", "# Title\n", [(1, "SKILL.md must begin with a '---' YAML frontmatter line")]),
            ("unclosed", "---\nname: my-skill\n", [(1, "frontmatter is not closed by a '---' line")]),
            ("mismatch", "---\nname: other\ndescription: x\n---\n",
             [(2, "name 'other' does not match the containing directory 'my-skill'")]),
            ("empty description", "---\nname: my-skill\ndescription: \"\"\n---\n", [(3, "description is empty")]),
            ("null description", "---\nname: my-skill\ndescription:\n---\n", [(3, "description is empty")]),
            ("absent fields", "---\nlicense: MIT\n---\n",
             [(1, "frontmatter has no name field"), (1, "frontmatter has no description field")]),
            ("unsupported", "---\nname: [my-skill]\ndescription:\n  - list\n---\n",
             [(2, "name is not a plain, quoted, or block string this check can read"),
              (3, "description is not a plain, quoted, or block string this check can read")]),
            ("duplicate", "---\nname: my-skill\ndescription: x\nname: my-skill\n---\n",
             [(4, "duplicate frontmatter key 'name'")]),
            ("unparsed", "---\nname: my-skill\ndescription: x\n- stray\n---\n",
             [(4, "cannot read this frontmatter line as a top-level 'key: value' entry")]),
            ("second block", "---\nname: my-skill\ndescription: x\n---\n\n---\nother: y\n---\n",
             [(6, "a second YAML block follows the frontmatter; keep metadata in one block")]),
            ("plain mapping", "---\nname: my-skill\ndescription: Use when: X\n---\n",
             [(3, "description is plain text containing ': ' or ending in ':', which YAML reads as a "
                  "mapping; quote it or use a | or > block scalar")]),
            ("plain trailing colon", "---\nname: my-skill\ndescription: Use\n  when:\n---\n",
             [(3, "description is plain text containing ': ' or ending in ':', which YAML reads as a "
                  "mapping; quote it or use a | or > block scalar")]),
            ("comment only", "---\nname: my-skill\ndescription: # none\n---\n", [(3, "description is empty")]),
        )
        for label, source, expected in cases:
            with self.subTest(label=label):
                self.assertEqual(self.findings(source), expected)

    def test_rule_after_frontmatter_is_not_a_second_block(self):
        source = "---\nname: my-skill\ndescription: x\n---\n\n---\n\nParagraph\n"
        self.assertEqual(self.findings(source), [])


class EntryTest(unittest.TestCase):
    def test_help_names_every_check_with_its_limits_and_contract(self):
        with tempfile.TemporaryDirectory(prefix="Markdown target ") as temporary:
            result = run_cli(temporary, "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        text = " ".join(result.stdout.split())
        for check in CHECKS_WITH_LIMITS:
            with self.subTest(check=check[0]):
                self.assertIn(check[0], text)
                self.assertIn(check[1], text)
        self.assertEqual(
            [check.name for check in CHECKER.CHECKS], [check[0] for check in CHECKS_WITH_LIMITS]
        )
        self.assertIn("'path:line: check-name: message'", text)
        self.assertIn("Exit 2: usage or input error", text)

    def test_explicit_files_outside_repository_are_read_only(self):
        with tempfile.TemporaryDirectory(prefix="Markdown target ") as temporary:
            directory = Path(temporary)
            clean = directory / "clean file.md"
            wrapped = directory / "wrapped file.md"
            unrelated = directory / "unrelated.md"
            clean.write_bytes(b"One paragraph.\r\n\r\nNext paragraph.\r\n")
            wrapped.write_bytes(b"First line\nsecond line\n[x](absent.md)\n")
            unrelated.write_bytes(b"Unrelated\nwrapped prose\n")
            before = {path.name: path.read_bytes() for path in directory.iterdir()}
            passed = run_cli(directory, "--", clean.name)
            self.assertEqual((passed.returncode, passed.stdout, passed.stderr), (0, "", ""))
            failed = run_cli(directory, "--", clean.name, wrapped.name)
            self.assertEqual(failed.returncode, 1, failed.stderr)
            self.assertEqual(failed.stderr, "")
            self.assertEqual(failed.stdout.splitlines(), [
                "wrapped file.md:2: paragraph-lines: paragraph started at line 1 continues on another physical line",
                "wrapped file.md:3: paragraph-lines: paragraph started at line 1 continues on another physical line",
                "wrapped file.md:3: relative-links: link target does not exist: absent.md",
            ])
            self.assertNotIn("unrelated.md", failed.stdout)
            self.assertEqual(before, {path.name: path.read_bytes() for path in directory.iterdir()})

    def test_skill_directory_name_comes_from_the_passed_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            skill = Path(temporary) / "demo-skill"
            skill.mkdir()
            (skill / "SKILL.md").write_text("---\nname: demo\ndescription: x\n---\n", encoding="utf-8")
            result = run_cli(temporary, "--", "demo-skill/SKILL.md")
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(
                result.stdout,
                "demo-skill/SKILL.md:2: skill-frontmatter: name 'demo' does not match the containing directory 'demo-skill'\n",
            )

    def test_input_errors_exit_2_and_other_files_are_still_checked(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            invalid = directory / "invalid.md"
            invalid.write_bytes(b"\xff")
            wrapped = directory / "wrapped.md"
            wrapped.write_text("First\nsecond\n", encoding="utf-8")
            result = run_cli(directory, "--", "missing.md", directory, invalid, wrapped)
            self.assertEqual(result.returncode, 2)
            self.assertIn("missing.md: cannot check input", result.stderr)
            self.assertIn("not a regular file", result.stderr)
            self.assertIn("invalid.md: cannot check input", result.stderr)
            self.assertIn("wrapped.md:2: paragraph-lines:", result.stdout)
            self.assertNotIn("cannot check input", result.stdout)
            only_input_error = run_cli(directory, "--", "missing.md")
            self.assertEqual((only_input_error.returncode, only_input_error.stdout), (2, ""))
            no_paths = run_cli(directory)
            self.assertEqual(no_paths.returncode, 2)
            self.assertIn("usage:", no_paths.stderr)
            self.assertEqual(no_paths.stdout, "")

    def test_unreadable_input_reports_native_cause_without_traceback(self):
        with mock.patch.object(Path, "is_file", return_value=True):
            with mock.patch.object(Path, "read_text", side_effect=PermissionError("permission denied")):
                error = io.StringIO()
                with redirect_stderr(error):
                    self.assertEqual(CHECKER.main(["unreadable.md"]), 2)
                self.assertIn("permission denied", error.getvalue())
                self.assertNotIn("Traceback", error.getvalue())

    def test_skill_markdown_passes_every_check(self):
        files = sorted(SKILL.rglob("*.md"))
        self.assertTrue(files)
        result = run_cli(REPOSITORY, "--", *files)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_script_uses_python_38_syntax(self):
        ast.parse(SCRIPT.read_text(encoding="utf-8"), feature_version=(3, 8))


CHECKS_WITH_LIMITS = (
    ("paragraph-lines", "not a full Markdown validator"),
    ("relative-links", "URLs are never fetched"),
    ("skill-frontmatter", "Applies only to files named SKILL.md"),
)


if __name__ == "__main__":
    unittest.main()
