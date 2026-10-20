"""Catalog types consumed by project readiness and configuration maintenance."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import PurePosixPath
from typing import Mapping


class ContractError(ValueError):
    """Raised when a setup contract document is invalid."""


class Harness(str, Enum):
    CODEX = 'codex'
    CURSOR = 'cursor'
    COPILOT = 'copilot'
    QODER = 'qoder'


@dataclass(frozen=True)
class AssetSpec:
    id: str
    kind: str
    source: PurePosixPath
    target: PurePosixPath | None
    harnesses: tuple[Harness, ...]
    control_plane: bool = False
    metadata: Mapping[str, object] = field(default_factory=dict)
    skill_id: str | None = None


@dataclass(frozen=True)
class Catalog:
    plugin_id: str
    plugin_version: str
    repository: str
    ref: str
    assets: tuple[AssetSpec, ...]
