# Lab 6 — The pipeline that passes its own tests

**ECBS5294 — Working with Data · Session 3, Block 6**

## Start here

| | |
|---|---|
| **The question** | How many orders did the shop take each month, and what was their revenue? |
| **The files** | `data/raw/orders.csv` and `data/raw/order_items.csv` — Olist, a Brazilian marketplace (a selected sample, not a representative one). |
| **What is wrong** | Every check passes. The report's number of orders does not match the raw file. |
| **What you hand in** | `DIAGNOSIS.md` and `NOTE.md` on Moodle, before you leave. |
| **First thing to do** | `uv run python pipeline.py`, and read what each check says. |

## Where things are

| | Where | What you do there |
|---|---|---|
| **Run** | the terminal, in the project folder | `uv run python pipeline.py`: `clean.py`, `report.py`, `checks.py`, in order; it stops at the first stage that fails |
| **Inspect** | `output/checks_report.json` (one record per check), and `notebooks/diagnose.ipynb` (kernel: `.venv`) for your own queries | look; nothing here changes a file |
| **Edit** | `scripts/checks.py` (the checks); `scripts/clean.py` (the decision, the domain rules); `scripts/report.py` (the label, if you keep delivered orders) | never `data/raw/` |
| **Record** | `DIAGNOSIS.md` (the evidence), `NOTE.md` (for the shop) | paste each query and what it returned |

**Your first three actions:** (1) run the pipeline and read each check's record; (2) open `scripts/checks.py` and,
for each of the three checks, write in `DIAGNOSIS.md` part 3 a wrong table it would pass; (3) open
`notebooks/diagnose.ipynb`, pick the `.venv` kernel, and find the orders the report does not count.

## Get the project

If you cloned it during the stretch, you already have it. Otherwise, in your terminal (Git Bash on Windows,
Terminal on macOS), in the folder where you keep course work:

```bash
git clone https://github.com/earino/ecbs5294-lab06-validations.git
cd ecbs5294-lab06-validations
uv sync
```

Open **this folder** in VS Code (*File → Open Folder…*). From the project folder, in the terminal:

```bash
uv run python pipeline.py
```

`pipeline.py` runs three scripts, in order, and stops at the first one that fails:

- `scripts/clean.py` — raw to **silver**: `data/silver/orders.parquet` (one row per order) and
  `data/silver/order_items.parquet` (one row per item). Its section A, the quarantine, is supplied with no rules in
  it: rows it sets aside go to `data/silver/rejects.csv`, with the reason.
- `scripts/report.py` — silver to **gold**: `data/gold/monthly.csv`, orders and revenue per month. Revenue is the sum
  of item prices, in Brazilian reais (BRL), without freight.
- `scripts/checks.py` — the checks. Each one returns a record (family, check, subject, observed, threshold, action),
  and all of them go to `output/checks_report.json`. If any record says `stop`, the run stops.

`notebooks/diagnose.ipynb` is where you run the queries the pipeline never runs (pick the `.venv` kernel). The
pipeline never reads it.

`data/raw/` also has `order_payments.csv`, `customers.csv` and `products.csv`. This pipeline does not read them.

## What is broken

The pipeline ends with **"every check passed"**. The report says the shop took **2,555 orders**, over 22 months.

`data/raw/orders.csv` has one row per order. Count its rows. Nothing errors, and three checks say `pass`. Find out
why, before you change anything.

## What you must produce

**Today the lab starts early.** The lecture gives its spare minutes to the lab, and they are spent on step 4, the
domain family, which Homework 3 requires. `scripts/checks.py` ends with **supplied mechanics** — `one()`,
`quarantined()`, `fingerprint()`, `run_clean_and_report_again()` — so your minutes go to the checks, not to plumbing.

1. **Name the wrong data** (`DIAGNOSIS.md`, part 3). For each of the three checks in `scripts/checks.py`, write one
   sentence: a wrong silver or gold table that this check would pass. Not "make it fail" — a weak check can be made to
   fail and is still weak. Then find the orders the report does not count, with a query the pipeline never runs, in
   `notebooks/diagnose.ipynb`.
2. **Three families** (`scripts/checks.py`). Fix or replace the key check and the reconciliation, and add the count
   family, so that each check can fail on the wrong data you named. All three **stop** the run:
   - **key** — silver orders: `order_id` unique and never `NULL`.
   - **count** — every raw order is accounted for: raw orders = silver orders, plus any you leave out on purpose,
     counted and named. And **idempotency**: `fingerprint()`, then `run_clean_and_report_again()`, then
     `fingerprint()` again; silver and gold must be the same files, byte for byte.
   - **reconciliation** — gold's monthly orders sum to the orders in silver, and gold's monthly revenue sums to the
     item prices in silver, **with a tolerance, never `==`**: gold rounds each month to the cent, and two sums of the
     same prices can differ in the last digits. `abs(a - b) <= tolerance`, and the difference in the message.

   Add each one to `CHECKS`. Run the pipeline. Watch it refuse, and read the number in the message.
