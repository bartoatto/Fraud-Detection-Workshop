# SAS version of the exercises

The same three exercises as `exercises/`, written in SAS for statistical programmers. Use these when attendees are SAS-first. They use the same study data on the same NetApp Volume, and write the same output files, so the review app in `exercises/c_StudyReviewApp` works with either version.

| # | Folder | What you do |
|---|--------|-------------|
| A | `a_ExploreADSL` | Explore ADSL in SAS Studio: contents, frequencies, data checks, plots |
| B | `b_ProdAndQC` | Run the production, QC and compare programs for Table 14.1 as Domino Jobs |
| C | `c_StudyReviewApp` | Publish the (Python) Study Review Desk and sign off the table |

`setup/domino_setup.sas` is shared by every program. It finds the NetApp Volume, creates the `ADAM`, `TFL` and `TFLQC` libraries, and defines a macro that publishes results to the Jobs screen.

## Requirements

- A compute environment with SAS, for example **SAS Analytics Pro**, with the SAS Studio IDE. The Python environment used for the other exercises does not include SAS.
- A SAS licence that is valid on the day (the SAS environment checked while this was written had an expired licence).
- The same NetApp Volume as the Python exercises (see `.setup/SETUP.md`).

## Status

These programs were written to follow the Python versions and Domino's reference SAS conventions, but **they have not been run**: no valid SAS licence was available when they were written. Run them once in your SAS environment before the session and fix anything the log reports. Typical things to check: the volume path, the `%sysget` warnings for unset environment variables (harmless), and that the CSV layout matches `tfl/t_dm1.csv` from the Python version.
