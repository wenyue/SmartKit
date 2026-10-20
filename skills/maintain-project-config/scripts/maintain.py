#!/usr/bin/env python
"""Maintain project configuration through the owning Skill's command interface."""
from __future__ import annotations

import argparse
from typing import Sequence

from project_config import project_configuration_cli


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    project_configuration_cli.add_arguments(parser, include_sync=True)
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return int(error.code)
    return project_configuration_cli.run(args)


if __name__ == '__main__':
    raise SystemExit(main())
