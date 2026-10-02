# SQL reference — one page

Everything a lab in this course asks you to write, in the order it was taught. Nothing here is new: each line is
on a slide of the block named beside it. Keep it open in a second tab. Paths are always `'data/raw/<file>'`
from the project folder, and every query is `con.sql("""...""").df()`; a single number is
`con.sql("...").fetchone()[0]`. The full reference, with a task index in plain English ("I want the first
character of a code…"), joins, JSON, pipelines and checks, is on the course site:
https://earino.github.io/ecbs5294-2026/site/reference.html
## Block 1 — one table, one row at a time

**The four inspection recipes** (copy exactly; the grammar is Block 2's).

```sql
DESCRIBE SELECT * FROM 'data/raw/owid_co2.csv';                      -- one row per column: its name and type
SUMMARIZE SELECT * FROM 'data/raw/owid_co2.csv';                      -- min, max, nulls, distinct, per column
SELECT COUNT(*), COUNT(DISTINCT (country, year)) FROM 'data/raw/owid_co2.csv';   -- rows against distinct keys
SELECT country, COUNT(*) AS n FROM 'data/raw/owid_co2.csv'
GROUP BY country ORDER BY n DESC;                                     -- the census: one row per value, read to the end
```

**The four-clause `SELECT`.** The clauses go in this order and no other.

```sql
SELECT country, co2              -- the columns you want, or * for all
FROM 'data/raw/owid_co2.csv'     -- the file
WHERE year = 2024                -- keep the rows where this is true
ORDER BY co2 DESC                -- DESC largest first; ASC (the default) smallest first
LIMIT 10;                        -- the first n rows of that order
```

**Comparisons in `WHERE`.** `=`, `!=`, `<`, `<=`, `>`, `>=`; text in single quotes, exactly as the file spells it
(`'International aviation'`, not `'international aviation'`). `IN ('A', 'B')` is "any of these".

**Missing values.** A missing value is `NULL`. It is not a value: `= NULL` and `!= NULL` are never true, so a
`WHERE` with either keeps nothing and says nothing. The only tests are `IS NULL` and `IS NOT NULL`.
pandas prints a `NULL` as `NaN` or `None`, neither of which is in the file: do not put those words in a query.

**Two conditions.** `AND` keeps a row when both are true; `OR` when either is.

```sql
WHERE year = 2024 AND country = 'World'
WHERE iso_code IS NOT NULL OR country = 'Kosovo'
```

**A view: a saved query with a name.** Write the filter once, read from it everywhere. It is not a copy of the
data; it re-runs its query each time it is read.

```sql
CREATE OR REPLACE VIEW countries AS
SELECT * FROM 'data/raw/owid_co2.csv'
WHERE iso_code IS NOT NULL;
-- then:  SELECT COUNT(*) FROM countries;
```

**One number into Python.** `.fetchone()` returns the first row of the result; `[0]` takes its first column.

```python
world = con.sql("SELECT co2 FROM 'data/raw/owid_co2.csv' WHERE year = 2024 AND country = 'World'").fetchone()[0]
```

## Block 2 — one table, groups

**Aggregates** collapse many rows into one number. `COUNT(*)` counts rows; `COUNT(col)` counts the rows where
`col` is not `NULL`; `COUNT(DISTINCT col)` counts its different values. `SUM`, `AVG`, `MIN`, `MAX` skip `NULL`.
An average over a column with gaps is the average of the rows that have a value.

```sql
SELECT COUNT(*) AS n_rows, COUNT(co2) AS n_co2, COUNT(DISTINCT country) AS n_countries,
       SUM(co2) AS total, AVG(co2) AS mean, MIN(co2), MAX(co2)
FROM countries WHERE year = 2024;
```

**`GROUP BY`**: one output row per distinct value of the grouped columns. Every column in the `SELECT` that is
not inside an aggregate must be in the `GROUP BY`. A `NULL` in the grouped column is a group of its own.

```sql
SELECT year, SUM(co2) AS total
FROM countries
GROUP BY year
ORDER BY year;
```

**The order a query runs**: `FROM` → `WHERE` → `GROUP BY` → aggregates in `SELECT` → `ORDER BY` → `LIMIT`.
`WHERE` runs before any group exists, so it cannot test a count. A name you make with `AS` is born in
`SELECT`; this course repeats the expression in `WHERE` rather than the name.

**Calculated columns and aliases.** `Quantity * Price AS revenue`. `ROUND(x, 2)` is for display: round when you
print, never while you are still adding up.

**`COALESCE(col, 0)`**: the first of its values that is not `NULL`.

**Dates.** `year(InvoiceDate)`, `month(InvoiceDate)`, `date_trunc('month', InvoiceDate)` (the first day of that
month, so months group and sort correctly).

```sql
SELECT date_trunc('month', InvoiceDate) AS month, SUM(Quantity * Price) AS revenue
FROM sales_2010
GROUP BY month
ORDER BY month;
```

**Text.** `left(Invoice, 1)` is the first character.

**A query inside a query.** The inner `SELECT` makes a table; the outer one reads it.

```sql
SELECT SUM(revenue) FROM (
    SELECT year, SUM(co2) AS revenue FROM countries GROUP BY year
);
```

**Comparing two sums.** Never `==`: two correct sums of the same rows can differ in the last decimal.
`abs(a - b) < 0.005` is "equal to the penny"; the identity is that a breakdown adds up to its total, so the two
numbers tie out.
## Block 3 — tables meet

**Joins.** `JOIN` (that is, `INNER JOIN`) keeps the rows that match on both sides and drops the rest without a
word. `LEFT JOIN` keeps every row of the left table; where the right side has no match its columns are `NULL`.

```sql
SELECT o.order_id, i.price
FROM orders AS o
LEFT JOIN order_items AS i ON i.order_id = o.order_id;
```

**The three counts after every join**: rows that went in, rows that came out, distinct keys that came out.
`COUNT(*)` against `COUNT(DISTINCT o.order_id)`: more rows than keys is fan-out.

**The rows a join lost** (the anti-join): a `LEFT JOIN`, then keep the rows whose right side is `NULL`.

```sql
SELECT o.order_id FROM orders AS o
LEFT JOIN order_items AS i ON i.order_id = o.order_id
WHERE i.order_id IS NULL;
```

**`HAVING`**: a `WHERE` on groups; it runs after `GROUP BY`, so it can test a count. This finds the keys that repeat.

```sql
SELECT order_id, COUNT(*) AS n FROM order_items
GROUP BY order_id
HAVING COUNT(*) > 1;
```

**A CTE**: a named query you write first and read below, `WITH name AS (...)`. Aggregate at the grain of the
measure, then join only what does not multiply it.

```sql
WITH per_order AS (
    SELECT order_id, SUM(price) AS items_total FROM order_items GROUP BY order_id
)
SELECT o.order_id, p.items_total
FROM orders AS o
LEFT JOIN per_order AS p ON p.order_id = o.order_id;
```

## Block 4 — documents into tables, and shares

**JSON.** `read_json_auto('data/raw/api/<file>.json')` reads a document. `unnest(list)` makes one row per
element. `->` goes one level in (still JSON); `->>` takes the value out as text, so wrap it: `CAST(r->>'value' AS BIGINT)`.
A struct is read with a dot: `rates."2024-01-02".BRL` (double quotes for a name that starts with a digit).

**A share of a total**: the total as a query inside the query, and the same rows on the top and the bottom.

```sql
SELECT country, co2 / (SELECT SUM(co2) FROM countries WHERE year = 2024) AS share
FROM countries WHERE year = 2024 ORDER BY share DESC;
```

**`CASE`**: a value chosen by a condition. `CASE WHEN year = 2024 THEN co2 END` is `co2` for that year and
`NULL` otherwise. A ratio of a whole is a weighted mean, never the average of the ratios.
## Block 5 — bronze, silver, gold

**Reading text as text.** `read_csv('data/raw/<file>.tsv', delim = '\t', all_varchar = true)`: every cell
arrives as the text the source wrote, so nothing is guessed. `split_part(text, ',', 2)` is the second
comma-separated piece. `TRIM(text)` strips spaces.

**Casting.** `CAST(cell AS DOUBLE)` refuses and names the value it cannot read. `TRY_CAST(cell AS DOUBLE)` never
errors: what it cannot read becomes `NULL`, silently, so count what it swallowed:

```sql
SELECT cell, COUNT(*) FROM long
WHERE TRY_CAST(cell AS DOUBLE) IS NULL
GROUP BY cell;
```

**Counting under a condition.** `COUNT(*) FILTER (WHERE geo IS NULL)` counts the rows where the condition holds,
inside one query with other counts.

## Block 6 — validations

**`AND` binds tighter than `OR`.** `a OR b AND c` means `a OR (b AND c)`. Parentheses every time you mix them,
or `col IN ('GEN', 'TRT')`.

**A check that can fail.** `assert condition, "message that names the number"` stops the run. Sums are compared
with a tolerance, never `==`: `assert abs(a - b) < 0.005, f"differ by {a - b:.4f}"`. The four families: key
(no duplicates), domain (every value is one of the allowed), count (the rows you expect), reconciliation (the
breakdown ties out to its total).
