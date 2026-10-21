"""Quick check that a compute environment can run this workshop.

Run this in a workspace terminal after building the environment:
    python .setup/verify_environment.py
"""

import importlib

# Everything exercises A-C actually import.
REQUIRED = [
    "pandas", "numpy", "matplotlib", "seaborn", "streamlit",
]
# Nice to have, but the workshop degrades gracefully without them.
OPTIONAL = [
    ("domino", "python-domino; only needed for jobs/launch_job.py"),
    ("flytekitplugins.domino.task", "Domino flows plugin; only needed for flow/workflow.py"),
]

def version(name):
    try:
        return importlib.import_module(name).__version__
    except Exception:
        return "?"

failed = []
print("Required:")
for mod in REQUIRED:
    try:
        importlib.import_module(mod)
        print(f"  ok      {mod:26} {version(mod)}")
    except ImportError as exc:
        failed.append(mod)
        print(f"  MISSING {mod:26} {exc}")

print("\nOptional:")
for mod, note in OPTIONAL:
    try:
        importlib.import_module(mod)
        print(f"  ok      {mod:26} {version(mod)}")
    except ImportError:
        print(f"  absent  {mod:26} {note}")

# ydata-profiling before 4.16 requires numpy<2, so it pins numpy back. That
# combination is supported - this just makes it visible.
try:
    import numpy
    from ydata_profiling import __version__ as yd
    print(f"\nnumpy {numpy.__version__} with ydata-profiling {yd}")
except ImportError:
    pass

print("\nFAILED - install the missing packages above" if failed else "\nPASS - environment can run the workshop")
raise SystemExit(1 if failed else 0)
