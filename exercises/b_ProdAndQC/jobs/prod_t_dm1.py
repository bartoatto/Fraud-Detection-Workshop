"""Production program: Demographics table - Summary of Demographic and Baseline Characteristics.

Safety population, by treatment arm. Reads ADSL from the NetApp Volume and writes the table
(CSV and HTML) back to tfl/ on the same volume.
Run as a Domino Job:  python exercises/b_ProdAndQC/jobs/prod_t_dm1.py
"""
import os
import sys

import pandas as pd

sys.path.append(os.environ.get("DOMINO_WORKING_DIR", "."))
from common import paths
from common.adam import load_adsl, round_half_up

TITLE = "Demographics table: Summary of Demographic and Baseline Characteristics - Safety Population"
FOOTNOTE = "Percentages use the number of subjects in each arm as the denominator. Source: ADSL."

AGE_GROUPS = ["<65", "65-80", ">80"]
SEX = {"F": "Female", "M": "Male"}


def n_pct(series: pd.Series, value, denom: int) -> str:
    n = int((series == value).sum())
    return f"{n} ({round_half_up(100 * n / denom)}%)"


def continuous(series: pd.Series) -> dict:
    s = series.dropna()
    return {
        "n": str(len(s)),
        "Mean (SD)": f"{round_half_up(s.mean())} ({round_half_up(s.std(ddof=1), 2)})",
        "Median": round_half_up(s.median()),
        "Min - Max": f"{round_half_up(s.min(), 0)} - {round_half_up(s.max(), 0)}",
    }


def build_table(adsl: pd.DataFrame) -> pd.DataFrame:
    pop = adsl[adsl["SAFFL"] == "Y"]
    # Treatment arms in the order of their planned treatment number (TRT01PN), read from the data.
    arms = pop[["TRT01PN", "ARM"]].drop_duplicates().sort_values("TRT01PN")["ARM"].tolist()
    groups = {arm: pop[pop["ARM"] == arm] for arm in arms}
    groups["Total"] = pop
    races = sorted(pop["RACE"].dropna().unique())
    ethnicities = sorted(pop["ETHNIC"].dropna().unique())

    rows = [("", "Subjects in population", {g: f"{len(d)}" for g, d in groups.items()})]

    def section(name, make_stats):
        rows.append((name, "", {g: "" for g in groups}))
        for label in make_stats(None).keys():
            rows.append((name, label, {g: make_stats(d)[label] for g, d in groups.items()}))

    def cont(col):
        return lambda d: continuous(d[col] if d is not None else pd.Series([0.0, 1.0]))

    def cat(col, values, names=None):
        def f(d):
            if d is None:
                return {(names or {}).get(v, v): None for v in values}
            return {(names or {}).get(v, v): n_pct(d[col], v, len(d)) for v in values}
        return f

    section("Age (years)", cont("AGE"))
    section("Age group, n (%)", cat("AGEGR1", AGE_GROUPS))
    section("Sex, n (%)", cat("SEX", list(SEX), SEX))
    section("Race, n (%)", cat("RACE", races))
    section("Ethnicity, n (%)", cat("ETHNIC", ethnicities))
    section("Baseline weight (kg)", cont("WEIGHTBL"))
    section("Baseline BMI (kg/m2)", cont("BMIBL"))

    return pd.DataFrame([{"Section": s, "Characteristic": c, **v} for s, c, v in rows])


def to_html(table: pd.DataFrame) -> str:
    return (f"<html><body style='font-family:Courier New,monospace;font-size:12px'>"
            f"<h3>{TITLE}</h3>{table.to_html(index=False, border=0)}<p>{FOOTNOTE}</p></body></html>")


def main():
    adsl = load_adsl()
    print(f"Read {len(adsl)} subjects from {paths.ADSL_FILE}")
    table = build_table(adsl)
    paths.ensure(paths.PROD_DIR)
    table.to_csv(paths.PROD_DM1, index=False)
    paths.PROD_DM1_HTML.write_text(to_html(table))
    print(f"Wrote {paths.PROD_DM1} ({len(table)} rows)")


if __name__ == "__main__":
    main()
