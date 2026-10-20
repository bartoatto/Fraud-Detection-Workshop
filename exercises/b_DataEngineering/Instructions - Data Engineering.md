# Data Engineering
Prepare the cleaned transactions for review by running a script as a Domino **Job**. The job adds derived columns and a rules-based risk score, writes the result back to the NetApp Volume, and produces an exploratory report.

## Exercise Instructions

1. In the workspace, open `exercises/b_DataEngineering/data_engineering.py` and read through it (do not modify it).
2. Sync your changes, then click **Run Job** (or **Jobs → Run**).
3. For the file name or command, enter `python exercises/b_DataEngineering/data_engineering.py` and start the job.
4. Open **Jobs** in the left-hand column and click the running job. Watch the logs update live.
5. When it finishes, review the outputs:
   - `engineered_cc_transactions.csv` on the NetApp Volume - the data the app reads
   - `artifacts/b_data_engineering/preprocessing_report.html` - the exploratory report

## New Domino Concepts

**Jobs:** A script run in its own container, on hardware you choose, without a workspace open. Each job records its logs, results and the exact code and environment it ran with.

**Results:** Files a job writes to the project are saved with the run, so anyone can look back at what it produced.

*Talk track:* one job is a single building block. Several jobs linked together can become a Flow, which we talk through but do not run.
