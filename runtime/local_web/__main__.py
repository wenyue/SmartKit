#!/usr/bin/env python
"""Run the supported local host CLI from any working directory."""
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from local_web.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
