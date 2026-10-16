"""One command interface for local pages, diff links, and disposable artifacts."""
from __future__ import annotations

import argparse
from datetime import timedelta
import json
from pathlib import Path
import sys
from typing import Optional, Sequence

from . import artifacts, service
from .apps import diff


def create(source: Path, seconds: float) -> dict:
    source = source.resolve(strict=True)
    value = json.loads(source.read_bytes().decode("utf-8"), object_pairs_hook=artifacts._unique_object)
    if (not isinstance(value, dict) or set(value) - {"files", "public"}
            or not isinstance(value.get("files"), dict) or not value["files"]
            or not isinstance(value.get("public", []), list)
            or not all(isinstance(name, str) for name in value.get("public", []))):
        raise ValueError("input needs files mapping and an optional public filename list")
    captured = {}
    for name, location in value["files"].items():
        artifacts.filename(name)
        if not isinstance(location, str) or not location:
            raise ValueError("input file locations must be nonempty paths")
        path = (source.parent / location).resolve(strict=True)
        if not path.is_file():
            raise ValueError("input is not a regular file: " + str(path))
        captured[name] = path.read_bytes()
    if not artifacts._number(seconds):
        raise ValueError("retention seconds must be finite and positive")
    artifact = artifacts.create_artifact(captured, public_files=value.get("public", []), retention=timedelta(seconds=seconds))
    return {"id": artifact.id, "created_at": artifact.created_at, "expires_at": artifact.expires_at,
            "files": {name: {"path": str(entry.path), "public": entry.public} for name, entry in artifact.files.items()}}


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Manage SmartKit's local host at http://127.0.0.1:47821, diff links, and preview artifacts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Python 3.8+ and the full plugin are required. Resolve this entry from the
loaded plugin's local_web resource, independently of the caller's cwd.

diff input (one JSON object; --input - reads stdin):
  {"repo":"/absolute/worktree", "base":"index",
   "files":[{"id":"F1", "path":"src/example.py"}]}
One batch shares repo, a default base, and optional PR context. Each file needs
a unique id and a path; title defaults to path. A file's explicit base overrides
the batch base; at least one must be supplied. base is index (capture alongside
the local review snapshot), absent, blob:FULL_OBJECT_ID from retained evidence,
or commit:FULL_BEFORE_COMMIT_ID. Optional file base_path names the old path for
index/commit baselines, including renames. There is no implicit HEAD or base.
The tool resolves existing Git objects to a fixed blob/absence; mutable index
never appears in a returned URL. Different repositories/PRs need separate batches.
For every PR add this complete batch context:
  "pr":{"repository":"owner/name", "number":507, "head":"FULL_REVIEWED_PR_HEAD"}
repository identifies the PR-owning GitHub repository, not the source fork or
local remote. number is a positive integer; head is the full fixed reviewed OID.
The tool builds each file's HTTPS GitHub Files changed URL, including its
diff- fragment from SHA-256 of the current UTF-8 path; do not pass a complete URL.
Optional file github_anchor overrides that default with an already-observed
diff- fragment without #. No GitHub lookup is needed to generate file links.
Non-PR batches omit pr and github_anchor. Every effective PR base must be fixed,
not index. Supply review context, not a preselected PR checkout. The tool searches
this repository's existing worktrees and verifies matching commits: one binds automatically,
multiple show a selection page, none or unavailable local data goes to GitHub.
It never fetches, checks out, clones, or creates worktrees. Bound URLs keep the
selected worktree even after later edits/commits; they do not reselect by head.
Unresolved PR URLs retain the context for selection/fallback on opening.
Validate the entire batch before starting the service.
Output: per-file id, title, url, html_url, markdown, plus github_url for PRs.
Use the returned links; url/markdown keep editor-first opening, html_url requests
local HTML, and github_url opens GitHub directly. Existing issued URL parameters
remain readable; the former per-file input array is replaced by this batch object.
No registration, URL signature, baseline backup, Git write or seven-day link
expiry is created.
The URL compares the fixed blob with the current on-disk path; deletion is an
absent current side, rename needs a new link, and missing Git data is an error.
VS Code is attempted from a visible page; explicit launch failure falls back
to GitHub or HTML in the same tab. A dispatched request tries to close the tab;
if browser policy blocks closing, the page keeps manual fallback links.
GitHub may show the remote PR version. CLI exit does not prove editor display.

