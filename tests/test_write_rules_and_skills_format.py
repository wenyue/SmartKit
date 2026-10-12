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


SCRIPT = Path(__file__).resolve().parents[1] / "skills/write-rules-and-skills/scripts/check_markdown_format.py"
SPEC = importlib.util.spec_from_file_location("check_markdown_format", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
CHECKER = importlib.util.module_from_spec(SPEC)
with mock.patch.object(sys, "dont_write_bytecode", True):
    SPEC.loader.exec_module(CHECKER)


class MarkdownFormatTest(unittest.TestCase):
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

    def run_cli(self, directory, *paths):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, paths)],
            cwd=directory, text=True, capture_output=True, check=False,
        )

    def test_portable_help_and_explicit_files_outside_repository_are_read_only(self):
        with tempfile.TemporaryDirectory(prefix="Markdown target ") as temporary:
            directory = Path(temporary)
            help_result = self.run_cli(directory, "--help")
            self.assertEqual(help_result.returncode, 0, help_result.stderr)
            self.assertIn("not a full Markdown validator", " ".join(help_result.stdout.split()))
            clean = directory / "clean file.md"
            wrapped = directory / "wrapped file.md"
            unrelated = directory / "unrelated.md"
            clean.write_bytes(b"One paragraph.\r\n\r\nNext paragraph.\r\n")
            wrapped.write_bytes(b"First line\nsecond line\n")
            unrelated.write_bytes(b"Unrelated\nwrapped prose\n")
            before = {path.name: path.read_bytes() for path in directory.iterdir()}
            passed = self.run_cli(directory, "--", clean.name)
            self.assertEqual(passed.returncode, 0, passed.stderr)
            self.assertEqual(passed.stdout, "")
            failed = self.run_cli(directory, "--", clean.name, wrapped.name)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("wrapped file.md:2: paragraph started at line 1", failed.stdout)
            self.assertNotIn("unrelated.md", failed.stdout)
            self.assertEqual(before, {path.name: path.read_bytes() for path in directory.iterdir()})

    def test_input_failures_are_visible_and_other_files_are_still_checked(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            invalid = directory / "invalid.md"
            invalid.write_bytes(b"\xff")
            wrapped = directory / "wrapped.md"
            wrapped.write_text("First\nsecond\n", encoding="utf-8")
            result = self.run_cli(directory, "--", "missing.md", directory, invalid, wrapped)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing.md: cannot check input", result.stderr)
            self.assertIn("not a regular file", result.stderr)
            self.assertIn("invalid.md: cannot check input", result.stderr)
            self.assertIn("wrapped.md:2:", result.stdout)
            no_paths = self.run_cli(directory)
            self.assertNotEqual(no_paths.returncode, 0)

    def test_unreadable_input_reports_native_cause_without_traceback(self):
        with mock.patch.object(Path, "is_file", return_value=True):
            with mock.patch.object(Path, "read_text", side_effect=PermissionError("permission denied")):
                error = io.StringIO()
                with redirect_stderr(error):
                    self.assertNotEqual(CHECKER.main(["unreadable.md"]), 0)
                self.assertIn("permission denied", error.getvalue())
                self.assertNotIn("Traceback", error.getvalue())

    def test_script_uses_python_38_syntax(self):
        ast.parse(SCRIPT.read_text(encoding="utf-8"), feature_version=(3, 8))


if __name__ == "__main__":
    unittest.main()
