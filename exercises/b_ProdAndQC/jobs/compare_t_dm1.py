"""Compare the production and QC versions of the demographics table cell by cell.

Writes the differences and a summary to the NetApp Volume, and publishes the
headline numbers to dominostats.json so they show on the Jobs screen.
Run as a Domino Job:  python exercises/b_ProdAndQC/jobs/compare_t_dm1.py
"""
import json
import os
import sys

import pandas as pd

sys.path.append(os.environ.get("DOMINO_WORKING_DIR", "."))
from common import paths

KEY = ["Section", "Characteristic"]


def compare(prod: pd.DataFrame, qc: pd.DataFrame):
    """Compare two tables cell by cell. Returns (summary, differences)."""
    prod, qc = prod.set_index(KEY), qc.set_index(KEY)
    missing_in_qc = prod.index.difference(qc.index)
    missing_in_prod = qc.index.difference(prod.index)
    both = prod.index.intersection(qc.index)

    diffs = []
    for key in both:
        for col in prod.columns:
            if prod.loc[key, col] != qc.loc[key, col]:
                diffs.append({"Section": key[0], "Characteristic": key[1], "Column": col,
                              "Production": prod.loc[key, col], "QC": qc.loc[key, col]})
    cells = len(both) * len(prod.columns)
    status = "Clean" if not diffs and missing_in_qc.empty and missing_in_prod.empty else "Issues"
    summary = {"table": "t_dm1", "status": status, "rows_compared": len(both), "cells_compared": cells,
               "cell_differences": len(diffs), "rows_only_in_production": len(missing_in_qc),
               "rows_only_in_qc": len(missing_in_prod)}
    return summary, pd.DataFrame(diffs, columns=["Section", "Characteristic", "Column", "Production", "QC"])


def publish(summary: dict) -> None:
    """Show the headline numbers on the Domino Jobs screen."""
    paths.write_dominostats({"Table": "t_dm1", "Status": summary["status"], "Cells compared": summary["cells_compared"],
                             "Cell differences": summary["cell_differences"]})


def main():
    for f in (paths.PROD_DM1, paths.QC_DM1):
        if not f.exists():
            raise SystemExit(f"{f} not found - run the production and QC programs first.")

    prod = pd.read_csv(paths.PROD_DM1, dtype=str, keep_default_na=False)
    qc = pd.read_csv(paths.QC_DM1, dtype=str, keep_default_na=False)
    summary, diffs = compare(prod, qc)

    diffs.to_csv(paths.COMPARE_DM1, index=False)
    paths.COMPARE_SUMMARY.write_text(json.dumps(summary, indent=2))
    publish(summary)

    print(json.dumps(summary, indent=2))
    for d in diffs.to_dict("records"):
        print(f"DIFF {d['Section']} / {d['Characteristic']} / {d['Column']}: prod={d['Production']} qc={d['QC']}")


if __name__ == "__main__":
    main()
