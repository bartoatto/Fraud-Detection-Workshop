"""Study Review Desk - an interactive dashboard on the CDISC pilot study (CDISCPILOT01).

Reads ADSL from the NetApp Volume. The sidebar filters drive every tab: overview KPIs,
demographics, disposition and exposure, time to discontinuation (Kaplan-Meier + log-rank),
a statistical test workbench, and the Table 14.1 production/QC results from Exercise B.
Published as a Domino App through app.sh.
"""
import json
import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.append(os.environ.get("DOMINO_WORKING_DIR", os.path.abspath("../..")))
from common import paths, stats
from common.adam import load_adsl

st.set_page_config(page_title="Study Review Desk", page_icon="🧪", layout="wide")

ARM_ORDER = ["Placebo", "Xanomeline Low Dose", "Xanomeline High Dose"]
ARM_COLORS = {"Placebo": "#8C8C99", "Xanomeline Low Dose": "#7B6CE6", "Xanomeline High Dose": "#543FDD"}
CONTINUOUS = {"Age (years)": "AGE", "Baseline weight (kg)": "WEIGHTBL", "Baseline BMI (kg/m2)": "BMIBL",
              "Treatment duration (days)": "TRTDURD", "Average daily dose (mg)": "AVGDD",
              "Years of education": "EDLEVEL", "Disease duration (months)": "DURDISM", "Baseline severity (BLDSEV)": "BLDSEV"}
CATEGORICAL = {"Sex": "SEX", "Race": "RACE", "Ethnicity": "ETHNIC", "Age group": "AGEGR1", "BMI group": "BMIGR1",
               "Study status": "EOSSTT", "Discontinuation reason": "DCSREAS"}


@st.cache_data
def adsl_data() -> pd.DataFrame:
    df = load_adsl()
    df["DISCONTINUED"] = (df["EOSSTT"] == "DISCONTINUED").astype(int)
    df["DCSREAS"] = df["DCSREAS"].fillna("COMPLETED")
    df["ARM"] = pd.Categorical(df["ARM"], [a for a in ARM_ORDER if a in set(df["ARM"])], ordered=True)
    return df


def style(fig, height=380):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=40, b=10), legend_title_text="", plot_bgcolor="white",
                      font=dict(color="#2E2E38"), colorway=list(ARM_COLORS.values()))
    fig.update_yaxes(gridcolor="#EAEAF0", zeroline=False)
    fig.update_xaxes(showgrid=False)
    return fig


def p_badge(p: float) -> str:
    text = "p < 0.001" if p < 0.001 else f"p = {p:.3f}"
    return f"{text} - {'significant' if p < 0.05 else 'not significant'} at the 5% level"


if not paths.ADSL_FILE.exists():
    st.error(f"ADSL not found at {paths.ADSL_FILE}. Check that the NetApp Volume is attached to the project.")
    st.stop()

full = adsl_data()

# ---- Sidebar filters -------------------------------------------------------------------------
st.sidebar.header("Filters")
population = st.sidebar.radio("Population", ["Safety (SAFFL)", "Intent-to-treat (ITTFL)", "Efficacy (EFFFL)", "All subjects"])
flag = {"Safety (SAFFL)": "SAFFL", "Intent-to-treat (ITTFL)": "ITTFL", "Efficacy (EFFFL)": "EFFFL"}.get(population)
df = full if flag is None else full[full[flag] == "Y"]
arms = st.sidebar.multiselect("Treatment arms", list(full["ARM"].cat.categories), default=list(full["ARM"].cat.categories))
sexes = st.sidebar.multiselect("Sex", sorted(full["SEX"].unique()), default=sorted(full["SEX"].unique()))
age_lo, age_hi = st.sidebar.slider("Age", int(full["AGE"].min()), int(full["AGE"].max()),
                                   (int(full["AGE"].min()), int(full["AGE"].max())))
