import pandas as pd

EXPECTED_COLUMNS = [
    "order_id", "order_date", "customer_id", "customer_name", "city", "segment",
    "product_id", "product_name", "category", "quantity", "unit_price", "discount",
]


def extract(path: str) -> pd.DataFrame:
    """Read the raw CSV as strings so bad values survive until validation."""
    df = pd.read_csv(path, dtype=str)
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Source file is missing columns: {sorted(missing)}")
    return df[EXPECTED_COLUMNS]
