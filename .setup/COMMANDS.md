# Workshop commands

Everything you run, in order. All commands run in a **workspace terminal** in the project root (`/mnt` in a DFS project). Sync your files first: jobs and flows run the synced project, not unsaved edits.

## 0. Before the session (once)

The data file `adsl.sas7bdat` is not in the code bundle. Put it at the **root** of a NetApp Volume named exactly `cdisc01-study-data` (the volume is flat: no subfolders).

1. Data > NetApp Volumes > Create Volume. Name: `cdisc01-study-data`. Give access to the people who will run the workshop.
2. Attach it to the project: Data > NetApp Volumes > Add Existing Volume.
3. Start a workspace (the volume mounts at `/domino/netapp-volumes/cdisc01-study-data/`) and copy the file in.
4. On the volume page, choose **Take Snapshot**. The flow reads the latest snapshot, so take it after the file is in place.

Check the setup:

```bash
python .setup/verify_environment.py
python -c "from common import paths; print(paths.ADSL_FILE, paths.ADSL_FILE.exists())"
```

The first prints `PASS`. The second prints the path and `True`.

## 1. Exercise A: explore the data

No command. Open `exercises/a_ExploreADSL/explore_adsl.ipynb` in JupyterLab and run the cells top to bottom. Plots are saved under `artifacts/a_explore_adsl/`.

## 2. Exercise B: the job

Start production, QC and compare as one Domino job:

```bash
python exercises/b_ProdAndQC/jobs/launch_job.py
```

It prints the job number and returns straight away. Open **Jobs**. Expected: Status **Clean**, Cells compared **120**, Cell differences **0**. The outputs appear on the volume (`t_dm1.csv`, `t_dm1.html`, `qc_t_dm1.csv`, `t_dm1_compare.csv`, `t_dm1_summary.json`).

Presenter demo, catch a difference:

```bash
QC_INTRODUCE_DIFF=1 python exercises/b_ProdAndQC/jobs/launch_job.py   # status becomes Issues
python exercises/b_ProdAndQC/jobs/launch_job.py                       # run again: back to Clean
```

Optional, reproducible run from a snapshot tag. First give a snapshot the tag `adsl-v1` (Data > NetApp Volumes > your volume > Snapshots), then:

```bash
env ADSL_SNAPSHOT_TAG=adsl-v1 python exercises/b_ProdAndQC/jobs/prod_t_dm1.py
```

## 3. Exercise B (optional): the flow

```bash
pyflyte run --remote exercises/b_ProdAndQC/flow/workflow.py demographics_table
```

Open **Flows** for the graph: production and QC run at the same time, then compare. Click the compare step and read its logs: Clean, 120 cells, 0 differences. The flow uses the latest snapshot of the volume; to use a tag instead, put `FLOW_SNAPSHOT_TAG=<tag>` in front of the command.

## 4. Exercise C: the app

Optional check in the workspace:

```bash
PORT=8501 bash exercises/c_StudyReviewApp/app.sh
```

Then publish it: Deployments > Apps > Publish, entry point `exercises/c_StudyReviewApp/app.sh`. Run the Exercise B job at least once first: the app's last tab reads the job's output files.

## 5. Git-based projects only

Push the code to a branch, then add the branch to the commands:

```bash
JOB_GIT_BRANCH=<branch> python exercises/b_ProdAndQC/jobs/launch_job.py
FLOW_GIT_REF=<branch> pyflyte run --remote exercises/b_ProdAndQC/flow/workflow.py demographics_table
```

## 6. Clean up before the session

On the volume, delete `t_dm1.csv`, `t_dm1.html`, `qc_t_dm1.csv`, `t_dm1_compare.csv` and `t_dm1_summary.json`. Keep `adsl.sas7bdat`. Clear `results/` in the project.

## If something fails

| Message or symptom | Cause and fix |
|---|---|
| `NetApp Volume 'cdisc01-study-data' is not mounted` | The job did not get the volume. Start it with `launch_job.py`, which asks for the volume itself. In the Run Job dialog, tick the volume and select **All snapshots**; check the job's Details lists it. |
| `NetApp Volume ... was not found` | The volume name is different, or you do not have access to it. Fix the name or the access. |
| `No snapshot of the volume ... at all` | Take a snapshot of the volume (Data > NetApp Volumes > Take Snapshot). |
| `No snapshot ... tagged '<tag>'` | You set `FLOW_SNAPSHOT_TAG` (or ran the tag step) and no snapshot has that tag. Tag one, or leave the variable unset. |
| Flow still asks for the tag `adsl-v1` | Your project has old code. Replace `common/domino_api.py`, `common/config.py` and `exercises/b_ProdAndQC/flow/workflow.py` with the current versions and sync. |
| `ModuleNotFoundError: No module named 'common'` | Run the command from the project root, or put `PYTHONPATH=$DOMINO_WORKING_DIR` in front. |
| Job marked **Failed** although the logs end with Clean and exit code 0 | A platform status problem, not the code: the outputs and the Clean result are valid. Run it again, and report it to your Domino admin if it repeats. |
| Flow's compare job shows no stats on the Jobs screen | Expected. Read the result in the compare step's logs in the flow. |
