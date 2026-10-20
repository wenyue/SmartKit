"""Project configuration maintenance over Hook-owned read contracts."""
from pathlib import Path
import sys


_RUNTIME = Path(__file__).resolve().parents[4] / "runtime"
if str(_RUNTIME) not in sys.path:
    sys.path.insert(0, str(_RUNTIME))
