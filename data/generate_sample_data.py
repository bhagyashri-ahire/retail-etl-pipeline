"""Generate a messy synthetic retail sales CSV so the pipeline has something to clean.

Dirty data is injected on purpose (nulls, duplicates, bad dates, negative values,
outliers, inconsistent casing) to exercise the data-quality checks.
To use a real public dataset (e.g. Kaggle 'Superstore'), rename its columns to
match src/extract.py::EXPECTED_COLUMNS and point the pipeline at the file.
"""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 5000

cities = ["Pune", "Mumbai", "Delhi", "Bengaluru", "Chennai", "Hyderabad"]
segments = ["Consumer", "Corporate", "Small Business"]
catalog = {
    "Electronics": [("P100", "Headphones", 1800), ("P101", "Keyboard", 1200), ("P102", "Webcam", 2500)],
    "Furniture": [("P200", "Office Chair", 6500), ("P201", "Desk Lamp", 900)],
    "Stationery": [("P300", "Notebook", 120), ("P301", "Pen Pack", 80), ("P302", "Stapler", 150)],
}
products = [(pid, name, cat, price) for cat, items in catalog.items() for pid, name, price in items]
customers = [(f"C{1000+i}", f"Customer {i}", str(rng.choice(cities)), str(rng.choice(segments)))
             for i in range(300)]

dates = pd.date_range("2024-01-01", "2024-12-31")
rows = []
for i in range(N):
    c = customers[rng.integers(len(customers))]
    p = products[rng.integers(len(products))]
    rows.append({
        "order_id": f"O{10000 + i // 2}",
        "order_date": pd.Timestamp(rng.choice(dates)).strftime("%Y-%m-%d"),
        "customer_id": c[0], "customer_name": c[1], "city": c[2], "segment": c[3],
        "product_id": p[0], "product_name": p[1], "category": p[2],
        "quantity": int(rng.integers(1, 8)),
        "unit_price": float(p[3]),
        "discount": float(rng.choice([0, 0, 0, 0.05, 0.1, 0.2])),
    })
df = pd.DataFrame(rows).drop_duplicates(["order_id", "product_id"]).reset_index(drop=True)

# --- inject dirt ---
n = len(df)
def pick(k):
    return rng.choice(n, k, replace=False)

df.loc[pick(40), "customer_id"] = None
df.loc[pick(30), "quantity"] = -1
df.loc[pick(20), "unit_price"] = 9_999_999.0
df.loc[pick(25), "order_date"] = "31-13-2024"
df.loc[pick(30), "discount"] = 1.5
upper = pick(60)
df.loc[upper, "category"] = df.loc[upper, "category"].str.upper()
df.loc[pick(40), "city"] = "  Pune "
df = pd.concat([df, df.sample(50, random_state=1)], ignore_index=True)  # duplicates

out = Path(__file__).parent / "raw"
out.mkdir(exist_ok=True)
df.to_csv(out / "retail_sales_raw.csv", index=False)
print(f"Wrote {len(df)} rows to {out / 'retail_sales_raw.csv'}")
