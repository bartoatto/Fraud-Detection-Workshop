"""Small helpers for finding a NetApp Volume through Domino's remote file system API.

Used by the job launcher and the flow definition, which both need the volume's ID. Run these
from a workspace: they use the workspace's access token.
"""
import os

import requests


def _get(path: str) -> list:
    token = requests.get("http://localhost:8899/access-token", timeout=10).text.strip()
    url = f"{os.environ['DOMINO_REMOTE_FILE_SYSTEM_HOSTPORT']}/remotefs/v1/{path}"
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    response.raise_for_status()
    return response.json()["data"]


def find_volume(name: str) -> dict:
    """Return the NetApp Volume with this exact name."""
    for volume in _get("volumes"):
        if volume["name"] == name:
            return volume
    raise LookupError(f"NetApp Volume '{name}' was not found (or you do not have access to it).")


def find_snapshot(volume_id: str, tag: str) -> dict:
    """Return the snapshot of a volume that carries this tag."""
    for snapshot in _get("snapshots"):
        if snapshot.get("volumeId") == volume_id and tag in [t["name"] for t in snapshot.get("tags", [])]:
            return snapshot
    raise LookupError(f"No snapshot of the volume is tagged '{tag}'.")
