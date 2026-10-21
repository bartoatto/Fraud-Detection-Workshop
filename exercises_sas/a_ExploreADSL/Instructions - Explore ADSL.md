# Explore ADSL (SAS)
Open the study's subject-level dataset the way a programmer would before building any table. The data is the CDISC pilot study (CDISCPILOT01) on the project's NetApp Volume, so there is nothing to upload.

## Exercise Instructions

1. Click **Workspaces** and launch **SAS Studio** (SAS Analytics Pro environment).
   - Walk through the launch dialog: environment, hardware tier, and the IDE choice.
2. Open `exercises_sas/a_ExploreADSL/explore_adsl.sas`.
3. Run the program (**Run**, or F3).
4. Read the log. The data checks print `OK` or `FAIL`, and one note points to a question worth asking the study team.
5. Look at the tables in the Results tab, and at the plots saved under `artifacts/a_explore_adsl/`.

## New Domino Concepts

**Workspaces:** An interactive session in the IDE of your choice (SAS Studio, JupyterLab, VS Code and others) running on the environment and hardware you pick.

**Compute Environments:** A container image holding the software a project needs, for example SAS. Everyone starts from the same setup.

**NetApp Volumes:** Shared storage mounted into workspaces, jobs and apps. The study data stays on the volume, separate from the code.
