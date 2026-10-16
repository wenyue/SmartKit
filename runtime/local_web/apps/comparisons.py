"""Resolve review context to fixed baselines and existing local worktrees."""
from __future__ import annotations

from dataclasses import dataclass, replace
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
from typing import List, Mapping, Optional, Tuple
from urllib.parse import parse_qs, urlencode, urlsplit

from .. import ORIGIN
from ..storage import redirected


@dataclass(frozen=True)
class Target:
    repo: Path
    path: str
    base: str
    github: Optional[str] = None
    head: Optional[str] = None
    base_path: Optional[str] = None

    def query(self) -> str:
        values = {"repo": str(self.repo), "path": self.path, "base": self.base}
        if self.github:
            values["github"] = self.github
        if self.head:
            values["head"] = self.head
        if self.base_path:
            values["base_path"] = self.base_path
        return urlencode(values)

    def url(self, *, html_only: bool = False) -> str:
        return ORIGIN + ("/diff/html?" if html_only else "/diff?") + self.query()


@dataclass(frozen=True)
class Comparison:
    target: Target
    before: Optional[bytes]
    after: Optional[bytes]
    worktree_file: Path


@dataclass(frozen=True)
class Resolution:
    targets: Tuple[Target, ...]
    message: str = ""


def validate_base(base: object) -> None:
    if not isinstance(base, str) or (base not in ("absent", "index")
            and re.fullmatch(r"(?:blob|commit):(?:[0-9a-f]{40}|[0-9a-f]{64})", base) is None):
        raise ValueError("base must be index, absent, blob:<full OID>, or commit:<full OID>")


