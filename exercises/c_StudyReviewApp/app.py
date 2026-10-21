"""Study Review Desk - a Streamlit app for reviewing a study's analysis outputs.

Reads ADSL and the Table 14.1 outputs from the NetApp Volume, shows the study at a glance,
and lets a reviewer sign off the table. Sign-off is gated: a table can only be approved when
the production and QC versions match. Every decision is logged with who and when.
Published as a Domino App through app.sh.
"""
import json
import os
import sys
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

sys.path.append(os.environ.get("DOMINO_WORKING_DIR", os.path.abspath("../..")))
from common import paths
from common.adam import load_adsl

st.set_page_config(page_title="Study Review Desk", page_icon="🧪", layout="wide")


@st.cache_data
def adsl_data() -> pd.DataFrame:
    return load_adsl()


def qc_status() -> dict | None:
    return json.loads(paths.COMPARE_SUMMARY.read_text()) if paths.COMPARE_SUMMARY.exists() else None


st.title("🧪 Study Review Desk")
st.caption("Protocol CDISCPILOT01 - Safety population")

if not paths.ADSL_FILE.exists():
    st.error(f"ADSL not found at {paths.ADSL_FILE}. Check that the NetApp Volume is attached to the project.")
    st.stop()

adsl = adsl_data()
tab_study, tab_table, tab_subjects, tab_signoff = st.tabs(["Study overview", "Table 14.1", "Subjects", "Sign-off"])

with tab_study:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Subjects", len(adsl))
    m2.metric("Sites", adsl["SITEID"].nunique())
    m3.metric("Completed the study", f"{(adsl['EOSSTT'] == 'COMPLETED').mean():.0%}")
    m4.metric("Median age", f"{adsl['AGE'].median():.0f}")
    left, right = st.columns(2)
    with left:
        st.subheader("Subjects by arm")
        st.bar_chart(adsl["ARM"].value_counts())
    with right:
        st.subheader("Why subjects discontinued")
        st.bar_chart(adsl["DCSREAS"].dropna().value_counts())
    st.subheader("Disposition by arm")
    st.dataframe(pd.crosstab(adsl["ARM"], adsl["EOSSTT"], margins=True), use_container_width=True)

with tab_table:
    status = qc_status()
    if not paths.PROD_DM1.exists():
        st.info("Table 14.1 has not been produced yet. Run the production program (Exercise B) as a Job.")
    else:
        st.subheader("Summary of Demographic and Baseline Characteristics")
        st.dataframe(pd.read_csv(paths.PROD_DM1, keep_default_na=False), hide_index=True, use_container_width=True, height=600)
        if status is None:
            st.warning("QC comparison has not been run.")
        elif status["status"] == "Clean":
            st.success(f"QC: production and QC match ({status['cells_compared']} cells compared).")
        else:
            st.error(f"QC: {status['cell_differences']} difference(s) between production and QC.")
            st.dataframe(pd.read_csv(paths.COMPARE_DM1, keep_default_na=False), hide_index=True, use_container_width=True)

with tab_subjects:
    f1, f2, f3 = st.columns(3)
    arms = f1.multiselect("Arm", sorted(adsl["ARM"].unique()))
    sexes = f2.multiselect("Sex", sorted(adsl["SEX"].unique()))
    sites = f3.multiselect("Site", sorted(adsl["SITEID"].unique()))
    view = adsl
    if arms:
        view = view[view["ARM"].isin(arms)]
    if sexes:
        view = view[view["SEX"].isin(sexes)]
    if sites:
        view = view[view["SITEID"].isin(sites)]
    st.caption(f"{len(view)} of {len(adsl)} subjects")
    st.dataframe(view[["USUBJID", "SITEID", "ARM", "AGE", "SEX", "RACE", "EOSSTT", "DCSREAS", "TRTDURD"]],
                 hide_index=True, use_container_width=True)

with tab_signoff:
    st.write("Sign off a table once its QC is clean. This is a simple, linear review: one reviewer, one decision, "
             "recorded with a timestamp.")
    status = qc_status()
    gate_open = status is not None and status["status"] == "Clean"
    if gate_open:
        st.success("Gate open: production and QC match.")
    else:
        st.warning("Gate closed: the table can only be approved when the QC comparison is clean.")

    options = ["Approve", "Request changes"] if gate_open else ["Request changes"]
    decision = st.radio("Decision", options, horizontal=True)
    comment = st.text_area("Comment", placeholder="Optional for approval, required when requesting changes")
    reviewer = os.environ.get("DOMINO_STARTING_USERNAME", os.environ.get("DOMINO_USER_NAME", "unknown"))
    if st.button("Record decision", type="primary"):
        if decision == "Request changes" and not comment.strip():
            st.error("Add a comment explaining what needs to change.")
        else:
            paths.ensure(paths.SIGNOFF_DIR)
            entry = pd.DataFrame([{"table": "t_dm1", "decision": decision, "comment": comment.strip(),
                                   "qc_status": status["status"] if status else "Not run", "reviewer": reviewer,
                                   "decided_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}])
            entry.to_csv(paths.SIGNOFF_LOG, mode="a", index=False, header=not paths.SIGNOFF_LOG.exists())
            st.success(f"{decision} recorded for t_dm1 by {reviewer}.")

    if paths.SIGNOFF_LOG.exists():
        st.subheader("Sign-off log")
        st.dataframe(pd.read_csv(paths.SIGNOFF_LOG, keep_default_na=False).iloc[::-1], hide_index=True, use_container_width=True)
