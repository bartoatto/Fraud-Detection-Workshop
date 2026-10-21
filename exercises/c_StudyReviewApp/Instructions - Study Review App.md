# Publish the Study Review Desk
Publish an interactive dashboard on the study data. Filter the population by arm, sex, age and site, explore demographics, disposition and exposure, see time to discontinuation as a Kaplan-Meier plot, and run statistical tests (ANOVA, Kruskal-Wallis, chi-square, log-rank, correlation) without writing code. The last tab shows Table 14.1 from Exercise B with its QC status.

The app reads everything from the NetApp Volume, so there is nothing to configure. The statistics are in `common/stats.py` if you want to add your own.

## Exercise Instructions

1. Make sure the Exercise B job has finished.
2. Optional check in the workspace terminal: `PORT=8501 bash exercises/c_StudyReviewApp/app.sh`, then open the proxied port.
3. Go to **Deployments → Apps → Publish** (or **Publish App**).
4. Choose the project files, pick `exercises/c_StudyReviewApp/app.sh` as the entry point, give the app a name and publish it.
5. Open the app and try each tab:
   - **Overview** - KPIs, enrolment by arm and site, cumulative randomisation
   - **Demographics** - pick a variable and a plot type; arm summaries
   - **Disposition & exposure** - why subjects stopped, treatment duration, dose, and a data query on COMPLFL
   - **Time to discontinuation** - Kaplan-Meier curves with a log-rank test
   - **Statistical tests** - choose a variable and get the right test; correlation heatmap
   - **Table 14.1 & data** - the production table with QC status, the filtered data, CSV download
6. Change the sidebar filters and watch every tab update.

## New Domino Concepts

**Apps:** A web app (Streamlit, Dash, Flask and others) published from project files, with Domino handling hosting, access control and the URL. Reviewers get a tool without needing the code.

**Talk track - one app, many users:** the same published URL serves every reviewer, with Domino handling access control. Statistics run in the app's container, on the environment you chose, so the numbers are reproducible.
