import pandas as pd
import pytest

from src.pipeline import run
from src.quality_checks import validate
from src.transform import transform


def make_df(**overrides):
    row = {"order_id": "O1", "order_date": "2024-05-01", "customer_id": "C1",
           "customer_name": "A", "city": " Pune ", "segment": "Consumer",
           "product_id": "P1", "product_name": "Pen", "category": "STATIONERY",
           "quantity": "2", "unit_price": "100", "discount": "0.1"}
    row.update(overrides)
    return pd.DataFrame([row])


def test_transform_cleans_and_computes_total():
    out = transform(make_df())
    assert out.loc[0, "city"] == "Pune"
    assert out.loc[0, "category"] == "Stationery"
    assert out.loc[0, "total_amount"] == 180.0


@pytest.mark.parametrize("override,reason", [
    ({"quantity": "-1"}, "non_positive_quantity"),
    ({"unit_price": "9999999"}, "price_out_of_range"),
    ({"discount": "1.5"}, "invalid_discount"),
    ({"order_date": "31-13-2024"}, "missing_required_value"),
    ({"customer_id": None}, "missing_required_value"),
])
def test_bad_rows_are_rejected(override, reason):
    clean, rejected = validate(transform(make_df(**override)))
    assert clean.empty
    assert rejected.iloc[0]["reject_reason"] == reason


def test_duplicates_rejected_keep_first():
    clean, rejected = validate(transform(pd.concat([make_df(), make_df()], ignore_index=True)))
    assert len(clean) == 1 and len(rejected) == 1


def test_end_to_end_reconciles(tmp_path):
    good, bad = make_df(), make_df(order_id="O2", quantity="-5")
    csv = tmp_path / "in.csv"
    pd.concat([good, bad, good], ignore_index=True).to_csv(csv, index=False)
    result = run(str(csv), db_url=f"sqlite:///{tmp_path / 't.db'}")
    assert result["reconciled"]
    assert (result["extracted"], result["loaded"], result["rejected"]) == (3, 1, 2)
