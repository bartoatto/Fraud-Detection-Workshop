"""Transaction Review Desk - a Streamlit app for reviewing risky card transactions.

It reads the engineered transactions that Exercise B wrote to the NetApp Volume, ranks them
with a simple rules-based risk score, and lets a reviewer approve, reject or escalate each
one. Every decision is saved with the reviewer and a timestamp.
Published as a Domino App through app.sh.
"""
import os
import sys
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

sys.path.append(os.environ.get("DOMINO_WORKING_DIR", os.path.abspath("../..")))
from common import paths
from common.features import RISK_FLAGS

st.set_page_config(page_title="Transaction Review Desk", page_icon="🔒", layout="wide")

DECISIONS = ["Pending", "Approve", "Reject", "Escalate"]


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(paths.ENGINEERED_FILE, index_col=0)


st.title("🔒 Transaction Review Desk")
if not paths.ENGINEERED_FILE.exists():
    st.warning(f"{paths.ENGINEERED_FILE.name} not found on the NetApp Volume. "
               "Run Exercise B (`exercises/b_DataEngineering/data_engineering.py`) as a Job, then reload.")
    st.stop()

data = load_data()
tab_overview, tab_queue = st.tabs(["Overview", "Review queue"])

with tab_overview:
    st.write("Each transaction is scored 0-7 by how many simple risk rules it trips. "
             "The rules are readable, so a reviewer can see why something was flagged.")
    m1, m2, m3 = st.columns(3)
    m1.metric("Transactions", f"{len(data):,}")
    m2.metric("High risk (4+ flags)", f"{(data['risk_flags'] >= 4).sum():,}")
    m3.metric("Known fraud rate", f"{data['Class'].mean():.1%}")

    left, right = st.columns(2)
    with left:
        st.subheader("Transactions by risk flags")
        st.bar_chart(data["risk_flags"].value_counts().sort_index())
    with right:
        st.subheader("How often each rule trips")
        counts = {name: int(rule(data).sum()) for name, rule in RISK_FLAGS.items()}
        st.bar_chart(pd.Series(counts).sort_values())

    st.subheader("Does the score line up with known outcomes?")
    check = data.groupby("risk_flags")["Class"].agg(fraud_rate="mean", transactions="count")
    st.dataframe(check.style.format({"fraud_rate": "{:.1%}", "transactions": "{:,}"}), use_container_width=True)

with tab_queue:
    st.write("The riskiest transactions in a random sample. Pick a decision for each row and save; "
             "decisions are logged with who made them and when.")
    q1, q2, q3 = st.columns(3)
    sample_size = q1.number_input("Sample size", 100, 20000, 2000, step=100)
    top_n = q2.number_input("Rows to review", 5, 50, 10)
    seed = q3.number_input("Sample seed", 0, 9999, 42)

    sample = data.sample(n=min(int(sample_size), len(data)), random_state=int(seed))
    queue = (sample.sort_values("risk_flags", ascending=False, kind="stable").head(int(top_n))
             .rename_axis("transaction_id").reset_index())
    queue["decision"] = "Pending"
    shown = ["transaction_id", "risk_flags", "flags_tripped", "Amount", "MerchantCat", "Channel", "Hour"]

    edited = st.data_editor(
        queue[shown + ["decision"]], hide_index=True, use_container_width=True, disabled=shown,
        column_config={"decision": st.column_config.SelectboxColumn("Decision", options=DECISIONS, required=True)},
    )
    reviewer = os.environ.get("DOMINO_STARTING_USERNAME", os.environ.get("DOMINO_USER_NAME", "unknown"))
    if st.button("Save decisions", type="primary"):
        decided = edited[edited["decision"] != "Pending"].copy()
        if decided.empty:
            st.info("Pick a decision for at least one row first.")
        else:
            decided["reviewer"] = reviewer
            decided["decided_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            paths.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
            decided[["transaction_id", "risk_flags", "decision", "reviewer", "decided_at"]].to_csv(
                paths.DECISIONS_FILE, mode="a", index=False, header=not paths.DECISIONS_FILE.exists())
            st.success(f"Saved {len(decided)} decision(s) to {paths.DECISIONS_FILE.name}")

    if paths.DECISIONS_FILE.exists():
        with st.expander("Decision log"):
            st.dataframe(pd.read_csv(paths.DECISIONS_FILE).tail(50), hide_index=True, use_container_width=True)
