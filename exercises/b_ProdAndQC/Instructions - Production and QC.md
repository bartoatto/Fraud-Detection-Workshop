# Production, QC and Compare
Clinical outputs are programmed twice: a **production** programmer builds the table, and a **QC** programmer rebuilds it independently without looking at the first. A third step compares the two. You will run all three as Domino **Jobs**.

The table is Table 14.1, a summary of demographic and baseline characteristics for the safety population, by treatment arm. Every program reads ADSL from, and writes its results back to, the NetApp Volume.

## Exercise Instructions

1. Open `prod_t_dm1.py` and `qc_t_dm1.py` in the workspace and skim them. They compute the same table in different ways. Do not modify them.
2. Sync your changes, then start each job with **Run Job**, one after the other:
   - `python exercises/b_ProdAndQC/prod_t_dm1.py`
   - `python exercises/b_ProdAndQC/qc_t_dm1.py`
   - `python exercises/b_ProdAndQC/compare_t_dm1.py`
3. Open **Jobs** and click the compare job. Watch the logs, and note the **Status**, **Cells compared** and **Cell differences** values that appear on the Jobs screen.
4. On the NetApp Volume, find the outputs:
   - `tfl/t_dm1.csv` and `tfl/t_dm1.html` - the production table
   - `qc/tfl/qc_t_dm1.csv` - the QC table
   - `compare/t_dm1_summary.json` - the comparison result

### Optional: reproducible runs with a snapshot tag
A snapshot tag freezes the input. Run the production job again, with the command:

`env ADSL_SNAPSHOT_TAG=adsl-v1 python exercises/b_ProdAndQC/prod_t_dm1.py`

(`env` sets the variable for that one command.) It now reads ADSL from the `adsl-v1` snapshot of the volume, not the live files, so the result can be reproduced later even if the live data changes.

### Presenter demo: catch a difference
Run the QC job as `env QC_INTRODUCE_DIFF=1 python exercises/b_ProdAndQC/qc_t_dm1.py`, then run the compare job again. It reports the changed cell, and the Jobs screen shows the status as Issues. Re-run the QC job without the variable to clear it.

## New Domino Concepts

**Jobs:** A script run in its own container, on hardware you choose, without a workspace open. Each job records its logs, results and the exact code and environment it ran with.

**Job statistics (`dominostats.json`):** A small file a job writes to publish headline numbers on the Jobs screen, so reviewers see the result without opening logs.

**Snapshots and tags:** Point-in-time, read-only copies of a NetApp Volume, with a name and a commit message. Snapshots are near-instant and are how a study freezes its input data.

*Talk track:* these three jobs form a pipeline. Linking jobs together is a Flow; we show what one looks like but do not run one.
