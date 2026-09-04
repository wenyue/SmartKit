from __future__ import annotations

import os
import secrets
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable

from .catalog import ContractError, safe_relative
from .external_contract import is_link_like as _is_link_like
from .models import Change, ChangeKind, ExpectedEntry, Plan
from .ownership import OWNERSHIP_PATH
from .project import ProjectError, confined_target


_replace = os.replace
_DIRECTORY_FLAGS = os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0) | getattr(os, 'O_NOFOLLOW', 0)
_FILE_FLAGS = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
_SECURE_DIR_FDS = os.name == 'posix' and bool(getattr(os, 'O_NOFOLLOW', 0))


class TransactionError(RuntimeError):
    """Raised when a plan cannot reach or restore its declared state."""

    def __init__(self, original_error: BaseException, rollback_errors: tuple[BaseException, ...] = ()):
        self.original_error = original_error
        self.rollback_errors = rollback_errors
        message = f'transaction failed: {original_error}'
        if rollback_errors:
            message += '; rollback failed: ' + '; '.join(str(error) for error in rollback_errors)
        super().__init__(message)


@dataclass(frozen=True)
class _Operation:
    path: PurePosixPath
    kind: ChangeKind
    content: bytes | None
    expected: ExpectedEntry | None


@dataclass(frozen=True)
class _Backup:
    operation: _Operation
    snapshot: Path | None
    mode: int | None
    identity: tuple[int, int] | None


@dataclass(frozen=True)
class _Mutation:
    backup: _Backup
    result_identity: tuple[int, int] | None
    result_content: bytes | None
    result_mode: int | None


@dataclass(frozen=True)
class _RootGuard:
    path: Path
    identity: tuple[int, int]


@dataclass(frozen=True)
class _CreatedDirectory:
    path: PurePosixPath | Path
    identity: tuple[int, int]


def _path_key(path: PurePosixPath) -> str:
    return path.as_posix()


def _validate_change(change: Change) -> PurePosixPath:
    if not isinstance(change, Change) or not isinstance(change.path, PurePosixPath):
        raise TransactionError(TypeError('plan change must have a relative POSIX path'))
    try:
        path = safe_relative(change.path.as_posix(), 'plan change path')
    except ContractError as error:
        raise TransactionError(error) from error
    if not isinstance(change.kind, ChangeKind):
        raise TransactionError(TypeError(f'unsupported change kind: {change.kind!r}'))
    if (
        change.kind in {ChangeKind.DELETE, ChangeKind.DELETE_DIRECTORY}
        and change.content is not None
    ):
        raise TransactionError(TypeError(f'delete change has content: {_path_key(change.path)}'))
    if (
        change.kind not in {ChangeKind.DELETE, ChangeKind.DELETE_DIRECTORY}
        and not isinstance(change.content, bytes)
    ):
        raise TransactionError(TypeError(f'file change content must be bytes: {_path_key(change.path)}'))
    if change.expected is not None and (
        not isinstance(change.expected, ExpectedEntry)
        or not isinstance(change.expected.mode, int)
        or not isinstance(change.expected.identity, tuple)
        or len(change.expected.identity) != 2
        or not all(isinstance(item, int) for item in change.expected.identity)
        or (
            change.kind is ChangeKind.DELETE_DIRECTORY
            and change.expected.content is not None
        )
        or (
            change.kind is not ChangeKind.DELETE_DIRECTORY
            and not isinstance(change.expected.content, bytes)
        )
    ):
        raise TransactionError(TypeError(f'plan change preimage is invalid: {_path_key(change.path)}'))
    return path


def _operations(plan: Plan) -> tuple[_Operation, ...]:
    if not isinstance(plan, Plan):
        raise TransactionError(TypeError('plan must be a Plan'))
    seen: set[PurePosixPath] = set()
    operations: list[_Operation] = []
    for change in plan.changes:
        path = _validate_change(change)
        if path in seen:
            raise TransactionError(ValueError(f'duplicate plan change: {_path_key(path)}'))
        seen.add(path)
        if change.kind is not ChangeKind.UNCHANGED:
            operations.append(_Operation(
                path,
                change.kind,
                change.content,
                change.expected,
            ))
    operations.sort(
        key=lambda operation: (
            2
            if operation.path == OWNERSHIP_PATH
            else 1
            if operation.kind is ChangeKind.DELETE_DIRECTORY
            else 0,
            -len(operation.path.parts)
            if operation.kind is ChangeKind.DELETE_DIRECTORY
            else 0,
            _path_key(operation.path),
        )
    )
    return tuple(operations)