create input: {"files":{"report.html":"captured.html","raw/data":"input.txt"},
               "public":["report.html"]}
Source paths resolve relative to that JSON file. Creation captures all bytes,
returns id/created_at/expires_at/files, starts no server and publishes nothing.
Default artifact retention is seven days; --retention-seconds is positive and
finite. publish --id explicitly exposes only declared public files and returns
their URLs. Access/publication/restart never renew expires_at. Before creation,
at service startup and every 60 seconds, cleanup removes only positively owned
expired groups; unknown/altered/redirected groups are preserved. Cleanup failure
stops dependent creation, preserving diagnostics and completed removals.
Publication failure retains the complete group; publish its ID to retry.

ensure/hook reuse one authenticated fixed-port host. Unknown port occupation
fails without stopping its owner. status starts no process. stop ends only the
verified shared instance, when requested, never merely because a chat ends.
Private readiness/setup URLs contain an instance credential; keep them private.
They read owner-produced observations/source state without checks or repair.
Hook/CLI startup is bounded recovery, not URL-click or login startup. Diff URLs
need no reissuing after restart but require the same worktree and Git object.
Preview artifacts and canonical/project records have independent lifetimes.
Failures print diagnostics and exit 1; hook failures exit 0 to preserve sessions.

Examples (<entry> is the loaded local_web resource):
  python "<entry>" diff --input batch.json
  python "<entry>" create --input files.json
  python "<entry>" publish --id artifact-ID
  python "<entry>" ensure
  python "<entry>" status
  python "<entry>" stop
''')
    commands = parser.add_subparsers(dest="command", required=True)
    ensure = commands.add_parser("ensure", help="Start/reuse the fixed-port host and return URLs.")
    ensure.add_argument("--mode", choices=("applications", "previews"), default="applications")
    commands.add_parser("status", help="Read verified live status without starting a process.")
    commands.add_parser("stop", help="Stop only the authenticated shared host.")
    commands.add_parser("cleanup", help="Remove positively owned expired artifact groups.")
    publish = commands.add_parser("publish", help="Publish declared files without renewing artifact expiry.")
    publish.add_argument("--id", required=True)
    capture = commands.add_parser("create", help="Capture private or explicitly publishable files.")
    capture.add_argument("--input", type=Path, required=True)
    capture.add_argument("--retention-seconds", type=float, default=artifacts.DEFAULT_RETENTION.total_seconds())
    compare = commands.add_parser("diff", help="Validate a batch and return self-contained live diff URLs.")
    compare.add_argument("--input", required=True, help="JSON batch path, or - for stdin")
    hook = commands.add_parser("hook", help="Record the project and restore the host from a session hook.")
    hook.add_argument("--harness", required=True, choices=("codex", "cursor", "copilot", "qoder"))
    commands.add_parser("serve", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        if args.command == "ensure":
            value = service.ensure_service(args.mode)
        elif args.command == "status":
            state = service.load_state()
            running = service.health(state) if state else None
            value = {"running": bool(running), "service": service.service_info(state) if running else None}
        elif args.command == "stop":
            value = {"stopped": service.stop_service()}
        elif args.command == "cleanup":
            artifacts.cleanup_expired()
            value = {"cleaned": True}
        elif args.command == "create":
            value = create(args.input, args.retention_seconds)
        elif args.command == "publish":
            value = service.publish_artifact(args.id)
        elif args.command == "diff":
            content = sys.stdin.read() if args.input == "-" else Path(args.input).read_bytes().decode("utf-8")
            value = diff.links(json.loads(content, object_pairs_hook=artifacts._unique_object))
        elif args.command == "hook":
            context = service.hook_project(args.harness)
            if not context:
                return 0
            if args.harness in ("codex", "qoder"):
                value = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}
            else:
                value = {"additional_context" if args.harness == "cursor" else "additionalContext": context}
        else:
            service.serve()
            return 0
        print(json.dumps(value, ensure_ascii=True))
        return 0
    except (OSError, ValueError, OverflowError) as error:
        print("SmartKit local host failed: " + str(error), file=sys.stderr)
        return 0 if args.command == "hook" else 1
