"""QC program: independent re-programming of the demographics table (double programming).

Written without looking at the production code. It builds the same table with plain Python
loops and the statistics module instead of pandas group-bys, then writes it to the volume.
Run as a Domino Job:  python exercises/b_ProdAndQC/jobs/qc_t_dm1.py

Presenters can set QC_INTRODUCE_DIFF=1 to plant one wrong number and show the compare job
catching it.
"""
import os
import statistics
import sys

import pandas as pd

sys.path.append(os.environ.get("DOMINO_WORKING_DIR", "."))
from common import paths
from common.adam import load_adsl, round_half_up



def pct(count: int, total: int) -> str:
    return f"{count} ({round_half_up(100.0 * count / total)}%)"


def stats_rows(values: list[float]) -> list[tuple[str, str]]:
    vals = [v for v in values if v == v]  # drop NaN
    return [("n", str(len(vals))),
            ("Mean (SD)", f"{round_half_up(statistics.fmean(vals))} ({round_half_up(statistics.stdev(vals), 2)})"),
            ("Median", round_half_up(statistics.median(vals))),
            ("Min - Max", f"{round_half_up(min(vals), 0)} - {round_half_up(max(vals), 0)}")]


def build_table(adsl: pd.DataFrame) -> pd.DataFrame:
    records = adsl.to_dict("records")
    safety = [r for r in records if r["SAFFL"] == "Y"]
    # Treatment arms in the order of their planned treatment number (TRT01PN), read from the data.
    arm_names = [arm for _, arm in sorted({(r["TRT01PN"], r["ARM"]) for r in safety})]
    columns = {arm: [r for r in safety if r["ARM"] == arm] for arm in arm_names}
    columns["Total"] = safety

    out = [("", "Subjects in population", {c: str(len(rs)) for c, rs in columns.items()})]

    def add_continuous(section, var):
        out.append((section, "", {c: "" for c in columns}))
        per_col = {c: dict(stats_rows([r[var] for r in rs])) for c, rs in columns.items()}
        for label in ["n", "Mean (SD)", "Median", "Min - Max"]:
            out.append((section, label, {c: per_col[c][label] for c in columns}))

    def add_categorical(section, var, ordered, display=None):
        out.append((section, "", {c: "" for c in columns}))
        for level in ordered:
            cells = {c: pct(sum(1 for r in rs if r[var] == level), len(rs)) for c, rs in columns.items()}
            out.append((section, (display or {}).get(level, level), cells))

    add_continuous("Age (years)", "AGE")
    add_categorical("Age group, n (%)", "AGEGR1", ["<65", "65-80", ">80"])
    add_categorical("Sex, n (%)", "SEX", ["F", "M"], {"F": "Female", "M": "Male"})
    add_categorical("Race, n (%)", "RACE", sorted({r["RACE"] for r in safety if isinstance(r["RACE"], str)}))
    add_categorical("Ethnicity, n (%)", "ETHNIC", sorted({r["ETHNIC"] for r in safety if isinstance(r["ETHNIC"], str)}))
    add_continuous("Baseline weight (kg)", "WEIGHTBL")
    add_continuous("Baseline BMI (kg/m2)", "BMIBL")

    return pd.DataFrame([{"Section": s, "Characteristic": c, **v} for s, c, v in out])


def plant_difference(table: pd.DataFrame) -> pd.DataFrame:
    """Presenter demo: change one number when QC_INTRODUCE_DIFF is set."""
    if os.environ.get("QC_INTRODUCE_DIFF"):
        row = table.index[(table["Section"] == "Age (years)") & (table["Characteristic"] == "Median")][0]
        table.loc[row, "Total"] = "99.9"
        print("QC_INTRODUCE_DIFF set: changed Age median (Total) to 99.9")
    return table


def main():
    table = plant_difference(build_table(load_adsl()))
    table.to_csv(paths.QC_DM1, index=False)
    print(f"Wrote {paths.QC_DM1} ({len(table)} rows)")


if __name__ == "__main__":
    main()
