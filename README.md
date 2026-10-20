# Domino Platform Workshop - Life Sciences SCE edition

A hands-on session on the Domino platform primitives, using a credit card fraud dataset as the working example. Work through the exercises in order; each one builds on the last.

| # | Folder | What you do |
|---|--------|-------------|
| A | `exercises/a_DataExploration` | Launch a workspace, open a notebook, clean and plot the data |
| B | `exercises/b_DataEngineering` | Run feature engineering as a Domino Job |
| C | `exercises/c_ReviewApp` | Publish the Transaction Review Desk app and record review decisions |

Each folder has an `Instructions` file. The data lives on the NetApp Volume `partner-sce-fraud-data`, which is attached to the project, and shared code is in `common/`. Files the exercises create go to that volume and to `artifacts/`.
