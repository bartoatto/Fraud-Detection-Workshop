"""Where the workshop reads and writes files.

The study data lives on a NetApp Volume attached to the project. Domino mounts it under
/domino/netapp-volumes (DFS projects) or /mnt/netapp-volumes (Git-based projects), so these
paths work in workspaces, jobs and apps alike.

Volume layout: flat, every file sits directly in the volume (no subfolders).
    adsl.sas7bdat       ADaM subject-level dataset (input)
    t_dm1.csv/.html     production demographics table
    qc_t_dm1.csv        independently programmed QC table
    t_dm1_compare.csv   prod-vs-QC differences
    t_dm1_summary.json  prod-vs-QC summary

Plots are not written to the volume: the notebook saves them under the project's artifacts folder.

Environment variables (all optional):
    STUDY_DATA_DIR     use this folder instead of the NetApp volume (for running outside Domino)
    STUDY_VOLUME_NAME  use a differently named volume (see common/config.py)
    ADSL_SNAPSHOT_TAG  read ADSL from that snapshot tag of the volume, so a run is reproducible
"""
import json
import os
from pathlib import Path

from common.config import MOUNT_ROOTS, VOLUME_NAME

PROJECT_DIR = Path(os.environ.get("DOMINO_WORKING_DIR") or Path(__file__).resolve().parents[1])
# Git-based projects have a separate artifacts store; DFS projects just use a folder in the project.
if os.environ.get("DOMINO_IS_GIT_BASED") == "true":
    ARTIFACTS_DIR = Path(os.environ.get("DOMINO_ARTIFACTS_DIR", "/mnt/artifacts"))
else:
    ARTIFACTS_DIR = PROJECT_DIR / "artifacts"


def _mount_root() -> Path:
    for root in MOUNT_ROOTS:
        if (Path(root) / VOLUME_NAME).is_dir():
            return Path(root)
    raise FileNotFoundError(
        f"NetApp Volume '{VOLUME_NAME}' is not mounted. Add it to this project under "
        "Data > NetApp Volumes, then restart the workspace or job.")


def _data_dir() -> Path:
    if os.environ.get("STUDY_DATA_DIR"):
        return Path(os.environ["STUDY_DATA_DIR"])
    return _mount_root() / VOLUME_NAME


DATA_DIR = _data_dir()


def _adsl_file() -> Path:
    tag = os.environ.get("ADSL_SNAPSHOT_TAG")
    if tag and not os.environ.get("STUDY_DATA_DIR"):
        return _mount_root() / "snapshot-tags" / VOLUME_NAME / tag / "adsl.sas7bdat"
    return DATA_DIR / "adsl.sas7bdat"


ADSL_FILE = _adsl_file()

PROD_DM1 = DATA_DIR / "t_dm1.csv"
PROD_DM1_HTML = DATA_DIR / "t_dm1.html"
QC_DM1 = DATA_DIR / "qc_t_dm1.csv"
COMPARE_DM1 = DATA_DIR / "t_dm1_compare.csv"
COMPARE_SUMMARY = DATA_DIR / "t_dm1_summary.json"


def artifact_dir(name: str) -> Path:
    """Return (and create) an artifacts sub-folder for one exercise."""
    path = ARTIFACTS_DIR / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_dominostats(stats: dict) -> Path:
    """Write dominostats.json so Domino shows the values on the Jobs screen.

    Git-based projects read it from /mnt/artifacts, DFS projects from the project root.
    """
    git_based = os.environ.get("DOMINO_IS_GIT_BASED") == "true"
    target = (ARTIFACTS_DIR if git_based else PROJECT_DIR) / "dominostats.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(stats, indent=2))
    return target
