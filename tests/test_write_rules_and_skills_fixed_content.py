from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPOSITORY = Path(__file__).resolve().parents[1]
SCRIPTS = REPOSITORY / "skills/write-rules-and-skills/scripts"


def run_script(name, *arguments):
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / name), *map(str, arguments)],
        text=True, capture_output=True, check=False,
    )


class FixedContentTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fixed content ")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "source"
        self.candidate = self.root / "candidate"
        self.source.mkdir()
        self.candidate.mkdir()
        self.snapshot_count = 0
        self.scope = ["example/SKILL.md", "example/agents/openai.yaml", "example/assets/icon.svg"]
        self.source_files = {
            "blueprint.md": b"---\ndescription: Run the exact workflow.\n---\n",
            "agents/openai.yaml": b'interface:\n  display_name: "Fixed Skill"\n',
            "assets/icon.svg": b"<svg>\x00\xff\r\n</svg>\n",
        }
        self.declaration = {
            "version": 1,
            "fields": [
                {
                    "source": {"path": "blueprint.md", "format": "frontmatter", "key": ["description"]},
                    "target": {"path": self.scope[0], "format": "frontmatter", "key": ["description"]},
                },
                {
                    "source": {"path": "agents/openai.yaml", "format": "yaml", "key": ["interface", "display_name"]},
                    "target": {"path": self.scope[1], "format": "yaml", "key": ["interface", "display_name"]},
                },
            ],
            "files": [{"source": "assets/icon.svg", "target": self.scope[2]}],
        }
        self.write(self.scope[0], "---\nname: example\ndescription: 'Run the exact workflow.'\n---\n\n# Example\n")
        self.write(self.scope[1], "interface:\n  display_name: 'Fixed Skill'\n")
        self.write(self.scope[2], self.source_files["assets/icon.svg"])

    def write(self, relative, content):
        path = self.candidate / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)

    def freeze(self, declaration=None):
        for relative, data in self.source_files.items():
            path = self.source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        (self.source / "fixed.json").write_text(
            json.dumps(self.declaration) if declaration is None else declaration, encoding="utf-8",
        )
        self.snapshot_count += 1
        snapshot = self.root / ("snapshot-" + str(self.snapshot_count))
        arguments = ["capture", "--root", self.source, "--output", snapshot]
        for relative in ["fixed.json", *self.source_files]:
            arguments.extend(["--path", relative])
        result = run_script("candidate_evidence.py", *arguments)
        self.assertEqual(result.returncode, 0, result.stderr)
        return snapshot

    def check(self, snapshot=None, *, declaration="fixed.json", extra=(), imported=False):
        if snapshot is None:
            snapshot = self.freeze()
        arguments = [
            "--candidate-root", self.candidate, "--target-root", self.candidate,
            "--fixed-content", declaration, "--fixed-snapshot", snapshot,
        ]
        for relative in self.scope:
            arguments.extend(["--candidate-path", relative])
        if imported:
            script = """
import importlib.util, sys, types
before_path, before_bytecode = list(sys.path), sys.dont_write_bytecode
ambient = {name: types.ModuleType(name) for name in ('fixed_content', 'candidate_evidence')}
sys.modules.update(ambient)
spec = importlib.util.spec_from_file_location('consumer_checker', sys.argv[1])
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
assert sys.path == before_path and sys.dont_write_bytecode == before_bytecode
assert all(sys.modules[name] is module for name, module in ambient.items())
raise SystemExit(checker.main(sys.argv[2:]))
"""
            return subprocess.run(
                [sys.executable, "-B", "-c", script, str(SCRIPTS / "check_candidate.py"),
                 *map(str, arguments), *map(str, extra), "--", str(self.candidate / self.scope[0])],
                cwd=self.root, text=True, capture_output=True, check=False,
            )
        return run_script("check_candidate.py", *arguments, *extra, "--", self.candidate / self.scope[0])

    def test_file_import_uses_owned_support_without_search_path_or_module_replacement(self):
        result = self.check(imported=True)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))

    def test_standalone_matching_fields_files_and_unrelated_metadata_are_read_only(self):
        self.write(self.scope[1], (
            'interface:\n  display_name: "Fixed\\x20Skill" # equivalent spelling\n'
            "  future_field: {arbitrary: [one, two]}\n"
            "policy:\n  allow_implicit_invocation: false\n"
            "dependencies:\n  tools:\n    - type: mcp\n      value: {url: 'https://example.com'}\n"
            "unknown_sequence:\n- first\n- second\n"
        ))
        before = {path: (self.candidate / path).read_bytes() for path in self.scope}
        result = self.check()
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))
        self.assertEqual(before, {path: (self.candidate / path).read_bytes() for path in self.scope})

    def test_live_source_changes_do_not_replace_frozen_expectations(self):
        snapshot = self.freeze()
        (self.source / "blueprint.md").write_text("unrelated replacement", encoding="utf-8")
        (self.source / "fixed.json").unlink()
        self.assertEqual(self.check(snapshot).returncode, 0)
        self.write(self.scope[0], "---\nname: example\ndescription: unrelated replacement\n---\n")
        self.assertEqual(self.check(snapshot).returncode, 1)

    def test_every_character_and_internal_space_is_significant(self):
        for value in ("Run the exact workflow!", "Run  the exact workflow.", " Run the exact workflow."):
            with self.subTest(value=value):
                self.write(self.scope[0], "---\nname: example\ndescription: '" + value + "'\n---\n")
                result = self.check()
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("fixed field", result.stdout)

    def test_files_compare_bytes_including_line_endings(self):
        self.write(self.scope[2], self.source_files["assets/icon.svg"].replace(b"\r\n", b"\n"))
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("source bytes", result.stdout)

    def test_missing_target_file_or_field_is_a_problem(self):
        for text in (None, "interface:\n  other: text\n", "policy: {}\n"):
            with self.subTest(text=text):
                if text is None:
                    (self.candidate / self.scope[1]).unlink()
                else:
                    self.write(self.scope[1], text)
                result = self.check()
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("absent", result.stdout)

    def test_unsupported_selected_strings_are_input_errors(self):
        values = (
            ">\n    Fixed Skill", "|\n    Fixed Skill", "&value Fixed Skill", "*value",
            "!!str Fixed Skill", "[Fixed Skill]", "{name: Fixed Skill}", "true", "123",
            "null", ",Fixed Skill", "Fixed: Skill", '"Fixed\\qSkill"', '"Fixed Skill"tail',
            "'Fixed Skill'\n    continuation", '"Fixed\\uD800Skill"',
            '"Fixed\u0085Skill"', '"Fixed\u2028Skill"',
        )
        for value in values:
            with self.subTest(value=value):
                self.write(self.scope[1], "interface:\n  display_name: " + value + "\n")
                result = self.check()
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("fixed-content", result.stderr)

    def test_ambiguous_mapping_or_ancestor_is_an_input_error(self):
        cases = (
            "interface:\n  display_name: Fixed Skill\n  display_name: Fixed Skill\n",
            "interface:\n  display_name: Fixed Skill\ninterface:\n  display_name: Fixed Skill\n",
            "interface:\n  <<: *defaults\n  display_name: Fixed Skill\n",
            "<<: *defaults\ninterface:\n  display_name: Fixed Skill\n",
            "interface: {display_name: Fixed Skill}\n",
            "interface: &defaults\n  display_name: Fixed Skill\n",
            "interface:\n  display_name: Fixed Skill\n other: bad indentation\n",
            "? interface\n: display_name\n",
            "interface:\n\tdisplay_name: Fixed Skill\n",
        )
        for source in cases:
            with self.subTest(source=source):
                self.write(self.scope[1], source)
                self.assertEqual(self.check().returncode, 2)

    def test_implicit_non_strings_require_quotes_in_candidate_fields(self):
        values = (
            ".5e+2", "-.5E-2", "+.5e2", "12e+3", "0x10", "0o10", "012", "12:34:56.7",
            "2001-1-2 3:04:05", "2001-1-2\t3:04:05", "2001-01-02T03:04:05Z", "null", "true", "=", "<<",
        )
        for value in values:
            with self.subTest(value=value):
                self.source_files["agents/openai.yaml"] = (
                    "interface:\n  display_name: " + json.dumps(value) + "\n"
                ).encode("utf-8")
                snapshot = self.freeze()
                self.write(self.scope[1], "interface:\n  display_name: " + value + "\n")
                result = self.check(snapshot)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("fixed-content", result.stderr)
                self.write(self.scope[1], "interface:\n  display_name: '" + value + "'\n")
                result = self.check(snapshot)
                self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))

    def test_implicit_source_scalars_are_incomplete_even_with_another_mismatch(self):
        for value in (".5e+2", "2001-1-2 3:04:05", "=", "<<"):
            with self.subTest(value=value):
                self.source_files["blueprint.md"] = ("---\ndescription: " + value + "\n---\n").encode("utf-8")
                self.write(self.scope[0], "---\nname: example\ndescription: '" + value + "'\n---\n")
                self.write(self.scope[2], b"another mismatch")
                result = self.check()
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("source 'blueprint.md'", result.stderr)
                self.assertIn("source bytes", result.stdout)

    def test_quoted_keys_comments_and_escapes_preserve_string_values(self):
        self.source_files["agents/openai.yaml"] = b'''"interface":
  'display_name': "It's a \\u4E2D\\nline"
'''
        self.write(self.scope[1], 'interface: # mapping\n  display_name: "It\'s a 中\\nline" # value\n')
        self.assertEqual(self.check().returncode, 0)
        self.source_files["agents/openai.yaml"] = b"interface:\n  display_name: 'It''s exact'\n"
        self.write(self.scope[1], 'interface:\n  display_name: "It\'s exact"\n')
        self.assertEqual(self.check().returncode, 0)

    def test_invalid_or_missing_source_fields_are_input_errors(self):
        for source in (b"---\nother: value\n---\n", b"---\ndescription: >\n  text\n---\n", b"\xff"):
            with self.subTest(source=source):
                self.source_files["blueprint.md"] = source
                result = self.check()
                self.assertEqual(result.returncode, 2)
                self.assertIn("source 'blueprint.md'", result.stderr)

    def test_input_error_takes_precedence_over_mismatch(self):
        self.write(self.scope[1], b"\xff")
        self.write(self.scope[2], b"changed")
        result = self.check()
        self.assertEqual(result.returncode, 2)
        self.assertIn("UTF-8", result.stderr)
        self.assertIn("source bytes", result.stdout)

    def test_declaration_requires_known_schema_and_nonoverlapping_targets(self):
        original = copy.deepcopy(self.declaration)
        cases = []
        for key, value in (("version", 2), ("version", True), ("fields", {}), ("extra", [])):
            altered = copy.deepcopy(original)
            altered[key] = value
            cases.append(altered)
        cases.append({"version": 1, "fields": [], "files": []})
        altered = copy.deepcopy(original)
        altered["fields"].append(altered["fields"][0])
        cases.append(altered)
        altered = copy.deepcopy(original)
        altered["files"].append({"source": "blueprint.md", "target": self.scope[0]})
        cases.append(altered)
        altered = copy.deepcopy(original)
        parent = copy.deepcopy(altered["fields"][1])
        parent["target"]["key"] = ["interface"]
        altered["fields"].append(parent)
        cases.append(altered)
        for declaration in cases:
            with self.subTest(declaration=declaration):
                self.declaration = declaration
                self.assertEqual(self.check().returncode, 2)
        snapshot = self.freeze('{"version": 1, "version": 1, "fields": [], "files": []}')
        result = self.check(snapshot)
        self.assertEqual(result.returncode, 2)
        self.assertIn("duplicate JSON", result.stderr)

    def test_source_and_target_paths_are_confined_and_must_be_declared(self):
        for endpoint in ("source", "target"):
            for path in ("../outside.md", "/absolute.md", "C:/absolute.md", "./alias.md", "bad\\path", "uncaptured.md"):
                with self.subTest(endpoint=endpoint, path=path):
                    self.declaration["fields"][0][endpoint]["path"] = path
                    self.assertEqual(self.check().returncode, 2)
            self.declaration["fields"][0][endpoint]["path"] = (
                "blueprint.md" if endpoint == "source" else self.scope[0]
            )
        self.assertEqual(self.check(declaration="../fixed.json").returncode, 2)
        self.assertEqual(self.check(declaration="uncaptured.json").returncode, 2)

    def test_context_paths_cannot_supply_fixed_targets(self):
        context = self.scope.pop()
        result = self.check(extra=("--context-path", context))
        self.assertEqual(result.returncode, 2)
        self.assertIn("exact Candidate path set", result.stderr)

    def test_tampered_snapshot_is_an_input_error(self):
        snapshot = self.freeze()
        manifest = json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))
        (snapshot / manifest["entries"][0]["payload"]).write_bytes(b"tampered")
        result = self.check(snapshot)
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot check fixed content", result.stderr)

    def test_target_symlink_is_rejected_when_supported(self):
        target = self.candidate / self.scope[2]
        target.unlink()
        destination = self.root / "elsewhere.svg"
        destination.write_bytes(self.source_files["assets/icon.svg"])
        try:
            target.symlink_to(destination)
        except OSError as exc:
            self.skipTest("symlink creation unavailable: " + str(exc))
        result = self.check()
        self.assertEqual(result.returncode, 2)
        self.assertIn("link", result.stderr)

    def test_optional_flags_require_mapping_and_unchanged_invocation_still_works(self):
        document = self.candidate / self.scope[0]
        self.assertEqual(run_script("check_candidate.py", "--", document).returncode, 0)
        for flags in (
            ("--fixed-content", "fixed.json"),
            ("--fixed-snapshot", self.root),
            ("--fixed-content", "fixed.json", "--fixed-snapshot", self.root),
        ):
            with self.subTest(flags=flags):
                result = run_script("check_candidate.py", *flags, "--", document)
                self.assertEqual(result.returncode, 2)

    def test_help_exposes_schema_and_helper_parses_as_python_38(self):
        result = run_script("check_candidate.py", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn('"version": 1', result.stdout)
        self.assertIn("Unselected branches are not validated", result.stdout)
        ast.parse((SCRIPTS / "fixed_content.py").read_text(encoding="utf-8"), feature_version=(3, 8))

    def test_entry_does_not_create_bytecode_when_invoked_without_B(self):
        scripts = self.root / "scripts"
        scripts.mkdir()
        for name in ("check_candidate.py", "fixed_content.py", "candidate_evidence.py"):
            (scripts / name).write_bytes((SCRIPTS / name).read_bytes())
        result = subprocess.run(
            [sys.executable, str(scripts / "check_candidate.py"), "--help"],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((scripts / "__pycache__").exists())


if __name__ == "__main__":
    unittest.main()
