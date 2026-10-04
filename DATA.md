# Data in this repository

Everything under `data/raw/` is real, public data, committed on purpose and **never edited**. Where it came from, its license, and exactly what was changed for this course:

The names of places in these files are their publishers'. Their use in this course says nothing about the political status of any place.

## Brazilian E-Commerce Public Dataset by Olist — a selected subset

**Source:** Olist, *Brazilian E-Commerce Public Dataset by Olist*, Kaggle,
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce — the original eight CSV files, e.g.
`https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce` (fetched 2026-09-19, SHA-256 `8df58ef3d2d7e994…`).

**License:** **CC BY-NC-SA 4.0**. Attribution: *Brazilian E-Commerce Public Dataset by Olist* (2018).
NonCommercial: this subset is redistributed for non-commercial teaching only. ShareAlike: this subset is an
adaptation and is shared under the same license, CC BY-NC-SA 4.0. The course's own code and text are not
relicensed by it.

**Changes made for this course — this is a SELECTED sample, not a representative one.** 2,653 of the 99,441 orders:
a deterministic 2.5% of orders (by a hash of `order_id`), **plus** every order that contains an item whose
category has no English translation, 40 orders containing items with no category, 25 orders with more than one
review, the orders sharing 15 review ids that span several orders, the one order with no payment row, every order
placed from 1 September 2018 on, and 30 orders from before November 2016. Every child row (items, payments,
reviews) of a selected order is included, and every customer, product, and seller those rows reference, so no
row in this subset refers to a row that is missing. The translation table is complete. No values were edited.
Selected, rather than random, because a random sample of this size can lose the rare situations the labs are
about.

## Files

| File | Bytes | SHA-256 |
|---|---:|---|
| `customers.csv` | 229,192 | `72269ff7db73a8b7…` |
| `order_items.csv` | 400,390 | `be335a108223b0bd…` |
| `order_payments.csv` | 151,384 | `a17effc15a7f5bf8…` |
| `orders.csv` | 463,359 | `047d88d8270f9b76…` |
| `products.csv` | 157,085 | `2e7fb3cec9c6d0b1…` |