3. **Decide.** Either fix `clean.py` (keep every order), or fix the label (gold says what it counts). Both are
   accepted. The decision must be the same in three places: the count check's expectation, the report's label, and
   the note.
4. **The domain family**, in the minutes the lecture gave back. Three rules, each from a census or from meaning:
   `order_status` is one of the values a census of the raw file finds; no item has a negative price; every purchase
   date is inside the data's window, September 2016 to October 2018. A row that breaks one is **quarantined**: write
   the rule into `scripts/clean.py`'s section A, with its reason. Then, in `checks.py`, one domain check per rule that
   reports how many were quarantined (`quarantined()`, action `quarantine`), and stops only if a bad row reached
   silver anyway. The count check now reads raw = silver + quarantined (+ excluded). Delete the weak price check.
   Before you trust a rule, break a **copy** of the project and watch it quarantine (the Rules below).
5. **The note** (`NOTE.md`). Three to five sentences, for someone who runs the shop and does not read SQL: what the
   number is (which orders, which months, which currency), how many orders it leaves out and why, and one thing this
   data **cannot** answer — written as a claim about the data: "this cannot tell you X, because the data has no Y".
6. `DIAGNOSIS.md`, all five parts, short. **Start the note and `DIAGNOSIS.md` at least ten minutes before the
   neighbour**, finished with step 4 or not. Then the last ten minutes, below, and the Moodle checkpoint.

## Rules

- **Never edit `data/raw/`.** The raw data is the evidence. To test a check on bad data, break a *copy*: never this
  folder's `data/raw/`.
- A check prints its number. `assert n == 0, f"{n} duplicate order_id"` — not `assert n == 0`.
- Sums of money are compared with a tolerance, never `==`, and the message carries the difference.
- You may use AI. If it writes a check for you, ask it what data would make that check fail, and try it. You must be
  able to explain every check you hand in: your neighbour will ask, at the end, without notes.

## Hints, if stuck

Staff will say these over the room at minutes 5, 10, and 15. Read them earlier if you want.

1. Take the first check. Imagine silver orders with one order in it twice. What does the check compute, and does it
   pass? Do the same for the other two: what is the worst silver or gold each one would let through?
2. Count the rows of `data/raw/orders.csv`, and the orders in silver. Which orders are missing? Group the raw file by
   `order_status`.
3. `clean.py` keeps only `delivered` orders, and the report calls them "orders". No check compares the number of
   orders that went in with the number that came out, so nothing noticed. That comparison is the count family.

## Diagnosis note

In `DIAGNOSIS.md`: the template is there. Part 3 is the wrong data each shipped check would pass, and the query that
found the missing orders, with its output. Part 4 is your checks, the decision, and the domain rules. Part 5 is your
checks' output — the run that refused, then the run that passes after your decision — and the reconciliation: which
identity, the two numbers, and where each came from.

## Stretch task

Next month, `orders.csv` arrives with a ninth column. Which of your checks fires? Which stage refuses? Predict before
you test. Then write a schema check: the raw file's columns, from `DESCRIBE`, against the list you expect; stop, and
name any column that is new or missing. Test it by taking one name out of your expected list: the check must fire and
name that column.

## Git thread

`git status` clean means: raw data and scripts committed, generated files ignored. `data/silver/`, `data/gold/` and
`output/` never appear in it. Homework 3 is graded with the fresh-clone test from the lecture — clone, `uv sync`,
`uv run python pipeline.py`, in a new folder — so try it here first: commit your work, clone the project into a new
folder, and run it there. It must run, and every check must pass.

## The last ten minutes

When staff call it — minute 33 of a lab that starts on time, later today, because the lab starts early — finished or
not, turn to the person next to you (three if the row is odd). One of you explains, about a minute: what was wrong,
why, the query that proved it, what you changed, how you know it is right. Point at the screen; do not read the note.
The other asks:

1. **Show me the query that proves it.**
2. **Why was it wrong, not just where?**
3. **The what-if question on the slide.**

Then swap. If either of you is unsure, or you disagree, put a hand up: staff come to you first. Then the answer to
the what-if, for everyone. An unfinished repair is explained the same way: what you found so far.

Before you leave: the lab's **checkpoint on Moodle**. Upload `DIAGNOSIS.md`, with its first line filled in, and
`NOTE.md`. That is what "complete" means; nobody signs you off.

## If you got lost: how to reset

Both of these **destroy work**. Read before running.

**Discard uncommitted changes (destructive)** — throw away edits and new files; keep your commits:

```bash
git restore --staged --worktree .    # every tracked file back to the last commit, staged or not
git clean -fd                        # and remove new, untracked files
```

> ⚠️ Permanently deletes uncommitted changes, staged or not, and any new untracked files.

**Full reset to the starter state (destructive)** — back to exactly what you cloned; throws away your commits too:

```bash
git reset --hard origin/main
git clean -fdx
```

> ⚠️ Discards your local commits and uncommitted changes. The `-x` also removes ignored files — `data/silver/`,
> `data/gold/`, `output/`, the `.venv/` environment — so the folder matches a fresh clone. `uv sync` rebuilds the
> environment in a minute.