def github_pr_url(repository: str, number: int) -> str:
    """Build a Files changed URL from the PR-owning repository and number."""
    if (not isinstance(repository, str)
            or re.fullmatch(r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+", repository) is None
            or repository.split("/")[1] in (".", "..")):
        raise ValueError("pr.repository must be a GitHub owner/name, not a URL")
    if type(number) is not int or number < 1:
        raise ValueError("pr.number must be a positive integer")
    return "https://github.com/" + repository + "/pull/" + str(number) + "/files"


def target_from_fields(fields: Mapping[str, str]) -> Target:
    if set(fields) - {"repo", "path", "base", "github", "head", "base_path"} or not {"repo", "path", "base"} <= set(fields):
        raise ValueError("diff needs repo, path, base, and optional github/head/base_path context")
    if not all(isinstance(value, str) and value and not any(ord(c) < 32 for c in value) for value in fields.values()):
        raise ValueError("diff parameters must be nonempty single-line strings")
    repo = Path(fields["repo"])
    if not repo.is_absolute():
        raise ValueError("repo must be an absolute worktree root")
    for name in (fields["path"], fields.get("base_path", fields["path"])):
        if (PurePosixPath(name).is_absolute() or "\\" in name or ":" in name
                or any(part in ("", ".", "..") or part.lower() == ".git" for part in name.split("/"))):
            raise ValueError("path must be a confined worktree-relative file")
    base = fields["base"]
    validate_base(base)
    if "base_path" in fields and not (base == "index" or base.startswith("commit:")):
        raise ValueError("base_path only applies to an index or commit baseline")
    github = fields.get("github")
    if github:
        parsed = urlsplit(github)
        if (parsed.scheme != "https" or parsed.netloc != "github.com"
                or re.fullmatch(r"/[^/]+/[^/]+/pull/[1-9][0-9]*(?:/files)?/?", parsed.path) is None):
            raise ValueError("github must be an HTTPS GitHub PR or Files changed URL")
    head = fields.get("head")
    if head and (re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", head) is None or not github or base == "index"):
        raise ValueError("PR head needs a full commit OID, github URL, and a fixed baseline")
    return Target(repo, fields["path"], base, github, head, fields.get("base_path"))


def target_from_query(query: str) -> Target:
    fields = parse_qs(query, keep_blank_values=True, strict_parsing=True, max_num_fields=6)
    if any(len(values) != 1 for values in fields.values()):
        raise ValueError("duplicate diff parameter")
    target = target_from_fields({name: values[0] for name, values in fields.items()})
    if target.base == "index":
        raise ValueError("URLs must pin a baseline; index is a link-generation input only")
    return target


def git(repo: Path, *arguments: str) -> bytes:
    environment = {name: value for name, value in os.environ.items() if not name.startswith("GIT_")}
    try:
        result = subprocess.run(["git", "--no-replace-objects", "-C", str(repo)] + list(arguments),
                                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                env=environment, timeout=10)
    except subprocess.TimeoutExpired as error:
        raise TimeoutError("Git comparison timed out") from error
    if result.returncode:
        raise OSError("Git comparison unavailable: " + result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def worktree_root(repo: Path) -> Path:
    root = repo.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("worktree root is unavailable")
    actual = Path(os.fsdecode(git(root, "rev-parse", "--show-toplevel")).strip()).resolve(strict=True)
    if actual != root:
        raise ValueError("repo must identify the exact worktree root")
    return root


def pin_baseline(target: Target) -> Target:
    """Resolve existing index/commit content without writing Git objects."""
    if target.base == "absent" or target.base.startswith("blob:"):
        return target
    name = target.base_path or target.path
    root = worktree_root(target.repo)
    if target.base == "index":
        records = git(root, "--literal-pathspecs", "ls-files", "--stage", "-z", "--", name)
    else:
        commit = target.base[len("commit:"):]
        if git(root, "cat-file", "-t", commit).strip() != b"commit":
            raise ValueError("before commit is not a Git commit")
        records = git(root, "--literal-pathspecs", "ls-tree", "--full-tree", "-z", commit, "--", name)
    entries = [entry for entry in records.split(b"\0") if entry]
    if not entries:
        base = "absent"
    else:
        if len(entries) != 1:
            raise ValueError("baseline path has unresolved or ambiguous entries")
        metadata, separator, filename = entries[0].partition(b"\t")
        parts = metadata.split()
        if not separator or os.fsdecode(filename) != name or len(parts) != 3:
            raise ValueError("unexpected Git baseline entry")
        if target.base == "index":
            if parts[2] != b"0":
                raise ValueError("index baseline is unmerged")
            oid = parts[1]
        else:
            if parts[1] != b"blob":
                raise ValueError("baseline path is not a file")
            oid = parts[2]
        base = "blob:" + oid.decode("ascii")
    return replace(target, base=base, base_path=None)


def pr_worktrees(target: Target) -> List[Path]:
    """Find live checkouts of the reviewed head in this repository only."""
    root = worktree_root(target.repo)

    def common_directory(repo: Path) -> Path:
        directory = Path(os.fsdecode(git(repo, "rev-parse", "--git-common-dir")).strip())
        return (repo / directory).resolve(strict=True)

    common = common_directory(root)
    result = []
    records = git(root, "worktree", "list", "--porcelain", "-z")
    for record in records.split(b"\0\0"):
        fields = {}
        for field in record.split(b"\0"):
            if field:
                name, _, value = field.partition(b" ")
                fields[name] = value
        if fields.get(b"HEAD") != target.head.encode("ascii") or b"bare" in fields:
            continue
        candidate = Path(os.fsdecode(fields[b"worktree"]))
        if not candidate.is_dir():
            continue
        candidate = worktree_root(candidate)
        # A worktree can disappear or switch after the list operation.
        if common_directory(candidate) != common or git(candidate, "rev-parse", "HEAD").strip() != target.head.encode("ascii"):
            continue
        if candidate not in result:
            result.append(candidate)
    return result


def resolve_targets(target: Target) -> Resolution:
    """Bind context to local files, or retain a PR's GitHub fallback on failure."""
    if target.head:
        try:
            roots = pr_worktrees(target)
            targets = tuple(pin_baseline(replace(target, repo=root, head=None)) for root in roots)
            for bound in targets:
                read_comparison(bound)
        except (OSError, ValueError) as error:
            return Resolution((), "本地 PR 比较不可用：" + str(error))
        return Resolution(targets, "未找到评审提交的本地检出。" if not targets else "")
    bound = pin_baseline(target)
    read_comparison(bound)
    return Resolution((bound,))


def read_comparison(target: Target) -> Comparison:
    """Read only the named Git object and current path; absence is not a failed read."""
    if target.head or target.base == "index" or target.base.startswith("commit:"):
        raise ValueError("resolve review context before reading its comparison")
    root = worktree_root(target.repo)
    before = None if target.base == "absent" else git(root, "cat-file", "blob", target.base[5:])
    current = root
    for part in target.path.split("/"):
        current /= part
        if redirected(current):
            raise ValueError("worktree target redirects through a link or reparse point")
    current.resolve().relative_to(root)
    try:
        information = current.stat()
    except FileNotFoundError:
        after = None
    else:
        if not stat.S_ISREG(information.st_mode):
            raise ValueError("worktree target is not a regular file")
        after = current.read_bytes()
    return Comparison(target, before, after, current)
