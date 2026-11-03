import pandas as pd


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise text, cast types, derive total_amount.

    Unparseable values become NaN/NaT (never silently 'fixed') so the quality
    checks can reject them and report why."""
    out = df.copy()
    for col in ["order_id", "customer_id", "customer_name", "city", "segment",
                "product_id", "product_name", "category"]:
        out[col] = out[col].str.strip()
    out["category"] = out["category"].str.title()
    out["order_date"] = pd.to_datetime(out["order_date"], format="%Y-%m-%d", errors="coerce")
    for col in ["quantity", "unit_price", "discount"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["total_amount"] = (out["quantity"] * out["unit_price"] * (1 - out["discount"])).round(2)
    return out
