"""Ask the last-focused VS Code window to open a registered Git comparison."""
from __future__ import annotations

import http.client
import json
from pathlib import Path
import re

from .storage import read_json, state_dir


def open_registered_diff(repo: Path, before_uri: str, after: Path) -> bool:
    """Return false only when no editor request was sent or the window declined it."""
    try:
        metadata = read_json(state_dir() / "vscode-bridge.json")
    except (OSError, ValueError):
        # Discovery has sent no request; ordinary file comparison is still safe.
        return False
    if (not isinstance(metadata, dict) or type(metadata.get("protocol")) is not int
            or metadata["protocol"] != 1):
        return False
    port, token = metadata.get("port"), metadata.get("token")
    if (type(port) is not int or not 1 <= port <= 65535
            or not isinstance(token, str) or re.fullmatch(r"[0-9a-f]{64}", token) is None):
        return False
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        try:
            connection.connect()
        except OSError:
            return False
        # After sending, a lost reply cannot prove that the editor did not open.
        # Propagate that uncertainty rather than dispatching a second editor request.
        try:
            connection.request("POST", "/diff", json.dumps({
                "repo": repo.as_uri(), "before": before_uri, "after": after.as_uri(),
            }).encode("utf-8"), {
                "Authorization": "Bearer " + token, "Content-Type": "application/json",
            })
            response = connection.getresponse()
            if response.status in (401, 404):
                return False
            content = response.read(4097)
            if response.status != 200 or len(content) > 4096:
                raise ValueError("VS Code bridge did not confirm the comparison")
            result = json.loads(content)
            if result == {"status": "fallback"}:
                return False
            if result != {"status": "opened"}:
                raise ValueError("VS Code bridge returned an unknown result")
            return True
        except (OSError, http.client.HTTPException) as error:
            raise OSError("VS Code comparison was sent, but its result is unknown") from error
    finally:
        connection.close()
