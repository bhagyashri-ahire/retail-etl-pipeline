import pandas as pd

MAX_PRICE = 100_000
MAX_QTY = 1_000


def validate(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split into (clean, rejected).

    Each rejected row gets exactly ONE reason (the first rule it fails), so
    extracted = loaded + rejected always reconciles."""
    df = df.copy()
    df["reject_reason"] = None

    def flag(mask, reason):
        df.loc[mask & df["reject_reason"].isna(), "reject_reason"] = reason

    required = ["order_id", "product_id", "customer_id", "customer_name",
                "product_name", "category", "order_date", "quantity", "unit_price", "discount"]
    flag(df[required].isna().any(axis=1), "missing_required_value")
    flag(df["quantity"] <= 0, "non_positive_quantity")
    flag(df["quantity"] > MAX_QTY, "quantity_out_of_range")
    flag((df["unit_price"] <= 0) | (df["unit_price"] > MAX_PRICE), "price_out_of_range")
    flag((df["discount"] < 0) | (df["discount"] > 1), "invalid_discount")
    flag(df.duplicated(["order_id", "product_id"], keep="first"), "duplicate_order_line")

    rejected = df[df["reject_reason"].notna()].copy()
    clean = df[df["reject_reason"].isna()].drop(columns="reject_reason")
    return clean, rejected
