# Explore ADSL
Open the study's subject-level dataset the way a stats programmer would before building any table: load it, check it, and look at who is in each treatment arm. The data is the CDISC pilot study (CDISCPILOT01) and sits on the project's NetApp Volume, so there is nothing to upload.

## Exercise Instructions

1. Click **Workspaces** (left-hand column) and launch **JupyterLab**.
   - Walk through the launch dialog: environment, hardware tier, and the IDE choice.
2. In the file browser, open `exercises/a_ExploreADSL/explore_adsl.ipynb`.
3. Run the cells top to bottom.
4. Read the data checks. One of them points to a question worth asking the study team.
5. Open `artifacts/a_explore_adsl/` to see the saved plots.
6. Sync your changes.

## New Domino Concepts

**Workspaces:** An interactive session in the IDE of your choice (JupyterLab, VS Code, SAS and others) running on the environment and hardware you pick.

**Compute Environments:** A container image holding the languages and packages a project needs, so everyone starts from the same setup.

**Hardware Tiers:** Preset CPU and memory sizes you choose per workspace or job.

**NetApp Volumes:** Shared storage mounted into workspaces, jobs and apps. The study data stays on the volume, separate from the code.
