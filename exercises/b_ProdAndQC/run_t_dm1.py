"""Run the whole Table 14.1 workflow as one Domino Job.

Production, then QC, then the comparison, in that order. Each step is the same program you
can also run on its own (prod_t_dm1.py, qc_t_dm1.py, compare_t_dm1.py).
Run as a Domino Job:  python exercises/b_ProdAndQC/run_t_dm1.py
"""
import os
import sys

sys.path.append(os.environ.get("DOMINO_WORKING_DIR", "."))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import compare_t_dm1
import prod_t_dm1
import qc_t_dm1

STEPS = [("1/3 Production program", prod_t_dm1.main),
         ("2/3 QC program (independent)", qc_t_dm1.main),
         ("3/3 Compare production and QC", compare_t_dm1.main)]

for title, step in STEPS:
    print(f"\n===== {title} =====")
    step()
