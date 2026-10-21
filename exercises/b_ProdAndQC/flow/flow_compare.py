"""Flow step 3: compare the production and QC tables and return the summary."""
import json
import os
import sys
from pathlib import Path

import pandas as pd

sys.path.append(os.environ.get("DOMINO_WORKING_DIR", "."))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "jobs"))
from compare_t_dm1 import compare, publish


def read_table(name: str) -> pd.DataFrame:
    return pd.read_csv(f"/workflow/inputs/{name}", dtype=str, keep_default_na=False)


summary, diffs = compare(read_table("prod_table"), read_table("qc_table"))
publish(summary)
print(json.dumps(summary, indent=2))
for d in diffs.to_dict("records"):
    print(f"DIFF {d['Section']} / {d['Characteristic']} / {d['Column']}: prod={d['Production']} qc={d['QC']}")

out = Path("/workflow/outputs/summary")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(summary))
