"""Start the Table 14.1 job from a script, using the Domino Python library.

Instead of clicking Run Job in the UI, this submits the same job through Domino's API and
returns straight away. Watch it under Jobs. Sync your workspace first, because the job runs
the project's files, not your unsaved edits.

Run from a workspace terminal:  python exercises/b_ProdAndQC/launch_job.py
"""
import os
import sys

from domino import Domino

sys.path.append(os.environ.get("DOMINO_WORKING_DIR", "."))
from common.domino_api import find_volume

VOLUME_NAME = "cdisc01-study-data"
COMMAND = "python exercises/b_ProdAndQC/run_t_dm1.py"
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