def _open_root(root: Path) -> int:
    absolute = Path(root).absolute()
    descriptor = os.open(absolute.anchor, _DIRECTORY_FLAGS)
    try:
        for part in absolute.parts[1:]:
            next_descriptor = os.open(part, _DIRECTORY_FLAGS, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _root_guard(root: Path) -> tuple[_RootGuard, int]:
    descriptor = _open_root(root)
    entry = os.fstat(descriptor)
    return _RootGuard(Path(root).absolute(), (entry.st_dev, entry.st_ino)), descriptor


def _assert_root(guard: _RootGuard) -> None:
    try:
        descriptor = _open_root(guard.path)
    except OSError as error:
        raise TransactionError('unsafe root namespace changed during transaction') from error
    try:
        entry = os.fstat(descriptor)
        if (entry.st_dev, entry.st_ino) != guard.identity or not stat.S_ISDIR(entry.st_mode):
            raise TransactionError('unsafe root namespace changed during transaction')
    finally:
        os.close(descriptor)


def _open_parent(
    root_fd: int,
    path: PurePosixPath,
    *,
    create: bool,
    created: list[_CreatedDirectory],
) -> int:
    descriptor = os.dup(root_fd)
    try:
        for index, part in enumerate(path.parts[:-1], start=1):
            created_path: PurePosixPath | None = None
            try:
                next_descriptor = os.open(part, _DIRECTORY_FLAGS, dir_fd=descriptor)
            except FileNotFoundError:
                if not create:
                    raise
                os.mkdir(part, 0o777, dir_fd=descriptor)
                created_path = PurePosixPath(*path.parts[:index])
                next_descriptor = os.open(part, _DIRECTORY_FLAGS, dir_fd=descriptor)
            except OSError as error:
                raise TransactionError(f'unsafe parent path: {part}') from error
            if created_path is not None:
                entry = os.fstat(next_descriptor)
                created.append(_CreatedDirectory(
                    created_path,
                    (entry.st_dev, entry.st_ino),
                ))
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _stat_at(
    parent_fd: int, name: str, *, directory: bool = False
) -> os.stat_result | None:
    try:
        entry = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(entry.st_mode):
        raise TransactionError(f'unsafe symlink at transaction target: {name}')
    expected = stat.S_ISDIR(entry.st_mode) if directory else stat.S_ISREG(entry.st_mode)
    if not expected:
        kind = 'directory' if directory else 'regular file'
        raise TransactionError(f'target path is not a {kind}: {name}')
    return entry


def _read_at(
    parent_fd: int, name: str
) -> tuple[bytes, int, tuple[int, int]] | None:
    entry = _stat_at(parent_fd, name)
    if entry is None:
        return None
    descriptor = os.open(name, _FILE_FLAGS, dir_fd=parent_fd)
    try:
        current = os.fstat(descriptor)
        if not stat.S_ISREG(current.st_mode) or (current.st_dev, current.st_ino) != (entry.st_dev, entry.st_ino):
            raise TransactionError(f'unsafe target changed while reading: {name}')
        chunks: list[bytes] = []
        while chunk := os.read(descriptor, 65536):
            chunks.append(chunk)
        return b''.join(chunks), stat.S_IMODE(current.st_mode), (current.st_dev, current.st_ino)
    finally:
        os.close(descriptor)


def _write_sibling(
    root_fd: int,
    path: PurePosixPath,
    content: bytes,
    mode: int | None,
    created: list[_CreatedDirectory],
    guard: _RootGuard | None = None,
) -> tuple[str, int]:
    """Create a closed same-directory temporary file through a freshly opened safe parent fd."""
    if guard is not None:
        _assert_root(guard)
    parent_fd = _open_parent(root_fd, path, create=True, created=created)
    temporary = f'.{path.name}.agents-setup-{secrets.token_hex(12)}.tmp'
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0)
    if guard is not None:
        _assert_root(guard)
    descriptor = os.open(temporary, flags, 0o666, dir_fd=parent_fd)
    try:
        view = memoryview(content)
        while view:
            written = os.write(descriptor, view)
            view = view[written:]
    except BaseException:
        os.close(descriptor)
        os.unlink(temporary, dir_fd=parent_fd)
        os.close(parent_fd)
        raise
    else:
        os.close(descriptor)
    if mode is not None:
        if guard is not None:
            _assert_root(guard)
        os.chmod(temporary, mode, dir_fd=parent_fd, follow_symlinks=False)
    return temporary, parent_fd


