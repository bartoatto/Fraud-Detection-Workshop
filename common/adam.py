"""Read the ADaM subject-level dataset and format numbers the way SAS would."""
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd

from common import paths


def load_adsl() -> pd.DataFrame:
    """Load ADSL (a SAS sas7bdat file) into a DataFrame."""
    return pd.read_sas(paths.ADSL_FILE, encoding="latin1")


def round_half_up(value: float, places: int = 1) -> str:
    """Format with round-half-up, as SAS does. Python's own round() uses banker's rounding."""
    step = Decimal(1).scaleb(-places)
    return str(Decimal(repr(float(value))).quantize(step, rounding=ROUND_HALF_UP))
