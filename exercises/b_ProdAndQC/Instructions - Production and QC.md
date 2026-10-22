# Production, QC and Compare
The exercise has two parts. `jobs/` holds the programs and the ways to run them as jobs. `flow/` holds the same work as a Domino Flow (optional).

Clinical outputs are programmed twice: a **production** programmer builds the table, and a **QC** programmer rebuilds it independently without looking at the first. A third step compares the two. You will run all three together as one Domino **Job**.

The table is the demographics table, a summary of demographic and baseline characteristics for the safety population, by treatment arm. Every program reads ADSL from, and writes its results back to, the NetApp Volume.

## Exercise Instructions

1. Open `jobs/prod_t_dm1.py` and `jobs/qc_t_dm1.py` in the workspace and skim them. They compute the same table in different ways. Do not modify them.
2. Sync your changes, then click **Run Job** and enter `python exercises/b_ProdAndQC/jobs/run_t_dm1.py`. This runs the production program, then the QC program, then the comparison, in order. (Each program can also be run as its own Job: `jobs/prod_t_dm1.py`, `jobs/qc_t_dm1.py`, `jobs/compare_t_dm1.py`.)
3. Open **Jobs** and click the job. Watch the logs: you can see the three steps go by. When it finishes, note the **Status**, **Cells compared** and **Cell differences** values that appear on the Jobs screen.
4. On the NetApp Volume, find the outputs:
   - `t_dm1.csv` and `t_dm1.html` - the production table
   - `qc_t_dm1.csv` - the QC table
   - `t_dm1_summary.json` - the comparison result

### Optional: start the job from a script
Instead of clicking Run Job, submit the same job from the workspace terminal with the Domino Python library:

`python exercises/b_ProdAndQC/jobs/launch_job.py`

It returns straight away and prints the job number. Watch it under **Jobs**. Sync first, because the job runs the project files, not your unsaved edits.

### Optional: run it as a Flow
`flow/workflow.py` defines the same work as a Domino Flow: the production and QC programs run **at the same time** as two jobs, and the comparison starts when both have finished. Each step is its own job, and the flow records how they connect.

**Snapshot the data first.** Flow jobs do not get the live volume; they mount a read-only snapshot. Take a snapshot of the volume once `adsl.sas7bdat` is on it (Data > NetApp Volumes > your volume > Take Snapshot). The flow uses the latest snapshot, and stops with a message if the volume has none.

Then, from the workspace terminal:

`pyflyte run --remote exercises/b_ProdAndQC/flow/workflow.py demographics_table`

Watch it under **Flows**. The Jobs screen shows the production, QC and compare jobs, with the comparison's Status, Cells compared and Cell differences.

### Optional: reproducible runs with a snapshot tag
A snapshot tag freezes the input. Give your snapshot the tag `adsl-v1` (Data > NetApp Volumes > your volume > Snapshots), then run the production job again with the command:

`env ADSL_SNAPSHOT_TAG=adsl-v1 python exercises/b_ProdAndQC/jobs/prod_t_dm1.py`

(`env` sets the variable for that one command.) It now reads ADSL from the `adsl-v1` snapshot of the volume, not the live files, so the result can be reproduced later even if the live data changes.

### Presenter demo: catch a difference
Run `env QC_INTRODUCE_DIFF=1 python exercises/b_ProdAndQC/jobs/run_t_dm1.py`. The QC step plants one wrong number, the comparison reports the changed cell, and the Jobs screen shows the status as Issues. Run the job again without the variable to clear it.

## New Domino Concepts

**Jobs:** A script run in its own container, on hardware you choose, without a workspace open. Each job records its logs, results and the exact code and environment it ran with.

**Job statistics (`dominostats.json`):** A small file a job writes to publish headline numbers on the Jobs screen, so reviewers see the result without opening logs.

**Snapshots and tags:** Point-in-time, read-only copies of a NetApp Volume, with a name and a commit message. Snapshots are near-instant and are how a study freezes its input data.

**Flows:** A workflow that links jobs together, running independent steps in parallel and recording how data moves between them.

*Talk track:* these three steps form a pipeline. Linking jobs together is a Flow. Show the flow graph, and run it only if the group is comfortable with the basics: stats programmers can find flows intimidating.
