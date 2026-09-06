from __future__ import annotations

import hashlib
import os
import re
import stat
from pathlib import Path, PurePosixPath
from typing import Callable, NamedTuple, Tuple


COMMIT = re.compile(r'^[0-9a-fA-F]{40}$')
GITHUB_URL = re.compile(
    r'^(?:https://github\.com/|git@github\.com:)([A-Za-z0-9_.-]+)/'
    r'([A-Za-z0-9_.-]+?)(?:\.git)?$'
)
GIT_REF = re.compile(r'^[A-Za-z0-9._/-]+$')
FRONTMATTER_NAME = re.compile(
    r'name:[ \t]*(?:"([^"]+)"|\'([^\']+)\'|([A-Za-z0-9][A-Za-z0-9_-]*))[ \t]*'
)
LICENSE_SIGNATURES: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    'MIT': ((
        'permission is hereby granted, free of charge, to any person obtaining a copy',
        'the above copyright notice and this permission notice shall be included',
        'the software is provided "as is", without warranty of any kind',
        'in no event shall the authors or copyright holders be liable',
    ), ()),
    'Apache-2.0': ((
        'apache license version 2.0, january 2004',
        'terms and conditions for use, reproduction, and distribution',
        'grant of copyright license',
        'grant of patent license',
        'redistribution. you may reproduce and distribute copies',
        'acceptance of support, warranty, indemnity, or other liability obligations',
        'end of terms and conditions',
    ), ()),
    'BSD-2-Clause': ((
        'redistribution and use in source and binary forms, with or without modification',
        'redistributions of source code must retain the above copyright notice',
        'redistributions in binary form must reproduce the above copyright notice',
        'this software is provided by the copyright holders and contributors "as is"',
    ), (
        'neither the name of the copyright holder nor the names of its contributors',
    )),
    'BSD-3-Clause': ((
        'redistribution and use in source and binary forms, with or without modification',
        'redistributions of source code must retain the above copyright notice',
        'redistributions in binary form must reproduce the above copyright notice',
        'neither the name of the copyright holder nor the names of its contributors',
        'this software is provided by the copyright holders and contributors "as is"',
    ), ()),
    'MPL-2.0': ((
        'mozilla public license version 2.0',
        '1. definitions',
        '2. license grants and conditions',
        '3. responsibilities',
        '10. versions of the license',
        'exhibit a - source code form license notice',
    ), ()),
    'ISC': ((
        'permission to use, copy, modify, and/or distribute this software for any purpose',
        'the above copyright notice and this permission notice appear in all copies',
        'the software is provided "as is" and the author disclaims all warranties',
        'in no event shall the author be liable for any special, direct, indirect, or consequential damages',
    ), ()),
}
LICENSE_MARKERS = frozenset(LICENSE_SIGNATURES)
LICENSE_CANDIDATES = (
    PurePosixPath('LICENSE'),
    PurePosixPath('LICENSE.txt'),
    PurePosixPath('LICENSE.md'),
    PurePosixPath('COPYING'),
    PurePosixPath('COPYING.txt'),
    PurePosixPath('COPYING.md'),
)
LICENSE_DISCOVERY_ORDER = (
    'MIT',
    'Apache-2.0',
    'BSD-3-Clause',
    'BSD-2-Clause',
    'MPL-2.0',
    'ISC',
)
_FILE_ATTRIBUTE_REPARSE_POINT = getattr(
    stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400,
)


class ExternalContractError(ValueError):
    """Raised when a GitHub source cannot satisfy the shared snapshot contract."""


class RefResolution(NamedTuple):
    requested_ref: str | None
    fetch_ref: str
    resolved_ref: str
    ref_kind: str


class SkillTreeSnapshot(NamedTuple):
    root: Path
    files: dict[str, str]


class LicenseDiscovery(NamedTuple):
    spdx: str
    path: PurePosixPath
    content: bytes


GitRunner = Callable[[Tuple[str, ...]], str]


def isolated_git_environment(home: Path) -> dict[str, str]:
    """Return the small host environment needed for isolated non-interactive Git reads."""
    inherited = (
        'PATH', 'PATHEXT', 'SYSTEMROOT', 'WINDIR', 'COMSPEC',
        'TEMP', 'TMP', 'TMPDIR', 'LANG', 'LC_ALL',
    )
    environment = {
        key: os.environ[key]
        for key in inherited
        if key in os.environ
    }
    private_home = str(Path(home).absolute())
    environment.update({
        'HOME': private_home,
        'USERPROFILE': private_home,
        'XDG_CONFIG_HOME': str(Path(private_home) / '.config'),
        'GIT_TERMINAL_PROMPT': '0',
        'GIT_CONFIG_NOSYSTEM': '1',
        'GIT_CONFIG_GLOBAL': os.devnull,
        'GCM_INTERACTIVE': 'Never',
    })
    return environment


def validate_source_identity(source_id: str, url: str) -> None:
    match = GITHUB_URL.fullmatch(url)
    if match is None or source_id.casefold() != (
        f'{match.group(1)}/{match.group(2)}'.casefold()
    ):
        raise ExternalContractError('source id and GitHub url must match')


def validate_ref(ref: str | None) -> None:
    if ref is not None and (
        not ref or ref.startswith('-') or GIT_REF.fullmatch(ref) is None
    ):
        raise ExternalContractError('source ref must be a safe Git argument')


