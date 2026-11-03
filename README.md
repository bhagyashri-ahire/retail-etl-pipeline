# Retail Sales ETL Pipeline

A Python + SQL ETL pipeline that ingests a raw retail sales CSV, cleans and validates it,
and loads it into a star-schema relational database with data-quality checks,
row-count reconciliation, and audit columns.

## Architecture

```
raw CSV  ->  extract  ->  transform  ->  validate  ->  load (single transaction)  ->  analytics SQL
                                            |                  |
                                      rejected rows     dim_customer, dim_product,
                                      + reasons         fact_sales, etl_audit_log
```

| Stage | File | What it does |
|---|---|---|
| Extract | `src/extract.py` | Reads CSV as strings, checks required columns exist |
| Transform | `src/transform.py` | Trims text, standardises category casing, parses dates/numbers, computes `total_amount` |
| Validate | `src/quality_checks.py` | Rejects rows with missing values, bad quantity/price/discount, duplicates; one reason per row |
| Load | `src/load.py` | Full-refresh load of dimensions + fact in one transaction; writes rejected rows and audit log |
| Orchestrate | `src/pipeline.py`, `dags/retail_etl_dag.py` | CLI entry point; optional Airflow DAG for daily scheduling |

## Data model (star schema)

- `fact_sales` (PK: `order_id, product_id`) -> FKs to `dim_customer`, `dim_product`
- `dim_customer`, `dim_product`
- `rejected_rows` (run_id, order/product id, reject_reason)
- `etl_audit_log` (rows extracted / loaded / rejected, reconciled flag, status)
- Every loaded table carries audit columns: `load_timestamp`, `source_file`

## Data quality & reconciliation

Rules: required fields present, valid date, quantity > 0, price within (0, 100,000], discount in [0, 1],
no duplicate (order_id, product_id). After loading, the pipeline checks
`rows_extracted == rows_loaded + rows_rejected` and fails the run if not.

## Data

`data/generate_sample_data.py` creates a **synthetic** retail dataset (~4.7K rows) with
deliberately injected errors (nulls, duplicates, invalid dates, negative quantities, outliers).
It is not real company data. To use a real public dataset (e.g. Kaggle "Superstore"),
rename its columns to match `EXPECTED_COLUMNS` in `src/extract.py`.

## Run it

```bash
pip install -r requirements.txt
python data/generate_sample_data.py
python -m src.pipeline            # loads into SQLite file retail_dw.db
python -m pytest -q               # run tests
```

Analytics queries: `sql/analysis_queries.sql` (monthly revenue, revenue by category, top customers,
reconciliation, rejection reasons).

**MySQL:** `pip install PyMySQL`, create a database, then
`export DATABASE_URL="mysql+pymysql://user:password@localhost:3306/retail_dw"` before running the pipeline.

**Airflow (optional):** install `apache-airflow`, put this repo on the PYTHONPATH, copy `dags/retail_etl_dag.py`
into your DAGs folder.

## Tech
Python, pandas, SQLAlchemy, SQL (SQLite/MySQL), pytest, GitHub Actions, Apache Airflow (optional DAG)

## Possible next steps
Incremental loads instead of full refresh, a Snowflake target, a dashboard on top of the star schema.
