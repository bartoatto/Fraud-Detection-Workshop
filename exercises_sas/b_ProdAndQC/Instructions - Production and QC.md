# Production, QC and Compare (SAS)
Clinical outputs are programmed twice: a **production** programmer builds the table, and a **QC** programmer rebuilds it independently without looking at the first. A third program compares the two. You will run all three as Domino **Jobs**.

The table is Table 14.1, a summary of demographic and baseline characteristics for the safety population, by treatment arm. Every program reads ADSL from, and writes its results back to, the NetApp Volume.

## Exercise Instructions

1. Open `prod_t_dm1.sas` and `qc_t_dm1.sas` and skim them. They build the same table with different procedures: production uses PROC MEANS and PROC SQL, QC uses PROC SQL, PROC UNIVARIATE and PROC FREQ. Do not modify them.
2. Sync your changes, then start each job with **Run Job**, one after the other. In a SAS environment Domino runs `.sas` files directly:
   - `exercises_sas/b_ProdAndQC/prod_t_dm1.sas`
   - `exercises_sas/b_ProdAndQC/qc_t_dm1.sas`
   - `exercises_sas/b_ProdAndQC/compare_t_dm1.sas`
3. Open **Jobs** and click the compare job. Watch the log, and note the **Status**, **Cells compared** and **Cell differences** values on the Jobs screen.
4. On the NetApp Volume, find the outputs:
   - `tfl/t_dm1.csv`, `tfl/t_dm1.html` and `tfl/t_dm1.sas7bdat` - the production table
   - `qc/tfl/qc_t_dm1.csv` and `qc_t_dm1.sas7bdat` - the QC table
   - `compare/t_dm1_summary.json` - the comparison result
   - `artifacts/b_prod_and_qc/t_dm1_compare.pdf` - the PROC COMPARE report

### Optional: reproducible runs with a snapshot tag
A snapshot tag freezes the input. Run the production job again with the environment variable `ADSL_SNAPSHOT_TAG` set to `adsl-v1` (in the job's environment variables, or as a command prefix `env ADSL_SNAPSHOT_TAG=adsl-v1 sas ...`). It then reads ADSL from the `adsl-v1` snapshot, not the live files.

### Presenter demo: catch a difference
Run the QC job with `QC_INTRODUCE_DIFF=1` set, then run the compare job again. It reports the changed cell, and the Jobs screen shows the status as Issues. Run the QC job again without the variable to clear it.

## New Domino Concepts

**Jobs:** A program run in its own container, on hardware you choose, without a workspace open. Each job records its log, results and the exact code and environment it ran with.

**Job statistics (`dominostats.json`):** A small file a job writes to publish headline numbers on the Jobs screen, so reviewers see the result without opening logs.

**Snapshots and tags:** Point-in-time, read-only copies of a NetApp Volume, with a name and a commit message. Snapshots are near-instant and are how a study freezes its input data.

*Talk track:* these three jobs form a pipeline. Linking jobs together is a Flow; we show what one looks like but do not run one.
