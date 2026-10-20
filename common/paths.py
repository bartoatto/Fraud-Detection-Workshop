"""Where the workshop reads and writes files.

The data lives on a NetApp Volume that is attached to the project. Domino mounts it under
/domino/netapp-volumes (DFS projects) or /mnt/netapp-volumes (Git-based projects), so these
paths work in workspaces, jobs and apps alike. Set FRAUD_DATA_DIR to point at another folder,
for example when running outside Domino.
"""
import os
from pathlib import Path

VOLUME_NAME = "partner-sce-fraud-data"

PROJECT_DIR = Path(os.environ.get("DOMINO_WORKING_DIR") or Path(__file__).resolve().parents[1])
ARTIFACTS_DIR = PROJECT_DIR / "artifacts"


def _data_dir() -> Path:
    if os.environ.get("FRAUD_DATA_DIR"):
        return Path(os.environ["FRAUD_DATA_DIR"])
    for root in ("/domino/netapp-volumes", "/mnt/netapp-volumes"):
        if (Path(root) / VOLUME_NAME).is_dir():
            return Path(root) / VOLUME_NAME
    raise FileNotFoundError(
        f"NetApp Volume '{VOLUME_NAME}' is not mounted. Add it to this project under "
        "Data > NetApp Volumes, then restart the workspace or job.")


DATA_DIR = _data_dir()

RAW_FILE = DATA_DIR / "raw_cc_transactions.csv.gz"
CLEAN_FILE = DATA_DIR / "clean_cc_transactions.csv"
ENGINEERED_FILE = DATA_DIR / "engineered_cc_transactions.csv"

DECISIONS_FILE = ARTIFACTS_DIR / "review_decisions.csv"


def artifact_dir(name: str) -> Path:
    """Return (and create) an artifacts sub-folder for one exercise."""
    path = ARTIFACTS_DIR / name
    path.mkdir(parents=True, exist_ok=True)
    return path
