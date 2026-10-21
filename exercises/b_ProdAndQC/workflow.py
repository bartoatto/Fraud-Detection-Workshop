"""Table 14.1 as a Domino Flow: production and QC run in parallel, then the comparison.

This is the same work as run_t_dm1.py, but each step is its own job, so the two programs run
at the same time and every step is tracked in the flow's lineage graph.

Flow jobs do not get the project's live volume, so each step mounts a read-only snapshot of
the study volume (the one tagged adsl-v1) and passes its table to the next step as text.

Commit and sync first (flow jobs run the project files, not your unsaved edits), then from a
workspace terminal:

    PYTHONPATH=/mnt/code pyflyte run --remote exercises/b_ProdAndQC/workflow.py table_14_1

For a Git-based project that should run a branch other than the default, set FLOW_GIT_REF.
"""
import os

from flytekit import workflow
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask, GitRef, NetAppVolumeSnapshot

from common.domino_api import find_snapshot, find_volume

VOLUME_NAME = "cdisc01-study-data"
SNAPSHOT_TAG = "adsl-v1"

# Look the volume and snapshot up by name so nothing deployment-specific is written in the code.
_volume = find_volume(VOLUME_NAME)
_snapshot = find_snapshot(_volume["id"], SNAPSHOT_TAG)
VOLUME_SNAPSHOTS = [NetAppVolumeSnapshot(Id=_volume["id"], Version=_snapshot["version"], Name=VOLUME_NAME)]
GIT_REF = GitRef(Type="branches", Value=os.environ["FLOW_GIT_REF"]) if os.environ.get("FLOW_GIT_REF") else None


def _command(script: str) -> str:
    env = f"ADSL_SNAPSHOT_VERSION={_snapshot['version']}"
    # QC_INTRODUCE_DIFF is passed through so the presenter demo works in the flow too.
    if os.environ.get("QC_INTRODUCE_DIFF"):
        env += " QC_INTRODUCE_DIFF=1"
    return (f"bash -c 'cd $DOMINO_WORKING_DIR && PYTHONPATH=$DOMINO_WORKING_DIR {env} "
            f"python exercises/b_ProdAndQC/{script}'")


def _job(name: str, script: str, inputs: dict, outputs: dict) -> DominoJobTask:
    config = DominoJobConfig(Command=_command(script), NetAppVolumeSnapshots=VOLUME_SNAPSHOTS)
    if GIT_REF:
        config.MainRepoGitRef = GIT_REF
    return DominoJobTask(name=name, domino_job_config=config, inputs=inputs, outputs=outputs, use_latest=True)


prod_task = _job("Production: Table 14.1", "flow_prod.py", {}, {"table": str})
qc_task = _job("QC: Table 14.1", "flow_qc.py", {}, {"table": str})
compare_task = _job("Compare production and QC", "flow_compare.py",
                    {"prod_table": str, "qc_table": str}, {"summary": str})


@workflow
def table_14_1() -> str:
    prod = prod_task()
    qc = qc_task()
    return compare_task(prod_table=prod, qc_table=qc)
