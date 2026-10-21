# Setup (presenters only)

Do this once, then publish the project as a **project template** so attendees start with the code in place. The study data lives on a NetApp Volume, not in the project.

## 1. Compute environment
Use the `Fraud-Detection-Workshop` environment described in `environment.md` (Python 3.12 Domino Standard Environment plus the packages in `Dockerfile`). Attendees need JupyterLab; VS Code is optional. Python only; reading the SAS dataset needs nothing beyond pandas.

## 2. NetApp Volume
- [ ] Create a NetApp Volume named exactly `cdisc01-study-data` (Data > NetApp Volumes > Create Volume; a couple of GB is plenty). The code looks for `<mount>/cdisc01-study-data/`.
- [ ] Create a folder `adam/` at the root and put `adsl.sas7bdat` in it. Mount the volume in a workspace or job and copy the file in.
- [ ] Take a snapshot with the tag `adsl-v1` (and a commit message). Exercise B's snapshot-tag step and the flow both read from that tag, so the name matters. A flow needs this snapshot to exist before it runs.
- [ ] Give attendees access. Exercise B writes `tfl/`, `qc/tfl/` and `compare/`, and the app writes `signoff/`, so attendees need Editor access. A shared live volume means everyone writes the same files, which is fine because every run produces the same output; use a separate copy per attendee if you want them isolated.

Mount paths: `/domino/netapp-volumes/<name>/` in DFS projects, `/mnt/netapp-volumes/<name>/` in Git-based projects. `common/paths.py` finds whichever exists.

## 3. Project
- [ ] Create a **DFS-backed** project from this repo's contents. DFS avoids Git credentials during a short session; say in the session that Git-backed projects are recommended for real work.
- [ ] Attach `cdisc01-study-data` to the project (Data > NetApp Volumes > Add Existing Volume).
- [ ] Set the project's default environment and hardware tier.

## 4. Dry run
- [ ] `python .setup/verify_environment.py` prints PASS
- [ ] Exercise A notebook runs top to bottom
- [ ] Exercise B: the single job (`jobs/run_t_dm1.py`) succeeds and its status shows Clean on the Jobs screen
- [ ] Exercise B optional: `jobs/launch_job.py` starts the job, and the flow (`flow/workflow.py`) runs and shows status Clean
- [ ] Exercise C: the app publishes, the tabs load, and an approval is recorded

Then restore the volume to its starting state by deleting `tfl/`, `qc/`, `compare/` and `signoff/`, and clear `artifacts/`.

## 4b. SAS version (optional)
- [ ] Use a SAS Analytics Pro environment with SAS Studio for the `exercises_sas/` programs, and check its SAS licence is valid.
- [ ] Run `exercises_sas/a_ExploreADSL/explore_adsl.sas` and `b_ProdAndQC/run_t_dm1.sas` once, and fix anything the log reports. They have not been run yet.
- [ ] Check the job's status on the Jobs screen, and that the app shows the SAS results.

## 5. Template and access
- [ ] Publish the project as a project template.
- [ ] Add attendees (about 20) to the shared Domino deployment. The list comes from the partner contact; users are added through Keycloak.

## Notes
- The jobs write `dominostats.json` so the Jobs screen shows the comparison result. Git-based projects read it from `artifacts/`; DFS projects read it from the project root. The code picks the right place from `DOMINO_IS_GIT_BASED`, but check on a DFS project that the values appear on the Jobs screen.
- `reference/` is not part of the template. See `AGENDA.md` for how this workshop relates to a full SCE study repository.
