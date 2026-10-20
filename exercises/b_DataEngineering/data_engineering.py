"""Data engineering job.

Reads the cleaned transactions from Exercise A, adds derived features and a rules-based
risk score, and writes the result back to the NetApp Volume for the review app.
Run it as a Domino Job:  python exercises/b_DataEngineering/data_engineering.py
"""
import os
import sys

import pandas as pd

sys.path.append(os.environ.get("DOMINO_WORKING_DIR", "."))
from common import paths
from common.features import add_derived_features, add_risk_flags


def run() -> pd.DataFrame:
    if paths.CLEAN_FILE.exists():
        print(f"Loading clean dataset from {paths.CLEAN_FILE}")
        clean_df = pd.read_csv(paths.CLEAN_FILE, index_col=0)
    else:  # Exercise A not run: redo its cleaning step.
        print(f"{paths.CLEAN_FILE.name} not found - cleaning {paths.RAW_FILE.name}")
        clean_df = pd.read_csv(paths.RAW_FILE).dropna()
    print(f"Loaded {len(clean_df):,} rows")

    engineered = add_risk_flags(add_derived_features(clean_df))
    engineered.to_csv(paths.ENGINEERED_FILE)
    print(f"Saved {len(engineered):,} rows to {paths.ENGINEERED_FILE}")

    try:
        from ydata_profiling import ProfileReport  # slow import, optional
        report = paths.artifact_dir("b_data_engineering") / "preprocessing_report.html"
        ProfileReport(clean_df, title="Credit Card Transactions - EDA Report", explorative=True, minimal=True).to_file(report)
        print(f"Saved {report}")
    except ImportError:
        print("ydata-profiling not installed - skipping the EDA report.")
    return engineered


if __name__ == "__main__":
    run()
