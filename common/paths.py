"""Where the workshop reads and writes files.

The study data lives on a NetApp Volume attached to the project. Domino mounts it under
/domino/netapp-volumes (DFS projects) or /mnt/netapp-volumes (Git-based projects), so these
paths work in workspaces, jobs and apps alike.

Volume layout (mirrors a typical SCE study folder):
    adam/adsl.sas7bdat       ADaM subject-level dataset (input)
    tfl/                     production tables
    qc/tfl/                  independently programmed QC tables
    compare/                 prod-vs-QC comparison results
    signoff/                 reviewer sign-off log

Environment variables (all optional):
    STUDY_DATA_DIR     use this folder instead of the NetApp volume (for running outside Domino)
    ADSL_SNAPSHOT_VERSION  read ADSL from that snapshot number (flow tasks mount a snapshot)
    ADSL_SNAPSHOT_TAG  read ADSL from that snapshot tag of the volume, so a run is reproducible
"""
import json
import os
from pathlib import Path

VOLUME_NAME = "cdisc01-study-data"
MOUNT_ROOTS = ("/domino/netapp-volumes", "/mnt/netapp-volumes")

PROJECT_DIR = Path(os.environ.get("DOMINO_WORKING_DIR") or Path(__file__).resolve().parents[1])
# Git-based projects have a separate artifacts store; DFS projects just use a folder in the project.
if os.environ.get("DOMINO_IS_GIT_BASED") == "true":
    ARTIFACTS_DIR = Path(os.environ.get("DOMINO_ARTIFACTS_DIR", "/mnt/artifacts"))
else:
    ARTIFACTS_DIR = PROJECT_DIR / "artifacts"


def _mount_root() -> Path:
    for root in MOUNT_ROOTS:
        if (Path(root) / VOLUME_NAME).is_dir() or (Path(root) / "snapshots" / VOLUME_NAME).is_dir():
            return Path(root)
    raise FileNotFoundError(
        f"NetApp Volume '{VOLUME_NAME}' is not mounted. Add it to this project under "
        "Data > NetApp Volumes, then restart the workspace or job.")


def _data_dir() -> Path:
    if os.environ.get("STUDY_DATA_DIR"):
        return Path(os.environ["STUDY_DATA_DIR"])
    root = _mount_root()
    live = root / VOLUME_NAME
    if live.is_dir():
        return live
    # Flow tasks mount a read-only snapshot instead of the live volume.
    version = os.environ.get("ADSL_SNAPSHOT_VERSION")
    if version:
        return root / "snapshots" / VOLUME_NAME / version
    raise FileNotFoundError(f"Only snapshots of '{VOLUME_NAME}' are mounted; set ADSL_SNAPSHOT_VERSION.")


DATA_DIR = _data_dir()


def _adsl_file() -> Path:
    if os.environ.get("STUDY_DATA_DIR"):
        return DATA_DIR / "adam" / "adsl.sas7bdat"
    tag = os.environ.get("ADSL_SNAPSHOT_TAG")
    version = os.environ.get("ADSL_SNAPSHOT_VERSION")
    if tag:
        return _mount_root() / "snapshot-tags" / VOLUME_NAME / tag / "adam" / "adsl.sas7bdat"
    if version:
        return _mount_root() / "snapshots" / VOLUME_NAME / version / "adam" / "adsl.sas7bdat"
    return DATA_DIR / "adam" / "adsl.sas7bdat"


ADSL_FILE = _adsl_file()

PROD_DIR = DATA_DIR / "tfl"
QC_DIR = DATA_DIR / "qc" / "tfl"
COMPARE_DIR = DATA_DIR / "compare"
SIGNOFF_DIR = DATA_DIR / "signoff"

PROD_DM1 = PROD_DIR / "t_dm1.csv"
PROD_DM1_HTML = PROD_DIR / "t_dm1.html"
QC_DM1 = QC_DIR / "qc_t_dm1.csv"
COMPARE_DM1 = COMPARE_DIR / "t_dm1_compare.csv"
COMPARE_SUMMARY = COMPARE_DIR / "t_dm1_summary.json"
SIGNOFF_LOG = SIGNOFF_DIR / "signoff_log.csv"


def artifact_dir(name: str) -> Path:
    """Return (and create) an artifacts sub-folder for one exercise."""
    path = ARTIFACTS_DIR / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure(*dirs: Path) -> None:
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def write_dominostats(stats: dict) -> Path:
    """Write dominostats.json so Domino shows the values on the Jobs screen.

    Git-based projects read it from /mnt/artifacts, DFS projects from the project root.
    """
    git_based = os.environ.get("DOMINO_IS_GIT_BASED") == "true"
    target = (ARTIFACTS_DIR if git_based else PROJECT_DIR) / "dominostats.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(stats, indent=2))
    return target
