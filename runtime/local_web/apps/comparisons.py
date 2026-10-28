"""Resolve review context to fixed baselines and existing local worktrees."""
from __future__ import annotations

from dataclasses import dataclass, replace
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
from typing import Dict, List, Literal, Mapping, Optional, Sequence, Tuple
from urllib.parse import parse_qs, urlencode, urlsplit

from .. import ORIGIN
from ..storage import redirected


BranchStatus = Literal["matching", "different", "detached", "unknown"]


@dataclass(frozen=True)
class Target:
    repo: Path
    path: str
    base: str
    github: Optional[str] = None
    head: Optional[str] = None
    base_path: Optional[str] = None
    base_commit: Optional[str] = None
    branch: Optional[str] = None
    source_repository: Optional[str] = None
    view: Literal["auto", "worktree", "snapshot"] = "auto"

    def query(self) -> str:
        values = {"repo": str(self.repo), "path": self.path, "base": self.base}
        if self.github:
            values["github"] = self.github
        if self.head:
            values["head"] = self.head
        if self.base_path:
            values["base_path"] = self.base_path
        if self.base_commit:
            values["base_commit"] = self.base_commit
        if self.branch:
            values["branch"] = self.branch
            values["source_repository"] = self.source_repository
        if self.view != "auto":
            values["view"] = self.view
        return urlencode(values)

    def url(self, *, html_only: bool = False) -> str:
        return ORIGIN + ("/diff/html?" if html_only else "/diff?") + self.query()


@dataclass(frozen=True)
class Comparison:
    target: Target
    before: Optional[bytes]
    after: Optional[bytes]
    worktree_file: Optional[Path]


@dataclass(frozen=True)
class Resolution:
    targets: Tuple[Target, ...]
    message: str = ""


@dataclass(frozen=True)
class Worktree:
    repo: Path
    head: str
    branch: Optional[str]


@dataclass(frozen=True)
class PullRequest:
    repository: str
    number: int
    head: str
    branch: Optional[str] = None
    source_repository: Optional[str] = None


def parse_pr(value: object) -> PullRequest:
    """Validate the PR owner separately from its optional source-branch identity."""
    required = {"repository", "number", "head"}
    if (not isinstance(value, dict) or not required <= set(value)
            or set(value) - required - {"branch", "source_repository"}):
        raise ValueError("pr needs repository, number, head, and optional paired branch/source_repository")
    github_pr_url(value["repository"], value["number"])
    if ({"branch", "source_repository"} & set(value)
            and (not {"branch", "source_repository"} <= set(value)
                 or value["branch"] is None or value["source_repository"] is None)):
        raise ValueError("pr.branch and pr.source_repository must be supplied together")
    validate_pr_source(value.get("branch"), value.get("source_repository"))
    if not isinstance(value["head"], str) or re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value["head"]) is None:
        raise ValueError("pr.head must be a full fixed commit OID")
    return PullRequest(value["repository"], value["number"], value["head"],
                       value.get("branch"), value.get("source_repository"))


