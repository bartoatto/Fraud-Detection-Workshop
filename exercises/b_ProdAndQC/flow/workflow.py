"""The demographics table as a Domino Flow: production and QC run in parallel, then the comparison.

This is the same work as run_t_dm1.py, but each step is its own job, so the two programs run
at the same time and every step is tracked in the flow's lineage graph.

Flow jobs do not get the project's live volume, so each step mounts a read-only snapshot of
the study volume (the one tagged adsl-v1, set in common/config.py), which appears at the usual volume path. Nothing is
written back to the volume: each step passes its table to the next as a file.

Before running it, the data must be snapshotted: the volume needs a snapshot tagged adsl-v1
(Data > NetApp Volumes > your volume > Take Snapshot). The flow stops with a clear message if
there is none.

Commit and sync first (flow jobs run the project files, not your unsaved edits), then from a
workspace terminal:

    PYTHONPATH=$DOMINO_WORKING_DIR pyflyte run --remote exercises/b_ProdAndQC/flow/workflow.py demographics_table

For a Git-based project that should run a branch other than the default, set FLOW_GIT_REF.
"""
import os
from pathlib import Path
from typing import TypeVar

from flytekit import workflow
from flytekit.types.file import FlyteFile
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask, GitRef, NetAppVolumeSnapshot

from common.config import FLOW_SNAPSHOT_TAG, VOLUME_NAME
from common.domino_api import find_snapshot, find_volume

PROJECT_DIR = Path(os.environ.get("DOMINO_WORKING_DIR") or Path(__file__).resolve().parents[3]).resolve()
# The step scripts sit next to this file; their paths are given relative to the project.
FLOW_DIR = Path(__file__).resolve().parent.relative_to(PROJECT_DIR)

# Look the volume and snapshot up by name so nothing deployment-specific is written in the code.
_volume = find_volume(VOLUME_NAME)
_snapshot = find_snapshot(_volume["id"], FLOW_SNAPSHOT_TAG)
VOLUME_SNAPSHOTS = [NetAppVolumeSnapshot(Id=_volume["id"], Version=_snapshot["version"], Name=VOLUME_NAME)]
GIT_REF = GitRef(Type="branches", Value=os.environ["FLOW_GIT_REF"]) if os.environ.get("FLOW_GIT_REF") else None


def _command(script: str) -> str:
    # QC_INTRODUCE_DIFF is passed through so the presenter demo works in the flow too.
    env = "QC_INTRODUCE_DIFF=1 " if os.environ.get("QC_INTRODUCE_DIFF") else ""
    return (f"bash -c 'cd $DOMINO_WORKING_DIR && PYTHONPATH=$DOMINO_WORKING_DIR {env}"
            f"python {FLOW_DIR / script}'")


def _job(name: str, script: str, inputs: dict, outputs: dict) -> DominoJobTask:
    config = DominoJobConfig(Command=_command(script), NetAppVolumeSnapshots=VOLUME_SNAPSHOTS)
    if GIT_REF:
        config.MainRepoGitRef = GIT_REF
    return DominoJobTask(name=name, domino_job_config=config, inputs=inputs, outputs=outputs, use_latest=True)


CSV = FlyteFile[TypeVar("csv")]

prod_task = _job("Production: demographics table", "flow_prod.py", {}, {"table": CSV})
qc_task = _job("QC: demographics table", "flow_qc.py", {}, {"table": CSV})
compare_task = _job("Compare production and QC", "flow_compare.py",
                    {"prod_table": CSV, "qc_table": CSV}, {"summary": str})


@workflow
def demographics_table() -> str:
    prod = prod_task()
    qc = qc_task()
    return compare_task(prod_table=prod, qc_table=qc)
