"""Silver -> gold: orders and revenue per month.

Run by pipeline.py (or on its own: uv run python scripts/report.py). Reads data/silver/, writes data/gold/monthly.csv.
Revenue is the sum of item prices, in Brazilian reais (BRL), without freight.
"""
import os
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.chdir(PROJECT_ROOT)
Path("data/gold").mkdir(parents=True, exist_ok=True)
con = duckdb.connect()

# Gold: one row per month. Item prices are summed per order first, so an order with three items is one order.
con.sql("""
    CREATE VIEW gold AS
    WITH order_value AS (
        SELECT order_id, SUM(price) AS items_brl
        FROM 'data/silver/order_items.parquet'
        GROUP BY order_id
    )
    SELECT strftime(date_trunc('month', o.purchased_at), '%Y-%m') AS month,
           COUNT(*)                                                AS orders,
           ROUND(SUM(v.items_brl), 2)                              AS revenue_brl
    FROM 'data/silver/orders.parquet' AS o
    LEFT JOIN order_value AS v USING (order_id)
    GROUP BY month
""")
con.sql("COPY (SELECT * FROM gold ORDER BY month) TO 'data/gold/monthly.csv' (HEADER)")

print("Orders and revenue per month (revenue: item prices, BRL)")
print(con.sql("SELECT * FROM gold ORDER BY month").df().to_string(index=False))
orders, revenue, months = con.sql("SELECT SUM(orders), SUM(revenue_brl), COUNT(*) FROM gold").fetchone()
print(f"\nOrders, all months: {orders:,}")
print(f"Revenue, all months: {revenue:,.2f} BRL")
print(f"Months: {months}")
print("-> data/gold/monthly.csv")
