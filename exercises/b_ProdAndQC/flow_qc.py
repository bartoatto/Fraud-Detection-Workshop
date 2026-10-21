"""Flow step 2: QC program. Independently rebuilds the table and returns it."""
import os
import sys
from pathlib import Path

sys.path.append(os.environ.get("DOMINO_WORKING_DIR", "."))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from common.adam import load_adsl
from qc_t_dm1 import build_table, plant_difference

table = plant_difference(build_table(load_adsl()))
out = Path("/workflow/outputs/table")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(table.to_csv(index=False))
print(f"QC table: {len(table)} rows")
