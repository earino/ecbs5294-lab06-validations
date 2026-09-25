"""Run the whole pipeline, from the project folder:

    uv run python pipeline.py

Each stage is a script in scripts/, run in order in a fresh Python process: clean (raw -> silver), report
(silver -> gold), checks. If a stage fails or a check says stop, the run stops there, says why, and exits with an
error: whatever runs after it (a dashboard, an email) must not use this run's gold.
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
STAGES = ["scripts/clean.py", "scripts/report.py", "scripts/checks.py"]

for stage in STAGES:
    print(f"\n== {stage}", flush=True)
    result = subprocess.run([sys.executable, stage], cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"\n== pipeline STOPPED at {stage}. Do not use data/gold/ from this run.", flush=True)
        sys.exit(1)
print("\n== pipeline finished: every check passed", flush=True)
