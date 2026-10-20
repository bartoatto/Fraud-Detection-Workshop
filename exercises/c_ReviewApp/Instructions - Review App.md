# Publish the Transaction Review Desk
Publish a small web app on top of the data from Exercise B. It ranks transactions with a simple, readable risk score, lets a reviewer approve, reject or escalate the riskiest ones, and logs each decision with the reviewer and a timestamp.

The app reads its data from the same NetApp Volume as the earlier exercises, so there is nothing to configure.

## Exercise Instructions

1. Make sure Exercise B has finished, so `engineered_cc_transactions.csv` is on the NetApp Volume.
2. Optional check in the workspace terminal: `PORT=8501 bash exercises/c_ReviewApp/app.sh`, then open the proxied port.
3. Go to **Deployments → Apps → Publish** (or **Publish App**).
4. Choose the project files, pick `exercises/c_ReviewApp/app.sh` as the entry point, give the app a name and publish it.
5. Open the app and try each tab:
   - **Overview** - how many transactions trip each risk rule, and whether the score lines up with known outcomes
   - **Review queue** - pick a decision for a few rows and click **Save decisions**
6. Open `artifacts/review_decisions.csv` (from the workspace) to see the audit trail.

## New Domino Concepts

**Apps:** A web app (Streamlit, Dash, Flask and others) published from project files, with Domino handling hosting, access control and the URL. Business users get a tool without needing the code.

**Talk track - app gates:** teams usually build in an exploratory project and need IT or Quality sign-off before an app is production ready. Governance can require an approval gate before an app is published.