sites = st.sidebar.multiselect("Sites (all if empty)", sorted(full["SITEID"].unique()))
df = df[df["ARM"].isin(arms) & df["SEX"].isin(sexes) & df["AGE"].between(age_lo, age_hi)]
if sites:
    df = df[df["SITEID"].isin(sites)]
df = df.assign(ARM=df["ARM"].cat.remove_unused_categories())
st.sidebar.caption(f"{len(df)} of {len(full)} subjects selected")

st.title("🧪 Study Review Desk")
st.caption(f"Protocol {full['STUDYID'].iloc[0]} - {population} population")
if df.empty:
    st.warning("No subjects match the filters.")
    st.stop()

tab_over, tab_demo, tab_disp, tab_surv, tab_tests, tab_table = st.tabs(
    ["Overview", "Demographics", "Disposition & exposure", "Time to discontinuation", "Statistical tests", "Table 14.1 & data"])

# ---- Overview ---------------------------------------------------------------------------------
with tab_over:
    k = st.columns(5)
    k[0].metric("Subjects", len(df))
    k[1].metric("Sites", df["SITEID"].nunique())
    k[2].metric("Median age", f"{df['AGE'].median():.0f}")
    k[3].metric("Completed the study", f"{(df['EOSSTT'] == 'COMPLETED').mean():.0%}")
    k[4].metric("Discontinued for AE", f"{(df['DCSREAS'] == 'ADVERSE EVENT').mean():.0%}")
    c1, c2 = st.columns(2)
    counts = df["ARM"].value_counts().reindex(df["ARM"].cat.categories).reset_index()
    counts.columns = ["ARM", "Subjects"]
    fig = px.bar(counts, x="ARM", y="Subjects", color="ARM", color_discrete_map=ARM_COLORS, text="Subjects",
                 title="Subjects by treatment arm")
    fig.update_layout(showlegend=False, xaxis_title="")
    fig.update_yaxes(rangemode="tozero")  # bars always start at zero so heights compare honestly
    c1.plotly_chart(style(fig), width="stretch")
    site = df.groupby(["SITEID", "ARM"], observed=True).size().reset_index(name="Subjects")
    order = site.groupby("SITEID")["Subjects"].sum().sort_values(ascending=False).index
    fig = px.bar(site, x="SITEID", y="Subjects", color="ARM", color_discrete_map=ARM_COLORS,
                 category_orders={"SITEID": list(order)}, title="Enrolment by site")
    fig.update_layout(xaxis_title="Site", xaxis_type="category")
    c2.plotly_chart(style(fig), width="stretch")
    ts = df.dropna(subset=["RANDDT"]).assign(month=lambda d: d["RANDDT"].dt.to_period("M").dt.to_timestamp())
    cum = ts.groupby("month").size().cumsum().reset_index(name="Randomised")
    st.plotly_chart(style(px.area(cum, x="month", y="Randomised", title="Cumulative randomisation", color_discrete_sequence=["#543FDD"]), 300),
                    width="stretch")

# ---- Demographics -----------------------------------------------------------------------------
with tab_demo:
    c1, c2 = st.columns([1, 1])
    var_label = c1.selectbox("Continuous variable", list(CONTINUOUS), key="demo_var")
    var = CONTINUOUS[var_label]
    kind = c2.radio("Plot", ["Histogram", "Box", "Violin"], horizontal=True)
    if kind == "Histogram":
        fig = px.histogram(df, x=var, color="ARM", barmode="overlay", opacity=0.65, nbins=20, color_discrete_map=ARM_COLORS)
    elif kind == "Box":
        fig = px.box(df, x="ARM", y=var, color="ARM", points="all", color_discrete_map=ARM_COLORS)
    else:
        fig = px.violin(df, x="ARM", y=var, color="ARM", box=True, points="all", color_discrete_map=ARM_COLORS)
    fig.update_layout(title=f"{var_label} by arm")
    st.plotly_chart(style(fig, 420), width="stretch")
    summary = df.groupby("ARM", observed=True)[var].agg(n="count", mean="mean", sd="std", median="median", min="min", max="max").round(2)
    st.dataframe(summary, width="stretch")

    c1, c2, c3 = st.columns(3)
    for col, (label, v) in zip((c1, c2, c3), [("Sex", "SEX"), ("Age group", "AGEGR1"), ("Race", "RACE")]):
        pct = pd.crosstab(df["ARM"], df[v], normalize="index").mul(100).reset_index().melt("ARM", value_name="%")
        fig = px.bar(pct, x="ARM", y="%", color=v, title=f"{label} (% of arm)")
        fig.update_layout(xaxis_title="", yaxis_range=[0, 100])
        col.plotly_chart(style(fig, 340), width="stretch")

