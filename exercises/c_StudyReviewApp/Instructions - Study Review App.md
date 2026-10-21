# Publish the Study Review Desk
Publish a small web app on top of the study data and the outputs from Exercise B. It shows the study at a glance, displays Table 14.1 with its QC status, and lets a reviewer sign off the table.

Sign-off is **gated**: a table can only be approved when the production and QC versions match. Every decision is logged with the reviewer and a timestamp. The app reads everything from the NetApp Volume, so there is nothing to configure.

## Exercise Instructions

1. Make sure the Exercise B job has finished.
2. Optional check in the workspace terminal: `PORT=8501 bash exercises/c_StudyReviewApp/app.sh`, then open the proxied port.
3. Go to **Deployments → Apps → Publish** (or **Publish App**).
4. Choose the project files, pick `exercises/c_StudyReviewApp/app.sh` as the entry point, give the app a name and publish it.
5. Open the app and try each tab:
   - **Study overview** - subjects, sites and arms
   - **Table 14.1** - the production table and its QC status
   - **Sign-off** - record a decision on Table 14.1
6. Find `signoff/signoff_log.csv` on the NetApp Volume to see the audit trail.

## New Domino Concepts

**Apps:** A web app (Streamlit, Dash, Flask and others) published from project files, with Domino handling hosting, access control and the URL. Reviewers get a tool without needing the code.

**Talk track - gates:** teams usually build in an exploratory project and need IT or Quality sign-off before something is production ready. The sign-off gate here is the same idea in miniature; Domino governance policies add formal approval steps around it.
