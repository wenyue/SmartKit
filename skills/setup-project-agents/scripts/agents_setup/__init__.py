"""Full setup orchestration over the project configuration maintenance engine."""
from pathlib import Path
import sys

# The complete plugin exposes maintenance support to setup and its consumers.
_MAINTENANCE_SCRIPTS = Path(__file__).resolve().parents[3] / 'maintain-project-config/scripts'
if str(_MAINTENANCE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_MAINTENANCE_SCRIPTS))
_RUNTIME = Path(__file__).resolve().parents[4] / 'runtime'
if str(_RUNTIME) not in sys.path:
    sys.path.insert(0, str(_RUNTIME))
