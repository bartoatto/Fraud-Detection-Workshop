"""Flow step 1: production program. Reads ADSL from the mounted snapshot and returns the table."""
import json
import os
import sys
from pathlib import Path

sys.path.append(os.environ.get("DOMINO_WORKING_DIR", "."))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from common.adam import load_adsl
from prod_t_dm1 import build_table

table = build_table(load_adsl())
out = Path("/workflow/outputs/table")  # the value handed to the next steps in the flow
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(table.to_dict("records")))  # one line of JSON text
print(f"Production table: {len(table)} rows")
