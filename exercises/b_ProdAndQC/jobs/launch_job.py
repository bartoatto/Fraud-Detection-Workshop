"""Start the Table 14.1 job from a script, using the Domino Python library.

Instead of clicking Run Job in the UI, this submits the same job through Domino's API and
returns straight away. Watch it under Jobs. Sync your workspace first, because the job runs
the project's files, not your unsaved edits.

Run from a workspace terminal:  python exercises/b_ProdAndQC/jobs/launch_job.py
"""
import os
import sys
from pathlib import Path

from domino import Domino

PROJECT_DIR = Path(os.environ.get("DOMINO_WORKING_DIR") or Path(__file__).resolve().parents[3])
sys.path.append(str(PROJECT_DIR))
from common.config import VOLUME_NAME
from common.domino_api import find_volume

# The job to run: the run_t_dm1.py next to this script, as a path relative to the project.
SCRIPT = Path(__file__).resolve().with_name("run_t_dm1.py").relative_to(PROJECT_DIR.resolve())
COMMAND = f"python {SCRIPT}"
TITLE = "Table 14.1: production, QC and compare"

project = f"{os.environ['DOMINO_PROJECT_OWNER']}/{os.environ['DOMINO_PROJECT_NAME']}"
domino = Domino(project, api_key=os.environ["DOMINO_USER_API_KEY"], host=os.environ["DOMINO_API_HOST"])

job = {
    "projectId": os.environ["DOMINO_PROJECT_ID"],
    "runCommand": COMMAND,
    "title": TITLE,
    "hardwareTierId": os.environ["DOMINO_HARDWARE_TIER_ID"],
    "environmentId": os.environ["DOMINO_ENVIRONMENT_ID"],
    # The job must be told to mount the study volume; it is not mounted by default.
    "netAppVolumeIds": [find_volume(VOLUME_NAME)["id"]],
}
branch = os.environ.get("JOB_GIT_BRANCH")  # only for Git-based projects
if branch:
    job["mainRepoGitRef"] = {"refType": "branches", "value": branch}

response = domino.request_manager.post(f"{os.environ['DOMINO_API_HOST']}/api/jobs/v1/jobs", json=job)
started = response.json()["job"]
print(f"Started job #{started['number']} ({started['id']}). Watch it under Jobs.")