def validate_pr_source(branch: Optional[str], source_repository: Optional[str]) -> None:
    if branch is None and source_repository is None:
        return
    if (not isinstance(branch, str) or not branch or branch.startswith(("-", "/"))
            or branch.endswith(("/", ".")) or ".." in branch or "@{" in branch or branch == "@"
            or any(c.isspace() or ord(c) < 32 or c in "~^:?*[\\" for c in branch)
            or any(not part or part.startswith(".") or part.endswith(".lock") for part in branch.split("/"))):
        raise ValueError("pr.branch must be a short Git branch name")
    github_pr_url(source_repository, 1)


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
    if set(fields) - {"repo", "path", "base", "github", "head", "base_path", "base_commit", "branch", "source_repository", "view"} or not {"repo", "path", "base"} <= set(fields):
        raise ValueError("unexpected or missing diff context")
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
    base_commit = fields.get("base_commit")
    if base_commit and (re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", base_commit) is None or not base.startswith("blob:")):
        raise ValueError("base_commit needs a full commit OID and a pinned blob baseline")
    if "base_path" in fields and not (base == "index" or base.startswith("commit:") or base_commit):
        raise ValueError("base_path needs an index, commit, or a blob with base_commit")
    github = fields.get("github")
    if github:
        parsed = urlsplit(github)
        if (parsed.scheme != "https" or parsed.netloc != "github.com"
                or re.fullmatch(r"/[^/]+/[^/]+/pull/[1-9][0-9]*(?:/files)?/?", parsed.path) is None):
            raise ValueError("github must be an HTTPS GitHub PR or Files changed URL")
    head = fields.get("head")
    if head and (re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", head) is None or not github or base == "index"):
        raise ValueError("PR head needs a full commit OID, github URL, and a fixed baseline")
    validate_pr_source(fields.get("branch"), fields.get("source_repository"))
    view = fields.get("view", "auto")
    if view not in ("auto", "worktree", "snapshot") or ((view != "auto" or "branch" in fields) and not head):
        raise ValueError("PR view and source branch require a fixed reviewed head")
    return Target(repo, fields["path"], base, github, head, fields.get("base_path"), base_commit,
                  fields.get("branch"), fields.get("source_repository"), view)


def target_from_query(query: str) -> Target:
    fields = parse_qs(query, keep_blank_values=True, strict_parsing=True, max_num_fields=10)
    if any(len(values) != 1 for values in fields.values()):
        raise ValueError("duplicate diff parameter")
    target = target_from_fields({name: values[0] for name, values in fields.items()})
    if target.base == "index":
        raise ValueError("URLs must pin a baseline; index is a link-generation input only")
    return target


def git(repo: Path, *arguments: str) -> bytes:
    environment = {name: value for name, value in os.environ.items() if not name.startswith("GIT_")}
    try:
        result = subprocess.run(["git", "--no-replace-objects", "--no-optional-locks", "-C", str(repo)] + list(arguments),
                                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                env=environment, timeout=10,
                                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
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
    bound = replace(target, base=base, base_path=None)
    if base == "absent":
        return bound
    if target.base.startswith("commit:"):
        return replace(bound, base_commit=commit, base_path=target.base_path)
    try:
        head = git(root, "rev-parse", "--verify", "HEAD^{commit}").decode("ascii").strip()
        committed = pin_baseline(replace(target, base="commit:" + head))
    except (OSError, ValueError):
        # Native positioning is optional; the captured index blob remains authoritative.
        return bound
    return committed if committed.base == base else bound


def common_directory(repo: Path) -> Path:
    directory = Path(os.fsdecode(git(repo, "rev-parse", "--git-common-dir")).strip())
    return (repo / directory).resolve(strict=True)


def registered_worktrees(repo: Path) -> List[Worktree]:
    """Read Git's topology, including the current checkout and external worktrees."""
    root = worktree_root(repo)
    common = common_directory(root)
    result = []
    records = git(root, "worktree", "list", "--porcelain", "-z")
    for record in records.split(b"\0\0"):
        if not record:
            continue
        fields = {}
        for field in record.split(b"\0"):
            if field:
                name, _, value = field.partition(b" ")
                fields[name] = value
        if b"bare" in fields:
            continue
        if b"worktree" not in fields:
            raise ValueError("invalid Git worktree record")
        candidate = Path(os.fsdecode(fields[b"worktree"]))
        try:
            candidate.stat()
        except FileNotFoundError:
            continue
        candidate = worktree_root(candidate)
        if common_directory(candidate) != common:
            continue
        head = git(candidate, "rev-parse", "--verify", "HEAD^{commit}").decode("ascii").strip()
        branch = git(candidate, "rev-parse", "--abbrev-ref", "HEAD").decode("utf-8").strip()
        entry = Worktree(candidate, head, None if branch == "HEAD" else branch)
        if entry not in result:
            result.append(entry)
    if not result:
        return result
    preferred = result[0].repo / ".worktrees"

    def priority(entry: Worktree) -> int:
        try:
            entry.repo.relative_to(preferred)
            return 0
        except ValueError:
            return 1

    return sorted(result, key=priority)


def github_repository(url: str) -> Optional[str]:
    """Recognize repository identity without returning credentials from remote URLs."""
    match = re.fullmatch(r"git@github\.com:([^/]+/[^/]+?)(?:\.git)?/?", url, re.IGNORECASE)
    if match:
        return match[1].lower()
    parsed = urlsplit(url)
    if parsed.scheme in ("https", "http", "ssh") and parsed.hostname and parsed.hostname.lower() == "github.com":
        path = parsed.path.strip("/")
        if path.endswith(".git"):
            path = path[:-4]
        if re.fullmatch(r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+", path):
            return path.lower()
    return None


def branch_source_status(entry: Worktree, branch: Optional[str], source_repository: Optional[str]) -> BranchStatus:
    """Keep an unverified source distinct from a known branch mismatch."""
    if entry.branch is None:
        return "detached"
    if branch is None or source_repository is None:
        return "unknown"
    remote = git(entry.repo, "config", "--get", "--default", "", "branch." + entry.branch + ".remote").decode().strip()
    merge = git(entry.repo, "config", "--get", "--default", "", "branch." + entry.branch + ".merge").decode().strip()
    if remote:
        if merge != "refs/heads/" + branch:
            return "different"
        if remote == ".":
            return "unknown"
        url = git(entry.repo, "remote", "get-url", remote).decode().strip()
        source = github_repository(url)
        if source is None:
            return "unknown"
        return "matching" if source == source_repository.lower() else "different"
    if entry.branch != branch:
        return "different"
    # Without tracking, only an unambiguous configured source can identify a same-name branch.
    remotes = git(entry.repo, "remote").decode().splitlines()
    sources = {github_repository(git(entry.repo, "remote", "get-url", name).decode().strip()) for name in remotes}
    if not sources or None in sources or len(sources) != 1:
        return "unknown"
    return "matching" if sources == {source_repository.lower()} else "different"


def matching_worktrees(entries: Sequence[Worktree], *, head: str, branch: Optional[str],
                       source_repository: Optional[str]) -> List[Worktree]:
    if branch:
        return [entry for entry in entries if branch_source_status(entry, branch, source_repository) == "matching"]
    return [entry for entry in entries if entry.head == head]


def pr_worktrees(target: Target) -> List[Path]:
    """Prefer a verified source branch; head-only contexts retain exact-commit discovery."""
    return [entry.repo for entry in matching_worktrees(registered_worktrees(target.repo), head=target.head,
            branch=target.branch, source_repository=target.source_repository)]


def worktree_changes(repo: Path) -> Dict[str, List[Dict[str, str]]]:
    """Inventory both index layers, rename sources, conflicts, and individual untracked paths."""
    changes = {name: [] for name in ("staged", "unstaged", "untracked", "conflicted")}  # type: Dict[str, List[Dict[str, str]]]
    records = iter(git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all",
                       "--ignore-submodules=none").split(b"\0"))
    for record in records:
        if not record:
            continue
        if len(record) < 4 or record[2:3] != b" ":
            raise ValueError("invalid Git status record")
        status = record[:2].decode("ascii")
        item = {"path": os.fsdecode(record[3:])}
        if "R" in status or "C" in status:
            # Porcelain -z emits the destination first, then a separate original path.
            original = next(records, b"")
            if not original:
                raise ValueError("Git status rename source is unavailable")
            item["original_path"] = os.fsdecode(original)
        if status == "??":
            changes["untracked"].append(dict(item, status="?"))
        elif status in ("DD", "AU", "UD", "UA", "DU", "AA", "UU"):
            changes["conflicted"].append(dict(item, status=status))
        else:
            for name, code in zip(("staged", "unstaged"), status):
                if code != " ":
                    changes[name].append(dict(item, status=code))
    return changes


def inspect_workspace(entry: Worktree, pr: PullRequest, branch_status: BranchStatus) -> Dict[str, object]:
    """Report independent identity, commit, and local-change evidence for one checkout."""
    remotes = [{"name": name, "repository": github_repository(git(entry.repo, "remote", "get-url", name).decode().strip())}
               for name in git(entry.repo, "remote").decode().splitlines()]
    sources = {remote["repository"] for remote in remotes}
    targets = {pr.repository.lower()}
    if pr.source_repository:
        targets.add(pr.source_repository.lower())
    if sources & targets:
        repository_status = "related"
    elif not sources or None in sources or pr.source_repository is None:
        repository_status = "unknown"
    else:
        repository_status = "unrelated"
    observation = {"repo": str(entry.repo), "branch": entry.branch, "head": entry.head,
                   "repository_status": repository_status, "remotes": remotes, "branch_status": branch_status,
                   "status": "unknown", "dirty": None, "changes": None, "ahead": None, "behind": None,
                   "message": ""}  # type: Dict[str, object]
    diagnostics = []  # type: List[str]
    try:
        changes = worktree_changes(entry.repo)
        observation.update(changes=changes, dirty=any(changes.values()))
    except (OSError, ValueError) as error:
        diagnostics.append(str(error))
    try:
        ahead, behind = map(int, git(entry.repo, "rev-list", "--left-right", "--count",
                                    entry.head + "..." + pr.head).split())
        observation.update(status="diverged" if ahead and behind else "ahead" if ahead else "behind" if behind else "same",
                           ahead=ahead, behind=behind)
    except (OSError, ValueError) as error:
        diagnostics.append(str(error))
    observation["message"] = "; ".join(diagnostics)
    return observation


def inspect_worktrees(repo: Path, pr: PullRequest) -> Dict[str, object]:
    """Inspect the current checkout even when source-branch discovery does not match it."""
    entries = registered_worktrees(repo)
    root = repo.resolve(strict=True)
    current = None  # type: Optional[Dict[str, object]]
    observations = []  # type: List[Dict[str, object]]
    for entry in entries:
        branch_status = branch_source_status(entry, pr.branch, pr.source_repository)
        matches = branch_status == "matching" if pr.branch else entry.head == pr.head
        if entry.repo == root or matches:
            observation = inspect_workspace(entry, pr, branch_status)
            if entry.repo == root:
                current = observation
            if matches:
                observations.append(observation)
    if current is None:
        raise ValueError("current checkout is missing from registered worktrees")
    return {"reviewed_head": pr.head, "branch": pr.branch, "source_repository": pr.source_repository,
            "current": current, "worktrees": observations,
            "message": "" if observations else "未找到对应分支的本地工作区。"}


def resolve_targets(target: Target) -> Resolution:
    """Bind a live worktree or read both fixed PR sides before offering a web fallback."""
    if target.head:
        failures = []
        try:
            if target.view != "auto":
                bound = pin_baseline(target)
                read_comparison(bound)
                return Resolution((bound,))
            try:
                roots = pr_worktrees(target)
            except (OSError, ValueError) as error:
                # Snapshot display is independently usable even when local discovery fails.
                roots = []
                failures.append(str(error))
            targets = []
            for root in roots:
                try:
                    bound = pin_baseline(replace(target, repo=root, view="worktree"))
                    read_comparison(bound)
                    targets.append(bound)
                except (OSError, ValueError) as error:
                    failures.append(str(error))
            if targets:
                return Resolution(tuple(targets), "；".join(failures))
            bound = pin_baseline(replace(target, view="snapshot"))
            read_comparison(bound)
            return Resolution((bound,), "未找到可用的本地工作区，显示固定 PR 快照。" + "；".join(failures))
        except (OSError, ValueError) as error:
            return Resolution((), "本地 PR 比较不可用：" + "；".join(failures + [str(error)]))
    bound = pin_baseline(target)
    read_comparison(bound)
    return Resolution((bound,))


def read_comparison(target: Target) -> Comparison:
    """Read only the named Git object and current path; absence is not a failed read."""
    if (target.head and target.view == "auto") or target.base == "index" or target.base.startswith("commit:"):
        raise ValueError("resolve review context before reading its comparison")
    root = worktree_root(target.repo)
    before = None if target.base == "absent" else git(root, "cat-file", "blob", target.base[5:])
    if target.view == "snapshot":
        after_target = pin_baseline(replace(target, base="commit:" + target.head, base_path=None, base_commit=None))
        after = None if after_target.base == "absent" else git(root, "cat-file", "blob", after_target.base[5:])
        return Comparison(target, before, after, None)
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
