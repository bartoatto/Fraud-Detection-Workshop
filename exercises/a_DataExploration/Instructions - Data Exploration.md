# Data Exploration
Explore a table of credit card transactions the way a stats programmer would before building anything on it: load it, clean it, look at it, and save the clean version. The raw file is already on the project's NetApp Volume, so there is nothing to upload.

## Exercise Instructions

1. Click **Workspaces** (left-hand column) and launch **JupyterLab**.
   - Walk through the launch dialog: environment, hardware tier, and the IDE choice.
2. Open `exercises/a_DataExploration/data_exploration_notebook.ipynb`.
3. Run the cells top to bottom.
4. Look at the summary tables and the plots.
5. Open `artifacts/a_data_exploration/` to see the saved plots, and confirm `clean_cc_transactions.csv` now sits beside the raw file on the NetApp Volume (`/domino/netapp-volumes/partner-sce-fraud-data/`, or `/mnt/netapp-volumes/...` in a Git-based project).
6. Sync your changes (commit them, if the project is Git-backed).

## New Domino Concepts

**Workspaces:** An interactive session in the IDE of your choice (JupyterLab, VS Code, RStudio and others) running on the environment and hardware you pick.

**Compute Environments:** A container image holding the tools, languages and packages a project needs, so everyone gets the same setup.

**Hardware Tiers:** Preset CPU, GPU and memory sizes you choose per workspace or job.

**NetApp Volumes:** Shared, snapshot-able storage mounted into workspaces, jobs and apps. The data stays on the volume, separate from the code, and the volume can be shared across projects.