# ---- Disposition & exposure ----------------------------------------------------------------------
with tab_disp:
    c1, c2 = st.columns(2)
    reasons = df.groupby(["ARM", "DCSREAS"], observed=True).size().reset_index(name="Subjects")
    fig = px.bar(reasons, y="ARM", x="Subjects", color="DCSREAS", orientation="h", title="Disposition by arm",
                 color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(yaxis_title="")
    c1.plotly_chart(style(fig), width="stretch")
    fig = px.box(df, x="ARM", y="TRTDURD", color="ARM", points="all", color_discrete_map=ARM_COLORS,
                 title="Treatment duration (days)")
    fig.update_layout(showlegend=False, xaxis_title="")
    c2.plotly_chart(style(fig), width="stretch")
    dose = df[df["ARM"] != "Placebo"]
    if not dose.empty:
        fig = px.scatter(dose, x="TRTDURD", y="CUMDOSE", color="ARM", color_discrete_map=ARM_COLORS, hover_data=["USUBJID", "DCSREAS"],
                         title="Cumulative dose vs treatment duration (active arms)", trendline="ols")
        st.plotly_chart(style(fig, 360), width="stretch")
    odd = df[(df["COMPLFL"] == "Y") & (df["EOSSTT"] == "DISCONTINUED")]
    if len(odd):
        with st.expander(f"Data query: {len(odd)} subjects are flagged as completers (COMPLFL=Y) but discontinued the study"):
            st.write("Check the definition of COMPLFL with the study team before using it for a completer analysis.")
            st.dataframe(odd[["USUBJID", "ARM", "COMPLFL", "EOSSTT", "DCSREAS", "TRTDURD"]], hide_index=True, width="stretch")

# ---- Time to discontinuation ---------------------------------------------------------------------
with tab_surv:
    st.write("Time from randomisation to study discontinuation (EOSDY). Subjects who completed are censored at their last day.")
    fig = go.Figure()
    for arm, d in df.groupby("ARM", observed=True):
        km = stats.kaplan_meier(d["EOSDY"], d["DISCONTINUED"])
        fig.add_trace(go.Scatter(x=km["time"], y=km["survival"], mode="lines", line_shape="hv", name=f"{arm} (n={len(d)})",
                                 line=dict(color=ARM_COLORS.get(arm), width=3)))
    fig.update_layout(title="Probability of remaining in the study", xaxis_title="Days since randomisation",
                      yaxis_title="Proportion still on study", yaxis_range=[0, 1.02])
    st.plotly_chart(style(fig, 460), width="stretch")
    if df["ARM"].nunique() > 1:
        p = stats.logrank_p(df, "EOSDY", "DISCONTINUED")
        st.info(f"Log-rank test across arms: **{p_badge(p)}**")
    else:
        st.caption("Select at least two arms for the log-rank test.")

# ---- Statistical tests ---------------------------------------------------------------------------
with tab_tests:
    st.write("Pick a variable and the right test is run for you, comparing the treatment arms in the current selection.")
    mode = st.radio("Variable type", ["Continuous", "Categorical"], horizontal=True)
    if df["ARM"].nunique() < 2:
        st.caption("Select at least two arms.")
    elif mode == "Continuous":
        label = st.selectbox("Variable", list(CONTINUOUS), key="test_var")
        res = stats.compare_continuous(df, CONTINUOUS[label])
        if res:
            c1, c2 = st.columns(2)
            c1.metric("One-way ANOVA", stats.fmt_p(res["anova_p"]), help="Tests whether the arm means differ. Assumes roughly normal data.")
            c2.metric("Kruskal-Wallis", stats.fmt_p(res["kruskal_p"]), help="Rank-based alternative that does not assume normality.")
            st.caption("Pairwise Welch t-tests (no multiplicity adjustment - exploratory):")
            pw = res["pairwise"].assign(**{"Mean difference": lambda d: d["Mean difference"].round(2),
                                           "p-value": lambda d: d["p-value"].map(stats.fmt_p)})
            st.dataframe(pw, hide_index=True, width="stretch")
            st.plotly_chart(style(px.box(df, x="ARM", y=CONTINUOUS[label], color="ARM", color_discrete_map=ARM_COLORS, points="all"), 340),
                            width="stretch")
    else:
        label = st.selectbox("Variable", list(CATEGORICAL), key="test_cat")
        res = stats.compare_categorical(df, CATEGORICAL[label])
        if res:
            c1, c2 = st.columns(2)
            c1.metric("Chi-square test", stats.fmt_p(res["p"]))
            c2.metric("Cramer's V (effect size)", f"{res['cramers_v']:.2f}", help="0 = no association, 1 = perfect association.")
            if res["low_expected"]:
                st.warning("Some expected counts are below 5, so the chi-square p-value is approximate. Consider Fisher's exact test.")
            st.dataframe(res["table"], width="stretch")
    st.divider()
    st.subheader("Correlation")
    pick = st.multiselect("Variables", list(CONTINUOUS), default=["Age (years)", "Baseline weight (kg)", "Baseline BMI (kg/m2)", "Treatment duration (days)"])
    if len(pick) >= 2:
        corr = df[[CONTINUOUS[p] for p in pick]].corr(method="spearman")
        corr.index = corr.columns = pick
        st.plotly_chart(style(px.imshow(corr.round(2), text_auto=True, zmin=-1, zmax=1, color_continuous_scale="RdBu_r",
                                        title="Spearman correlation"), 420), width="stretch")

# ---- Table 14.1 and data -------------------------------------------------------------------------
with tab_table:
    st.subheader("Table 14.1 - production and QC (Exercise B)")
    if not paths.PROD_DM1.exists():
        st.info("Table 14.1 has not been produced yet. Run the production program (Exercise B) as a Job.")
    else:
        status = json.loads(paths.COMPARE_SUMMARY.read_text()) if paths.COMPARE_SUMMARY.exists() else None
        if status is None:
            st.warning("QC comparison has not been run.")
        elif status["status"] == "Clean":
            st.success(f"QC: production and QC match ({status['cells_compared']} cells compared).")
        else:
            st.error(f"QC: {status['cell_differences']} difference(s) between production and QC.")
            st.dataframe(pd.read_csv(paths.COMPARE_DM1, keep_default_na=False), hide_index=True, width="stretch")
        st.caption("This table is the programmed output for the whole safety population; it does not change with the sidebar filters.")
        st.dataframe(pd.read_csv(paths.PROD_DM1, keep_default_na=False), hide_index=True, width="stretch", height=500)
    st.subheader("Subject-level data (current selection)")
    st.dataframe(df.drop(columns=["DISCONTINUED"]), hide_index=True, width="stretch", height=350)
    st.download_button("Download selection as CSV", df.drop(columns=["DISCONTINUED"]).to_csv(index=False), "adsl_selection.csv", "text/csv")
