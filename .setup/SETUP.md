# Setup (presenters only)

Do this once, then publish the project as a **project template** so attendees start with the code in place. The data lives on a NetApp Volume, not in the project.

## 1. Compute environment
Use the `Fraud-Detection-Workshop` environment described in `environment.md` (Python 3.12 Domino Standard Environment plus the packages in `Dockerfile`). Attendees need JupyterLab; VS Code is optional.

## 2. NetApp Volume
- [ ] Create a NetApp Volume named exactly `partner-sce-fraud-data` (Data > NetApp Volumes > Create Volume; a few GB is plenty). The name matters because the code looks for `<mount>/partner-sce-fraud-data/`.
- [ ] Put `raw_cc_transactions.csv.gz` at the root of the volume. Mount the volume in a workspace or job and copy the file in.
- [ ] Take a snapshot (for example tag `raw-v1`) so you can restore the starting state between sessions.
- [ ] Give attendees access: grant the volume to each user (or an organization) as Editor, since exercises A and B write files to it. If attendees should not share one live volume, give each their own copy of the starting data instead.

Mount paths: `/domino/netapp-volumes/<name>/` in DFS projects, `/mnt/netapp-volumes/<name>/` in Git-based projects. `common/paths.py` finds whichever exists. Set `FRAUD_DATA_DIR` to override it.

## 3. Project
- [ ] Create a **DFS-backed** project from this repo's contents. DFS is used so attendees do not need Git credentials; say in the session that Git-backed projects are recommended for real work.
- [ ] Attach the `partner-sce-fraud-data` volume to the project (Data > NetApp Volumes > Add Existing Volume).
- [ ] Set the project's default environment and hardware tier.

## 4. Dry run
- [ ] `python .setup/verify_environment.py` prints PASS
- [ ] Exercise A notebook runs and writes `clean_cc_transactions.csv` to the volume
- [ ] Exercise B job succeeds and writes `engineered_cc_transactions.csv` to the volume
- [ ] Exercise C app publishes and the Overview and Review queue tabs load

Then restore the volume to the raw-only snapshot (or delete the generated `clean_` and `engineered_` files) and clear `artifacts/`, so attendees start clean.

## 5. Template and access
- [ ] Publish the project as a project template.
- [ ] Add attendees (about 20) to the shared Domino deployment. The list comes from the partner contact; users are added through Keycloak.
