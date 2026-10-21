# Setup (presenters only)

Do this once, then publish the project as a **project template** so attendees start with the code in place. The study data lives on a NetApp Volume, not in the project.

## 1. Compute environment
Use the `Fraud-Detection-Workshop` environment described in `environment.md` (Python 3.12 Domino Standard Environment plus the packages in `Dockerfile`). The exercises need only pandas, matplotlib, seaborn and streamlit. Attendees need JupyterLab.

## 2. NetApp Volume
- [ ] Create a NetApp Volume named exactly `cdisc01-study-data` (Data > NetApp Volumes > Create Volume; 1 GB is plenty). The code looks for `<mount>/cdisc01-study-data/`.
- [ ] Create a folder `adam` at the root of the volume and put `adsl.sas7bdat` in it. Mount the volume in a workspace or job and copy the file in.
- [ ] Take a snapshot and tag it `adsl-v1` (used by the optional reproducibility step in Exercise B).
- [ ] Give attendees access. Exercises B and C write files to the volume, so attendees need the Editor role. If they should not share one live volume, give each their own copy.

Mount paths: `/domino/netapp-volumes/<name>/` in DFS projects, `/mnt/netapp-volumes/<name>/` in Git-based projects. `common/paths.py` finds whichever exists. Set `STUDY_DATA_DIR` to read from another folder.

## 3. Project
- [ ] Create a **DFS-backed** project from this repo's contents. DFS is used so attendees do not need Git credentials; say in the session that Git-backed projects are recommended for real work.
- [ ] Attach the `cdisc01-study-data` volume to the project (Data > NetApp Volumes > Add Existing Volume).
- [ ] Set the project's default environment and hardware tier.

## 4. Dry run
- [ ] `python .setup/verify_environment.py` prints PASS
- [ ] Exercise A notebook runs top to bottom
- [ ] Exercise B: production, QC and compare jobs succeed, and the compare job shows its statistics on the Jobs screen
- [ ] Exercise C app publishes, all four tabs load, and the sign-off form records an approval

Then delete everything the exercises created on the volume (`tfl/`, `qc/`, `compare/`, `signoff/`) and clear `artifacts/`, so attendees start clean.

## 5. Template and access
- [ ] Publish the project as a project template.
- [ ] Add attendees (about 20) to the shared Domino deployment. The list comes from the partner contact; users are added through Keycloak.
