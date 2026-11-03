"""Run the full ETL:  python -m src.pipeline [path_to_csv]"""
import logging
import sys
import uuid
from pathlib import Path

from src.extract import extract
from src.load import create_schema, get_engine, load
from src.quality_checks import validate
from src.transform import transform

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("etl")
DEFAULT_SOURCE = "data/raw/retail_sales_raw.csv"


def run(source: str = DEFAULT_SOURCE, db_url: str | None = None) -> dict:
    run_id = uuid.uuid4().hex[:12]
    log.info("run_id=%s source=%s", run_id, source)

    raw = extract(source)
    log.info("Extracted %d rows", len(raw))

    clean, rejected = validate(transform(raw))
    log.info("Validation: %d clean, %d rejected", len(clean), len(rejected))
    for reason, n in rejected["reject_reason"].value_counts().items():
        log.info("  rejected %-25s %d", reason, n)

    engine = get_engine(db_url)
    create_schema(engine)
    result = load(engine, clean, rejected, run_id, Path(source).name, len(raw))
    log.info("Load result: %s", result)
    if not result["reconciled"]:
        raise RuntimeError("Row counts do not reconcile: extracted != loaded + rejected")
    return result


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SOURCE)