def resolve_ref(url: str, requested_ref: str | None, run_git: GitRunner) -> RefResolution:
    validate_ref(requested_ref)
    if requested_ref is None:
        symbolic = run_git(('ls-remote', '--symref', url, 'HEAD'))
        match = re.search(r'ref: refs/heads/([^\s]+)\s+HEAD', symbolic)
        return RefResolution(None, 'HEAD', match.group(1) if match else 'HEAD', 'branch')
    if COMMIT.fullmatch(requested_ref):
        return RefResolution(requested_ref, requested_ref, requested_ref, 'commit')
    if run_git(('ls-remote', '--heads', url, requested_ref)):
        return RefResolution(requested_ref, requested_ref, requested_ref, 'branch')
    if run_git(('ls-remote', '--tags', url, f'refs/tags/{requested_ref}')):
        return RefResolution(requested_ref, requested_ref, requested_ref, 'tag')
    raise ExternalContractError(f'source ref does not exist: {requested_ref}')


def _license_text(content: bytes) -> str | None:
    try:
        return ' '.join(content.decode('utf-8').casefold().split())
    except UnicodeDecodeError:
        return None


def _matching_licenses(content: bytes) -> frozenset[str]:
    text = _license_text(content)
    if text is None:
        return frozenset()
    return frozenset(
        spdx
        for spdx, (required, forbidden) in LICENSE_SIGNATURES.items()
        if all(marker in text for marker in required)
        and not any(marker in text for marker in forbidden)
    )


def license_matches(spdx: str, content: bytes) -> bool:
    if spdx not in LICENSE_SIGNATURES:
        raise ExternalContractError(f'unsupported SPDX license: {spdx}')
    return _matching_licenses(content) == {spdx}


def discover_license(root: Path, label: str) -> LicenseDiscovery:
    discoveries: list[LicenseDiscovery] = []
    for relative in LICENSE_CANDIDATES:
        path = source_path(root, relative, label)
        if not path.exists():
            continue
        if not path.is_file():
            raise ExternalContractError(f'{label} is not a regular file: {relative}')
        try:
            content = path.read_bytes()
        except OSError as error:
            raise ExternalContractError(f'{label} cannot be read: {relative}') from error
        matches = _matching_licenses(content)
        if len(matches) > 1:
            raise ExternalContractError(f'{label} is ambiguous: {relative}')
        if matches:
            spdx = next(item for item in LICENSE_DISCOVERY_ORDER if item in matches)
            discoveries.append(LicenseDiscovery(spdx, relative, content))
    if not discoveries:
        raise ExternalContractError(f'{label} was not found or recognized')
    signatures = {
        (item.spdx, hashlib.sha256(item.content).hexdigest())
        for item in discoveries
    }
    if len(signatures) != 1:
        paths = ', '.join(item.path.as_posix() for item in discoveries)
        raise ExternalContractError(f'{label} is ambiguous: {paths}')
    return discoveries[0]


def is_link_like(path: Path) -> bool:
    """Return whether a path redirects through a symlink or Windows reparse point."""
    try:
        status = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(status.st_mode) or bool(
        getattr(status, 'st_file_attributes', 0) & _FILE_ATTRIBUTE_REPARSE_POINT
    )


_is_link_like = is_link_like


def source_path(root: Path, relative: PurePosixPath, label: str) -> Path:
    current = root
    if _is_link_like(current) or not current.is_dir():
        raise ExternalContractError(f'{label} source root is not a regular directory')
    for part in relative.parts:
        current /= part
        if _is_link_like(current):
            raise ExternalContractError(f'{label} path contains a symlink')
    return current


def snapshot_skill_tree(
    checkout_root: Path,
    relative: PurePosixPath,
    expected_name: str,
    label: str,
) -> SkillTreeSnapshot:
    root = source_path(checkout_root, relative, label)
    if _is_link_like(root) or not root.is_dir():
        raise ExternalContractError(f'{label} is not a regular directory')
    files: dict[str, str] = {}
    for path in sorted(root.rglob('*')):
        if _is_link_like(path):
            raise ExternalContractError(f'{label} contains a symlink')
        if path.is_dir():
            continue
        if not path.is_file():
            raise ExternalContractError(f'{label} contains a non-regular file')
        relative_file = path.relative_to(root).as_posix()
        files[relative_file] = hashlib.sha256(path.read_bytes()).hexdigest()
    skill = root / 'SKILL.md'
    try:
        text = skill.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as error:
        raise ExternalContractError(f'{label} is missing a UTF-8 SKILL.md') from error
    lines = text.splitlines()
    if not lines or lines[0] != '---':
        raise ExternalContractError(f'{label} SKILL.md has no YAML frontmatter')
    try:
        end = lines.index('---', 1)
    except ValueError as error:
        raise ExternalContractError(
            f'{label} SKILL.md has malformed YAML frontmatter'
        ) from error
    body_start = end + 1
    while body_start < len(lines) and not lines[body_start].strip():
        body_start += 1
    if (
        body_start < len(lines)
        and lines[body_start] == '---'
        and '---' in lines[body_start + 1:]
    ):
        raise ExternalContractError(f'{label} SKILL.md has duplicate YAML frontmatter')
    names: list[str] = []
    for line in lines[1:end]:
        if line.lstrip() != line or not line.startswith('name:'):
            continue
        match = FRONTMATTER_NAME.fullmatch(line)
        if match is None:
            raise ExternalContractError(f'{label} SKILL.md has malformed name frontmatter')
        names.append(next(value for value in match.groups() if value is not None))
    if len(names) != 1:
        raise ExternalContractError(f'{label} SKILL.md must declare one frontmatter name')
    if names[0] != expected_name:
        raise ExternalContractError(f'{label} name does not match config')
    return SkillTreeSnapshot(root, files)
