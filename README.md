# Domino Platform Workshop - Life Sciences edition

A hands-on session on the Domino platform primitives, using the CDISC pilot study (CDISCPILOT01) as the working example. You work the way a statistical programming team does: explore the subject-level data, program a table twice (production and QC), compare the two, and publish a review app. Work through the exercises in order.

| # | Folder | What you do |
|---|--------|-------------|
| A | `exercises/a_ExploreADSL` | Launch a workspace, open a notebook, explore the ADSL dataset |
| B | `exercises/b_ProdAndQC` | Run the production, QC and compare programs for Table 14.1 as Domino Jobs |
| C | `exercises/c_StudyReviewApp` | Publish the Study Review Desk app and sign off the table |

Each folder has an `Instructions` file. `exercises_sas/` has the same exercises written in SAS (see its README). The study data lives on the NetApp Volume `cdisc01-study-data`, which is attached to the project, and shared code is in `common/`. The programs write their results back to that volume.
