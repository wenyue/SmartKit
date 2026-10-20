from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from project_state.models import Catalog
from project_state.paths import _confined_root, confined_target

from .catalog import load_project_config
from .models import ProjectConfig


@dataclass(frozen=True)
class ProjectState:
    root: Path
    config: ProjectConfig


def inspect_project(target_root: Path, *, catalog: Catalog) -> ProjectState:
    """Load target-owned setup state without changing the target project."""
    root = _confined_root(target_root)
    config_path = confined_target(root, PurePosixPath('.agents/config.json'))
    return ProjectState(
        root=root,
        config=load_project_config(config_path, catalog=catalog),
    )
