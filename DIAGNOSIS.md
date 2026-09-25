# Diagnosis note

**Explained to:** ______ · **Need help with:** ______ (write *nothing* if none). This line is your Moodle checkpoint.

Fill in every part, short is fine. Parts 3, 4 and 5 are **pasted**: the query you ran and what it returned, not a
description of it. Paste the evidence *before* you change anything — a fix erases the output that proves the cause.

1. **What was the symptom?** Which number or shape was wrong, and what did you compare it to?

2. **What was the actual cause?** Not what you changed — why the old query produced that number.

3. **What evidence showed that?** Paste the queries you ran and their output: the census, `DESCRIBE`, the row count
   before and after, `COUNT(*)` against `COUNT(DISTINCT …)`, the NULL count — whatever showed you the cause.

```text

```

4. **What did you change?** Paste the query (or the lines of the script) as it is now.

```sql

```

5. **How did you verify it?** Paste the check that passes now and would fail if the bug came back, and the
   reconciliation: which identity must hold for this number (a sum, a ratio's two parts, a weighted mean), the two
   numbers that now agree, and where each came from.

```text

```
