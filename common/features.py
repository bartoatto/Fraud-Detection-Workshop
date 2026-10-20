"""Feature engineering shared by the data-engineering job and the app."""
from datetime import datetime

import pandas as pd

LABEL = "Class"


def get_generation_label(age: float) -> str:
    birth_year = datetime.today().year - age
    if birth_year <= 1945:
        return "Silent Generation"
    if birth_year <= 1964:
        return "Baby Boomer"
    if birth_year <= 1980:
        return "Generation X"
    if birth_year <= 1996:
        return "Millennial"
    if birth_year <= 2012:
        return "Generation Z"
    return "Generation Alpha"


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add the engineered columns."""
    df = df.copy()
    # Spend relative to the customer's 30 day average (epsilon avoids dividing by zero).
    df["amount_vs_avg30d_ratio"] = df["Amount"] / (df["Avg30d"] + 1e-6)
    # Average of merchant risk and IP reputation.
    df["risk_score"] = (df["MerchantRisk"] + df["IPReputation"]) / 2
    # Device trust minus merchant risk: a trusted device on a risky merchant scores high.
    df["trust_score"] = df["DeviceTrust"] - df["MerchantRisk"]
    df["generation"] = df["Age"].apply(get_generation_label)
    return df


RISK_FLAGS = {
    "Card not present": lambda d: d["CardPresent"] == 0,
    "Online channel": lambda d: d["Channel"] == "online",
    "Risky merchant": lambda d: d["MerchantRisk"] > 1,
    "Untrusted device": lambda d: d["DeviceTrust"] < -1,
    "Poor IP reputation": lambda d: d["IPReputation"] < -1,
    "Far from home": lambda d: d["DistFromHome"] > 2,
    "Night-time": lambda d: d["Hour"].isin([0, 1, 2, 3, 4, 5, 23]),
}


def add_risk_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Count how many simple, explainable rules a transaction trips (0-7).

    This is a rules-based score a reviewer can read, not a trained model.
    """
    df = df.copy()
    flags = pd.DataFrame({name: rule(df) for name, rule in RISK_FLAGS.items()})
    df["risk_flags"] = flags.sum(axis=1)
    df["flags_tripped"] = flags.apply(lambda row: ", ".join(row.index[row]), axis=1)
    return df