def _same_parent(root_fd: int, path: PurePosixPath, parent_fd: int) -> None:
    fresh_fd = _open_parent(root_fd, path, create=False, created=[])
    try:
        fresh = os.fstat(fresh_fd)
        held = os.fstat(parent_fd)
        if (fresh.st_dev, fresh.st_ino) != (held.st_dev, held.st_ino):
            raise TransactionError(f'unsafe parent changed during transaction: {_path_key(path)}')
    finally:
        os.close(fresh_fd)


def _expected(root_fd: int, operation: _Operation) -> None:
    try:
        parent_fd = _open_parent(root_fd, operation.path, create=False, created=[])
    except FileNotFoundError:
        if operation.kind is ChangeKind.CREATE:
            return
        raise TransactionError(f'target disappeared after planning: {_path_key(operation.path)}')
    try:
        if operation.kind is ChangeKind.DELETE_DIRECTORY:
            entry = _stat_at(parent_fd, operation.path.name, directory=True)
            observed = None if entry is None else ExpectedEntry(
                None,
                stat.S_IMODE(entry.st_mode),
                (entry.st_dev, entry.st_ino),
            )
        else:
            current = _read_at(parent_fd, operation.path.name)
            entry = current
            observed = None if current is None else ExpectedEntry(
                current[0], current[1], current[2]
            )
    finally:
        os.close(parent_fd)
    if operation.kind is ChangeKind.CREATE and entry is not None:
        raise TransactionError(f'create target appeared after planning: {_path_key(operation.path)}')
    if operation.kind in {
        ChangeKind.UPDATE,
        ChangeKind.DELETE,
        ChangeKind.DELETE_DIRECTORY,
    } and entry is None:
        raise TransactionError(f'target disappeared after planning: {_path_key(operation.path)}')
    if operation.expected is not None and observed != operation.expected:
        raise TransactionError(f'target changed after planning: {_path_key(operation.path)}')


def _backup(root_fd: int, operation: _Operation, backup_root: Path, index: int) -> _Backup:
    try:
        parent_fd = _open_parent(root_fd, operation.path, create=False, created=[])
    except FileNotFoundError:
        return _Backup(operation, None, None, None)
    try:
        if operation.kind is ChangeKind.DELETE_DIRECTORY:
            entry = _stat_at(parent_fd, operation.path.name, directory=True)
            if entry is None:
                return _Backup(operation, None, None, None)
            observed = ExpectedEntry(
                None,
                stat.S_IMODE(entry.st_mode),
                (entry.st_dev, entry.st_ino),
            )
            if operation.expected is not None and observed != operation.expected:
                raise TransactionError(
                    f'target changed after planning: {_path_key(operation.path)}'
                )
            return _Backup(
                operation,
                None,
                stat.S_IMODE(entry.st_mode),
                (entry.st_dev, entry.st_ino),
            )
        current = _read_at(parent_fd, operation.path.name)
    finally:
        os.close(parent_fd)
    if current is None:
        return _Backup(operation, None, None, None)
    content, mode, identity = current
    if (
        operation.expected is not None
        and ExpectedEntry(content, mode, identity) != operation.expected
    ):
        raise TransactionError(f'target changed after planning: {_path_key(operation.path)}')
    snapshot = backup_root / f'{index:04d}'
    snapshot.write_bytes(content)
    return _Backup(operation, snapshot, mode, identity)


