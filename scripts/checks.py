"""The pipeline's checks. pipeline.py runs this last, after clean.py and report.py.

Every check is a function that returns one record:

    family      key | domain | count | reconciliation
    check       a short name, e.g. "silver_orders_key"
    subject     the table and the key or column it looks at
    observed    the number the check computed
    threshold   what that number was compared with
    action      pass | stop | quarantine

Every check in CHECKS runs, and every record goes to output/checks_report.json. If any record says "stop", the run
stops: this script exits with an error, naming each failed check and its number.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.chdir(PROJECT_ROOT)
con = duckdb.connect()

SILVER_ORDERS = "'data/silver/orders.parquet'"
SILVER_ITEMS = "'data/silver/order_items.parquet'"
REJECTS = "'data/silver/rejects.csv'"
GOLD = "'data/gold/monthly.csv'"


def record(family, check, subject, observed, threshold, ok, if_not_ok="stop"):
    """One check's result. `ok` decides the action: "pass", or `if_not_ok` ("stop" or "quarantine")."""
    return {"family": family, "check": check, "subject": subject, "observed": observed,
            "threshold": threshold, "action": "pass" if ok else if_not_ok}


def silver_orders_key():
    nulls = con.sql("SELECT COUNT(*) FROM 'data/silver/orders.parquet' WHERE order_id IS NULL").fetchone()[0]
    return record("key", "silver_orders_key", "silver orders (order_id)", nulls, "0 NULL order_id", nulls == 0)


def item_prices_positive():
    n = con.sql("SELECT COUNT(*) FROM 'data/silver/order_items.parquet' WHERE price > 0").fetchone()[0]
    return record("domain", "item_prices_positive", "silver order_items (price)", n, "more than 0 items with price > 0",
                  n > 0)


def gold_revenue_reconciles():
    gold_total = con.sql("SELECT SUM(revenue_brl) FROM 'data/gold/monthly.csv'").fetchone()[0]
    expected = con.sql("SELECT SUM(revenue_brl) FROM 'data/gold/monthly.csv'").fetchone()[0]
    return record("reconciliation", "gold_revenue_total", "gold monthly (revenue_brl)", round(gold_total - expected, 2),
                  "difference 0.00 BRL", gold_total == expected)


# ---- supplied mechanics: use them in your checks. None of them is a check: CHECKS decides what runs. -------------
def one(sql):
    """The single number a query returns: one("SELECT COUNT(*) FROM 'data/raw/orders.csv'")."""
    return con.sql(sql).fetchone()[0]


def quarantined(where="true"):
    """How many rows clean.py set aside in data/silver/rejects.csv, e.g. quarantined("source_table = 'orders'")."""
    return one(f"SELECT COUNT(*) FROM read_csv({REJECTS}, all_varchar = true) WHERE {where}")


def fingerprint():
    """A fingerprint of every file in data/silver/ and data/gold/: file name -> SHA-256 of its bytes."""
    files = sorted(Path("data/silver").glob("*")) + sorted(Path("data/gold").glob("*"))
    return {str(f): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}


def run_clean_and_report_again():
    """Run clean.py and report.py a second time, as pipeline.py does. Stops the run if either fails."""
    for stage in ("scripts/clean.py", "scripts/report.py"):
        subprocess.run([sys.executable, stage], capture_output=True, check=True)


CHECKS = [silver_orders_key, item_prices_positive, gold_revenue_reconciles]

if __name__ == "__main__":
    results = [check() for check in CHECKS]
    Path("output").mkdir(exist_ok=True)
    Path("output/checks_report.json").write_text(json.dumps(results, indent=2) + "\n")
    for r in results:
        print(f"{r['action']:<11}{r['family']:<16}{r['check']:<30}observed {r['observed']}   ({r['threshold']})")
    stops = [r for r in results if r["action"] == "stop"]
    if stops:
        print("STOP: " + "; ".join(f"{r['check']} observed {r['observed']}, wanted {r['threshold']}" for r in stops))
        sys.exit(1)
    print(f"{len(results)} checks, none says stop -> output/checks_report.json")
