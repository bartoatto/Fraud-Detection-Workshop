"""Statistical helpers for the Study Review Desk. Pure functions on DataFrames, so they can be tested alone."""
import numpy as np
import pandas as pd
from scipy import stats


def compare_continuous(df: pd.DataFrame, var: str, group: str = "ARM") -> dict:
    """Compare a numeric variable across arms: one-way ANOVA, Kruskal-Wallis and the pairwise Welch t-tests."""
    samples = {g: d[var].dropna().to_numpy() for g, d in df.groupby(group, observed=True)}
    samples = {g: s for g, s in samples.items() if len(s) > 1}
    if len(samples) < 2:
        return {}
    arms = list(samples)
    pairs = [{"Comparison": f"{a} vs {b}", "Mean difference": samples[a].mean() - samples[b].mean(),
              "p-value": stats.ttest_ind(samples[a], samples[b], equal_var=False).pvalue}
             for i, a in enumerate(arms) for b in arms[i + 1:]]
    return {"anova_p": stats.f_oneway(*samples.values()).pvalue,
            "kruskal_p": stats.kruskal(*samples.values()).pvalue,
            "pairwise": pd.DataFrame(pairs)}


def compare_categorical(df: pd.DataFrame, var: str, group: str = "ARM") -> dict:
    """Test whether a categorical variable is associated with arm: chi-square, plus Cramer's V as the effect size."""
    table = pd.crosstab(df[group], df[var])
    if table.shape[0] < 2 or table.shape[1] < 2:
        return {}
    chi2, p, _, expected = stats.chi2_contingency(table)
    v = np.sqrt(chi2 / (table.to_numpy().sum() * (min(table.shape) - 1)))
    return {"table": table, "p": p, "cramers_v": v, "low_expected": bool((expected < 5).any())}


def kaplan_meier(time: pd.Series, event: pd.Series) -> pd.DataFrame:
    """Kaplan-Meier survival curve. event is 1 when the event happened and 0 when the subject was censored."""
    d = pd.DataFrame({"t": time.to_numpy(), "e": event.to_numpy()}).dropna().sort_values("t")
    at_risk, surv, rows = len(d), 1.0, [(0.0, 1.0)]
    for t, g in d.groupby("t"):
        events = int(g["e"].sum())
        if events:
            surv *= 1 - events / at_risk
        rows.append((float(t), surv))
        at_risk -= len(g)
    return pd.DataFrame(rows, columns=["time", "survival"])


def logrank_p(df: pd.DataFrame, time: str, event: str, group: str = "ARM") -> float:
    """Log-rank test that the event curves are the same in every arm."""
    d = df[[time, event, group]].dropna()
    groups = sorted(d[group].unique())
    times = np.sort(d.loc[d[event] == 1, time].unique())
    obs_minus_exp, var = np.zeros(len(groups)), np.zeros((len(groups), len(groups)))
    for t in times:
        at_risk = np.array([(d.loc[d[group] == g, time] >= t).sum() for g in groups], float)
        events = np.array([((d[group] == g) & (d[time] == t) & (d[event] == 1)).sum() for g in groups], float)
        n, e = at_risk.sum(), events.sum()
        obs_minus_exp += events - e * at_risk / n
        if n > 1:
            w = e * (n - e) / (n - 1) / n
            var += w * (np.diag(at_risk) - np.outer(at_risk, at_risk) / n)
    stat = obs_minus_exp[:-1] @ np.linalg.solve(var[:-1, :-1], obs_minus_exp[:-1])
    return float(stats.chi2.sf(stat, len(groups) - 1))


def fmt_p(p: float) -> str:
    return "<0.001" if p < 0.001 else f"{p:.3f}"
