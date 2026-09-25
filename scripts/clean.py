"""Raw -> silver: Olist orders and their items.

Run by pipeline.py (or on its own: uv run python scripts/clean.py). Reads data/raw/ and never edits it.
Writes data/silver/orders.parquet (one row per order), data/silver/order_items.parquet (one row per item), and
data/silver/rejects.csv (every row a domain rule set aside, with the reason).
"""
import os
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.chdir(PROJECT_ROOT)
Path("data/silver").mkdir(parents=True, exist_ok=True)
con = duckdb.connect()

# A. Quarantine. The mechanics are supplied; the rules are yours (the README's domain family). A row that breaks a
#    rule is quarantined: it goes to data/silver/rejects.csv with its reason, it stays out of silver, and the run goes
#    on. No rule is written yet, so nothing is quarantined: `WHERE false`. Write each rule into the WHERE, and its
#    reason into `reason` (a CASE, if a view has more than one rule). Keep the four columns as they are.
con.sql("""
    CREATE VIEW order_rejects AS
    SELECT 'orders' AS source_table, order_id, NULL::BIGINT AS order_item_id,
           'no rule yet' AS reason
    FROM 'data/raw/orders.csv'
    WHERE false
""")
con.sql("""
    CREATE VIEW item_rejects AS
    SELECT 'order_items' AS source_table, order_id, order_item_id,
           'no rule yet' AS reason
    FROM 'data/raw/order_items.csv'
    WHERE false
""")

# B. Silver orders: one row per order_id, without the quarantined ones.
con.sql("""
    CREATE VIEW silver_orders AS
    SELECT order_id,
           customer_id,
           order_status,
           order_purchase_timestamp AS purchased_at
    FROM 'data/raw/orders.csv'
    WHERE order_id NOT IN (SELECT order_id FROM order_rejects)
      AND order_status = 'delivered'
""")

# C. Silver items: one row per (order_id, order_item_id), for the orders in silver, without the quarantined ones.
con.sql("""
    CREATE VIEW silver_items AS
    SELECT order_id, order_item_id, product_id, price, freight_value
    FROM 'data/raw/order_items.csv'
    WHERE order_id IN (SELECT order_id FROM silver_orders)
      AND (order_id, order_item_id) NOT IN (SELECT (order_id, order_item_id) FROM item_rejects)
""")

# D. Write silver and the rejects. Overwritten on every run.
con.sql("COPY (SELECT * FROM silver_orders ORDER BY order_id) TO 'data/silver/orders.parquet' (FORMAT parquet)")
con.sql("COPY (SELECT * FROM silver_items ORDER BY order_id, order_item_id) TO 'data/silver/order_items.parquet' (FORMAT parquet)")
con.sql("""
    COPY (SELECT * FROM order_rejects UNION ALL SELECT * FROM item_rejects ORDER BY source_table, order_id, order_item_id)
    TO 'data/silver/rejects.csv' (HEADER)
""")
n_orders = con.sql("SELECT COUNT(*) FROM 'data/silver/orders.parquet'").fetchone()[0]
n_items = con.sql("SELECT COUNT(*) FROM 'data/silver/order_items.parquet'").fetchone()[0]
n_rejects = con.sql("SELECT COUNT(*) FROM order_rejects").fetchone()[0] + con.sql("SELECT COUNT(*) FROM item_rejects").fetchone()[0]
print(f"silver: {n_orders:,} orders -> data/silver/orders.parquet; {n_items:,} items -> data/silver/order_items.parquet")
print(f"quarantined: {n_rejects:,} rows -> data/silver/rejects.csv")
