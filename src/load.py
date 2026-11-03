import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def get_engine(url: str | None = None):
    """Defaults to a local SQLite file. For MySQL set DATABASE_URL, e.g.
    mysql+pymysql://user:password@localhost:3306/retail_dw"""
    url = url or os.getenv("DATABASE_URL", "sqlite:///retail_dw.db")
    return create_engine(url)


def create_schema(engine):
    ddl = (SQL_DIR / "schema.sql").read_text()
    with engine.begin() as conn:
        for stmt in ddl.split(";"):
            if stmt.strip():
                conn.execute(text(stmt))


def load(engine, clean: pd.DataFrame, rejected: pd.DataFrame,
         run_id: str, source_file: str, rows_extracted: int) -> dict:
    """Full-refresh load of dimensions + fact, rejected rows, and an audit log entry.

    Everything runs in ONE transaction: either all tables update or none do."""
    now = datetime.now().replace(microsecond=0)
    audit = {"load_timestamp": now, "source_file": source_file}

    dim_c = (clean[["customer_id", "customer_name", "city", "segment"]]
             .drop_duplicates("customer_id").assign(**audit))
    dim_p = (clean[["product_id", "product_name", "category"]]
             .drop_duplicates("product_id").assign(**audit))
    fact = clean[["order_id", "product_id", "customer_id", "order_date", "quantity",
                  "unit_price", "discount", "total_amount"]].assign(**audit)
    fact["order_date"] = fact["order_date"].dt.date
    rej = rejected[["order_id", "product_id", "reject_reason"]].assign(
        run_id=run_id, load_timestamp=now)

    loaded, n_rej = len(fact), len(rej)
    reconciled = int(rows_extracted == loaded + n_rej)
    status = "SUCCESS" if reconciled else "RECONCILIATION_FAILED"

    with engine.begin() as conn:
        for t in ["fact_sales", "dim_customer", "dim_product"]:  # children first
            conn.execute(text(f"DELETE FROM {t}"))
        dim_c.to_sql("dim_customer", conn, if_exists="append", index=False)
        dim_p.to_sql("dim_product", conn, if_exists="append", index=False)
        fact.to_sql("fact_sales", conn, if_exists="append", index=False)
        rej.to_sql("rejected_rows", conn, if_exists="append", index=False)
        pd.DataFrame([{
            "run_id": run_id, "source_file": source_file, "rows_extracted": rows_extracted,
            "rows_loaded": loaded, "rows_rejected": n_rej, "reconciled": reconciled,
            "status": status, "run_timestamp": now,
        }]).to_sql("etl_audit_log", conn, if_exists="append", index=False)

    return {"extracted": rows_extracted, "loaded": loaded, "rejected": n_rej,
            "reconciled": bool(reconciled), "status": status}