def _final_matches(parent_fd: int, operation: _Operation, backup: _Backup) -> None:
    if operation.kind is ChangeKind.DELETE_DIRECTORY:
        current = _stat_at(parent_fd, operation.path.name, directory=True)
        current_identity = None if current is None else (current.st_dev, current.st_ino)
        current_mode = None if current is None else stat.S_IMODE(current.st_mode)
        matches_backup = (
            current_identity == backup.identity
            and current_mode == backup.mode
        )
    else:
        observed = _read_at(parent_fd, operation.path.name)
        current = observed
        current_identity = None if observed is None else observed[2]
        current_mode = None if observed is None else observed[1]
        current_content = None if observed is None else observed[0]
        backup_content = None if backup.snapshot is None else backup.snapshot.read_bytes()
        matches_backup = (
            current_identity == backup.identity
            and current_mode == backup.mode
            and current_content == backup_content
        )
    if backup.identity is None:
        if current is not None:
            raise TransactionError(f'unsafe final target appeared: {_path_key(operation.path)}')
    elif current is None or not matches_backup:
        raise TransactionError(f'unsafe final target changed: {_path_key(operation.path)}')


def _apply(root_fd: int, guard: _RootGuard, operation: _Operation, backup: _Backup, created: list[_CreatedDirectory], applied: list[_Mutation]) -> None:
    if operation.kind in {ChangeKind.DELETE, ChangeKind.DELETE_DIRECTORY}:
        parent_fd = _open_parent(root_fd, operation.path, create=False, created=created)
        try:
            _assert_root(guard)
            _final_matches(parent_fd, operation, backup)
            applied.append(_Mutation(backup, None, None, None))
            if operation.kind is ChangeKind.DELETE_DIRECTORY:
                os.rmdir(operation.path.name, dir_fd=parent_fd)
            else:
                os.unlink(operation.path.name, dir_fd=parent_fd)
        finally:
            os.close(parent_fd)
        return
    assert operation.content is not None
    temporary, parent_fd = _write_sibling(
        root_fd, operation.path, operation.content, backup.mode, created, guard
    )
    try:
        _assert_root(guard)
        _same_parent(root_fd, operation.path, parent_fd)
        _final_matches(parent_fd, operation, backup)
        temp_entry = os.stat(temporary, dir_fd=parent_fd, follow_symlinks=False)
        applied.append(_Mutation(
            backup,
            (temp_entry.st_dev, temp_entry.st_ino),
            operation.content,
            stat.S_IMODE(temp_entry.st_mode),
        ))
        _replace(temporary, operation.path.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
    finally:
        try:
            os.unlink(temporary, dir_fd=parent_fd)
        except FileNotFoundError:
            pass
        os.close(parent_fd)


def _verify_desired(root_fd: int, changes: tuple[Change, ...]) -> None:
    for change in changes:
        try:
            parent_fd = _open_parent(root_fd, change.path, create=False, created=[])
        except FileNotFoundError:
            if change.kind in {ChangeKind.DELETE, ChangeKind.DELETE_DIRECTORY}:
                continue
            raise TransactionError(f'content changed before transaction commit: {_path_key(change.path)}')
        try:
            current = (
                _stat_at(parent_fd, change.path.name, directory=True)
                if change.kind is ChangeKind.DELETE_DIRECTORY
                else _read_at(parent_fd, change.path.name)
            )
        except FileNotFoundError:
            current = None
        finally:
            os.close(parent_fd)
        if change.kind in {ChangeKind.DELETE, ChangeKind.DELETE_DIRECTORY}:
            if current is not None:
                raise TransactionError(f'delete result changed: {_path_key(change.path)}')
        elif current is None or current[0] != change.content:
            raise TransactionError(f'content changed before transaction commit: {_path_key(change.path)}')


def _verify_applied(root_fd: int, applied: list[_Mutation]) -> None:
    """Prove that no applied target changed before the transaction commits."""
    for mutation in applied:
        operation = mutation.backup.operation
        try:
            parent_fd = _open_parent(root_fd, operation.path, create=False, created=[])
        except FileNotFoundError:
            current = None
        else:
            try:
                current = (
                    _stat_at(parent_fd, operation.path.name, directory=True)
                    if operation.kind is ChangeKind.DELETE_DIRECTORY
                    else _read_at(parent_fd, operation.path.name)
                )
            finally:
                os.close(parent_fd)
        if operation.kind in {ChangeKind.DELETE, ChangeKind.DELETE_DIRECTORY}:
            if current is not None:
                raise TransactionError(
                    f'applied target changed before transaction commit: '
                    f'{_path_key(operation.path)}'
                )
            continue
        if current is None:
            raise TransactionError(
                f'applied target changed before transaction commit: '
                f'{_path_key(operation.path)}'
            )
        content, mode, identity = current
        if (
            identity != mutation.result_identity
            or content != mutation.result_content
            or mode != mutation.result_mode
        ):
            raise TransactionError(
                f'applied target changed before transaction commit: '
                f'{_path_key(operation.path)}'
            )


def _restore(root_fd: int, mutation: _Mutation, created: list[_CreatedDirectory]) -> None:
    backup = mutation.backup
    if backup.operation.kind is ChangeKind.DELETE_DIRECTORY:
        parent_fd = _open_parent(
            root_fd,
            backup.operation.path,
            create=False,
            created=created,
        )
        try:
            current = _stat_at(
                parent_fd,
                backup.operation.path.name,
                directory=True,
            )
            current_identity = None if current is None else (current.st_dev, current.st_ino)
            if current_identity == backup.identity:
                return
            if current_identity != mutation.result_identity:
                raise TransactionError(
                    f'third-party target retained during rollback: '
                    f'{_path_key(backup.operation.path)}'
                )
            if backup.identity is None:
                raise TransactionError(
                    f'directory backup is missing: {_path_key(backup.operation.path)}'
                )
            os.mkdir(
                backup.operation.path.name,
                backup.mode if backup.mode is not None else 0o777,
                dir_fd=parent_fd,
            )
        finally:
            os.close(parent_fd)
        return
    try:
        parent_fd = _open_parent(root_fd, backup.operation.path, create=backup.snapshot is not None, created=created)
    except FileNotFoundError:
        return
    try:
        current = _stat_at(parent_fd, backup.operation.path.name)
        current_identity = None if current is None else (current.st_dev, current.st_ino)
        if current_identity == backup.identity:
            return
        if current_identity != mutation.result_identity:
            raise TransactionError(f'third-party target retained during rollback: {_path_key(backup.operation.path)}')
        if current is not None:
            observed = _read_at(parent_fd, backup.operation.path.name)
            if observed is None or (
                observed[0] != mutation.result_content
                or observed[1] != mutation.result_mode
            ):
                raise TransactionError(
                    f'third-party target retained during rollback: '
                    f'{_path_key(backup.operation.path)}'
                )
        if backup.snapshot is None:
            if current is not None:
                os.unlink(backup.operation.path.name, dir_fd=parent_fd)
            return
    finally:
        os.close(parent_fd)
    assert backup.snapshot is not None
    content = backup.snapshot.read_bytes()
    temporary, parent_fd = _write_sibling(root_fd, backup.operation.path, content, backup.mode, created)
    try:
        _same_parent(root_fd, backup.operation.path, parent_fd)
        os.replace(temporary, backup.operation.path.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
    finally:
        try:
            os.unlink(temporary, dir_fd=parent_fd)
        except FileNotFoundError:
            pass
        os.close(parent_fd)


def _cleanup_created(root_fd: int, created: list[_CreatedDirectory]) -> list[BaseException]:
    errors: list[BaseException] = []
    for item in reversed(created):
        assert isinstance(item.path, PurePosixPath)
        path = item.path
        try:
            parent_fd = _open_parent(root_fd, path, create=False, created=[])
        except FileNotFoundError:
            continue
        except BaseException as error:
            errors.append(error)
            continue
        try:
            current = _stat_at(parent_fd, path.name, directory=True)
            if current is None:
                continue
            if (current.st_dev, current.st_ino) != item.identity:
                raise TransactionError(
                    f'third-party directory retained during rollback: '
                    f'{_path_key(path)}'
                )
            os.rmdir(path.name, dir_fd=parent_fd)
        except BaseException as error:
            errors.append(error)
        finally:
            os.close(parent_fd)
    return errors


def _rollback(root_fd: int, guard: _RootGuard, applied: list[_Mutation], created: list[_CreatedDirectory]) -> tuple[BaseException, ...]:
    errors: list[BaseException] = []
    try:
        _assert_root(guard)
    except BaseException as error:
        errors.append(error)
    for mutation in reversed(applied):
        try:
            _restore(root_fd, mutation, created)
        except BaseException as error:
            errors.append(error)
    errors.extend(_cleanup_created(root_fd, created))
    return tuple(errors)


def _apply_secure(
    target_root: Path,
    plan: Plan,
    postcondition: Callable[[], None] | None,
) -> None:
    operations = _operations(plan)
    guard, root_fd = _root_guard(target_root)
    applied: list[_Mutation] = []
    created: list[_CreatedDirectory] = []
    try:
        for change in plan.changes:
            _expected(root_fd, _Operation(
                _validate_change(change),
                change.kind,
                change.content,
                change.expected,
            ))
        with tempfile.TemporaryDirectory(prefix='agents-setup-transaction-') as temporary_root:
            try:
                backups = {
                    operation.path: _backup(root_fd, operation, Path(temporary_root), index)
                    for index, operation in enumerate(operations)
                }
                for operation in operations:
                    _expected(root_fd, operation)
                    _apply(root_fd, guard, operation, backups[operation.path], created, applied)
                _verify_desired(root_fd, plan.changes)
                if postcondition is not None:
                    postcondition()
                _verify_applied(root_fd, applied)
                _verify_desired(root_fd, plan.changes)
            except BaseException as error:
                original = error.original_error if isinstance(error, TransactionError) else error
                raise TransactionError(original, _rollback(root_fd, guard, applied, created)) from error
    finally:
        os.close(root_fd)


def _apply_fallback(
    target_root: Path,
    plan: Plan,
    postcondition: Callable[[], None] | None,
) -> None:
    """Functional fallback with repeated confinement; it cannot provide POSIX openat guarantees."""
    operations = _operations(plan)
    root = Path(target_root)
    root_entry = root.lstat()
    root_identity = (root_entry.st_dev, root_entry.st_ino)
    applied: list[_Mutation] = []
    created: list[_CreatedDirectory] = []

    def target(path: PurePosixPath) -> Path:
        try:
            return confined_target(root, path)
        except ProjectError as error:
            raise TransactionError(error) from error

    def guard() -> None:
        item = root.lstat()
        if stat.S_ISLNK(item.st_mode) or not stat.S_ISDIR(item.st_mode) or (item.st_dev, item.st_ino) != root_identity:
            raise TransactionError('unsafe fallback root namespace changed')

    def entry(path: Path, *, directory: bool = False) -> os.stat_result | None:
        try:
            item = path.lstat()
        except FileNotFoundError:
            return None
        is_link = stat.S_ISLNK(item.st_mode) or _is_link_like(path)
        expected = stat.S_ISDIR(item.st_mode) if directory else stat.S_ISREG(item.st_mode)
        if is_link or not expected:
            raise TransactionError(f'unsafe fallback target: {path}')
        return item

    def observed(
        path: Path,
        *,
        directory: bool = False,
    ) -> ExpectedEntry | None:
        before = entry(path, directory=directory)
        if before is None:
            return None
        identity = (before.st_dev, before.st_ino)
        mode = stat.S_IMODE(before.st_mode)
        if directory:
            return ExpectedEntry(None, mode, identity)
        content = path.read_bytes()
        after = entry(path)
        if after is None or (
            (after.st_dev, after.st_ino) != identity
            or stat.S_IMODE(after.st_mode) != mode
        ):
            raise TransactionError(f'unsafe fallback target changed while reading: {path}')
        return ExpectedEntry(content, mode, identity)

    def ensure_parent(path: Path) -> None:
        guard()
        parent = path.parent
        missing: list[Path] = []
        current = parent
        while not current.exists():
            missing.append(current)
            current = current.parent
        if current.is_symlink() or not current.is_dir():
            raise TransactionError(f'unsafe fallback parent: {current}')
        for directory in reversed(missing):
            guard()
            directory.mkdir()
            item = directory.lstat()
            if _is_link_like(directory) or not stat.S_ISDIR(item.st_mode):
                raise TransactionError(f'unsafe fallback parent: {directory}')
            created.append(_CreatedDirectory(
                directory,
                (item.st_dev, item.st_ino),
            ))

    def sibling(path: Path, content: bytes, mode: int | None) -> Path:
        ensure_parent(path)
        temporary = path.parent / f'.{path.name}.agents-setup-{secrets.token_hex(12)}.tmp'
        guard()
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_BINARY', 0),
            0o666,
        )
        try:
            view = memoryview(content)
            while view:
                written = os.write(descriptor, view)
                view = view[written:]
        finally:
            os.close(descriptor)
        if mode is not None:
            guard()
            temporary.chmod(mode)
        return temporary

    def expected(operation: _Operation) -> None:
        current = observed(
            target(operation.path),
            directory=operation.kind is ChangeKind.DELETE_DIRECTORY,
        )
        if operation.kind is ChangeKind.CREATE and current is not None:
            raise TransactionError(f'create target appeared after planning: {_path_key(operation.path)}')
        if operation.kind in {
            ChangeKind.UPDATE,
            ChangeKind.DELETE,
            ChangeKind.DELETE_DIRECTORY,
        } and current is None:
            raise TransactionError(f'target disappeared after planning: {_path_key(operation.path)}')
        if operation.expected is not None and current != operation.expected:
            raise TransactionError(
                f'target changed after planning: {_path_key(operation.path)}'
            )
        if operation.kind is ChangeKind.UNCHANGED and (
            current is None or current.content != operation.content
        ):
            raise TransactionError(f'content changed before transaction commit: {_path_key(operation.path)}')

    def verify_desired(change: Change) -> None:
        path = target(change.path)
        current = entry(
            path,
            directory=change.kind is ChangeKind.DELETE_DIRECTORY,
        )
        if change.kind in {ChangeKind.DELETE, ChangeKind.DELETE_DIRECTORY}:
            if current is not None:
                raise TransactionError(f'delete result changed: {_path_key(change.path)}')
        elif current is None or path.read_bytes() != change.content:
            raise TransactionError(
                f'content changed before transaction commit: {_path_key(change.path)}'
            )

    def verify_applied() -> None:
        for mutation in applied:
            operation = mutation.backup.operation
            path = target(operation.path)
            current = entry(
                path,
                directory=operation.kind is ChangeKind.DELETE_DIRECTORY,
            )
            identity = None if current is None else (current.st_dev, current.st_ino)
            if operation.kind in {ChangeKind.DELETE, ChangeKind.DELETE_DIRECTORY}:
                if current is not None:
                    raise TransactionError(
                        f'applied target changed before transaction commit: '
                        f'{_path_key(operation.path)}'
                    )
                continue
            if (
                current is None
                or identity != mutation.result_identity
                or path.read_bytes() != mutation.result_content
                or stat.S_IMODE(current.st_mode) != mutation.result_mode
            ):
                raise TransactionError(
                    f'applied target changed before transaction commit: '
                    f'{_path_key(operation.path)}'
                )

    temporary_context = tempfile.TemporaryDirectory(prefix='agents-setup-transaction-')
    try:
        for change in plan.changes:
            expected(_Operation(
                change.path,
                change.kind,
                change.content,
                change.expected,
            ))
        snapshots = Path(temporary_context.name)
        backups: dict[PurePosixPath, _Backup] = {}
        for index, operation in enumerate(operations):
            path = target(operation.path)
            item = observed(
                path,
                directory=operation.kind is ChangeKind.DELETE_DIRECTORY,
            )
            if operation.expected is not None and item != operation.expected:
                raise TransactionError(
                    f'target changed after planning: {_path_key(operation.path)}'
                )
            if item is None:
                backups[operation.path] = _Backup(operation, None, None, None)
            elif operation.kind is ChangeKind.DELETE_DIRECTORY:
                backups[operation.path] = _Backup(
                    operation,
                    None,
                    item.mode,
                    item.identity,
                )
            else:
                snapshot = snapshots / f'{index:04d}'
                assert item.content is not None
                snapshot.write_bytes(item.content)
                backups[operation.path] = _Backup(
                    operation,
                    snapshot,
                    item.mode,
                    item.identity,
                )
        for operation in operations:
            expected(operation)
            backup = backups[operation.path]
            path = target(operation.path)
            guard()
            current = observed(
                path,
                directory=operation.kind is ChangeKind.DELETE_DIRECTORY,
            )
            backup_content = (
                None if backup.snapshot is None else backup.snapshot.read_bytes()
            )
            backup_entry = (
                None
                if backup.identity is None or backup.mode is None
                else ExpectedEntry(backup_content, backup.mode, backup.identity)
            )
            if current != backup_entry:
                raise TransactionError(f'unsafe fallback final target changed: {_path_key(operation.path)}')
            if operation.kind in {ChangeKind.DELETE, ChangeKind.DELETE_DIRECTORY}:
                applied.append(_Mutation(backup, None, None, None))
                if operation.kind is ChangeKind.DELETE_DIRECTORY:
                    path.rmdir()
                else:
                    path.unlink()
                continue
            assert operation.content is not None
            temporary = sibling(path, operation.content, backup.mode)
            try:
                current = observed(target(operation.path))
                if current != backup_entry:
                    raise TransactionError(f'unsafe fallback final target changed: {_path_key(operation.path)}')
                current_parent = target(operation.path).parent.stat()
                temporary_parent = temporary.parent.stat()
                if (current_parent.st_dev, current_parent.st_ino) != (temporary_parent.st_dev, temporary_parent.st_ino):
                    raise TransactionError(f'unsafe fallback parent changed: {_path_key(operation.path)}')
                temp_entry = temporary.stat()
                applied.append(_Mutation(
                    backup,
                    (temp_entry.st_dev, temp_entry.st_ino),
                    operation.content,
                    stat.S_IMODE(temp_entry.st_mode),
                ))
                guard()
                _replace(temporary, path)
            finally:
                temporary.unlink(missing_ok=True)
        for change in plan.changes:
            verify_desired(change)
        if postcondition is not None:
            postcondition()
        verify_applied()
        for change in plan.changes:
            verify_desired(change)
    except BaseException as error:
        rollback_errors: list[BaseException] = []
        try:
            guard()
        except BaseException as rollback_error:
            rollback_errors.append(rollback_error)
            original = error.original_error if isinstance(error, TransactionError) else error
            raise TransactionError(original, tuple(rollback_errors)) from error
        for mutation in reversed(applied):
            try:
                guard()
                backup = mutation.backup
                operation = backup.operation
                guard()
                path = target(operation.path)
                guard()
                current = entry(
                    path,
                    directory=operation.kind is ChangeKind.DELETE_DIRECTORY,
                )
                identity = None if current is None else (current.st_dev, current.st_ino)
                if identity == backup.identity:
                    continue
                if identity != mutation.result_identity:
                    raise TransactionError(f'third-party fallback target retained: {_path_key(operation.path)}')
                if current is not None and (
                    path.read_bytes() != mutation.result_content
                    or stat.S_IMODE(current.st_mode) != mutation.result_mode
                ):
                    raise TransactionError(
                        f'third-party fallback target retained: {_path_key(operation.path)}'
                    )
                if operation.kind is ChangeKind.DELETE_DIRECTORY:
                    if backup.identity is None:
                        raise TransactionError(
                            f'directory backup is missing: {_path_key(operation.path)}'
                        )
                    guard()
                    path.mkdir(mode=backup.mode if backup.mode is not None else 0o777)
                elif backup.snapshot is None:
                    if current is not None:
                        guard()
                        path.unlink()
                else:
                    guard()
                    temporary = sibling(path, backup.snapshot.read_bytes(), backup.mode)
                    try:
                        guard()
                        os.replace(temporary, path)
                    finally:
                        temporary.unlink(missing_ok=True)
            except BaseException as rollback_error:
                rollback_errors.append(rollback_error)
        for item in reversed(created):
            assert isinstance(item.path, Path)
            directory = item.path
            try:
                guard()
                current = entry(directory, directory=True)
                if current is None:
                    continue
                if (current.st_dev, current.st_ino) != item.identity:
                    raise TransactionError(
                        f'third-party fallback directory retained: {directory}'
                    )
                guard()
                directory.rmdir()
            except BaseException as rollback_error:
                rollback_errors.append(rollback_error)
                if 'fallback root namespace changed' in str(rollback_error):
                    break
        original = error.original_error if isinstance(error, TransactionError) else error
        raise TransactionError(original, tuple(rollback_errors)) from error
    finally:
        temporary_context.cleanup()


def apply_plan(
    target_root: Path,
    plan: Plan,
    *,
    postcondition: Callable[[], None] | None = None,
) -> None:
    """Apply a plan; callers provide exclusive access to its targets during this call.

    Descriptor-relative operations close namespace traversal attacks where available, but host
    filesystems expose no portable compare-and-swap replacement or deletion by prior identity.
    """
    if _SECURE_DIR_FDS:
        try:
            _apply_secure(Path(target_root), plan, postcondition)
        except BaseException as error:
            if isinstance(error, TransactionError):
                raise
            raise TransactionError(error) from error
        return
    try:
        _apply_fallback(Path(target_root), plan, postcondition)
    except BaseException as error:
        if isinstance(error, TransactionError):
            raise
        raise TransactionError(error) from error
