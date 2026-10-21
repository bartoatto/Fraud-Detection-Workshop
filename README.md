# Domino Platform Workshop - Life Sciences (SCE) edition

A hands-on session on the Domino platform primitives, using a real clinical trial dataset: the public CDISC pilot study (CDISCPILOT01). You will explore the study's subject-level data, produce a table with production and QC programs, and publish an app for reviewers.

| # | Folder | What you do |
|---|--------|-------------|
| A | `exercises/a_ExploreADSL` | Launch a workspace and explore the ADSL dataset |
| B | `exercises/b_ProdAndQC` | Run production, QC and compare programs as Domino Jobs |
| C | `exercises/c_StudyReviewApp` | Publish the Study Review Desk and record a sign-off |

Each folder has an `Instructions` file. Work through the exercises in order.

The data lives on the NetApp Volume `cdisc01-study-data`, which is attached to the project, and shared code is in `common/`. Programs write their results back to the volume.
