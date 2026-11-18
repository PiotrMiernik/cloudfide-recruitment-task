import pandas as pd
import pytest

from pipeline import (
    clean_data,
    calculate_revenue,
    aggregate_revenue,
    run_pipeline
)


def make_sample_data() -> pd.DataFrame:
    """Create a small dataset with valid raw column names."""
    return pd.DataFrame(
        {
            "Order ID": ["SO-1", "SO-2", "SO-3"],
            "Region": [" north ", "SOUTH", "North"],
            "Product": ["Keyboard", "Mouse", "Keyboard"],
            "Quantity ": ["2", "3", "1"],
            "Unit Price": ["89.00", "29.50", "89.00"],
            "Discount": ["10.00", None, None],
            "Order Date": [
                "2026-01-01",
                "2026-01-02",
                "2026-01-03",
            ],
        }
    )


def test_clean_data_removes_duplicates_and_technical_rows():
    """Verify that technical rows and exact duplicates are removed."""
    df = make_sample_data()

    header = pd.DataFrame(
        [dict(zip(df.columns, df.columns))]
    )

    total = df.iloc[[0]].copy()
    total["Order ID"] = "TOTAL"

    df = pd.concat(
        [df, df.iloc[[0]], header, total],
        ignore_index=True,
    )

    result = clean_data(df)

    assert len(result) == 3
    assert not result.duplicated().any()


def test_clean_data_normalizes_regions():
    """Verify that region names are standardized."""
    df = make_sample_data()

    result = clean_data(df)

    assert result["region"].tolist() == [
        "North",
        "South",
        "North",
    ]


def test_clean_data_converts_numeric_values():
    """Verify conversion of decimal commas and thousands separators."""
    df = make_sample_data()

    df.loc[0, "Quantity "] = "1 762"
    df.loc[1, "Unit Price"] = "29,50"

    result = clean_data(df)

    assert result.loc[0, "quantity"] == 1762
    assert result.loc[1, "unit_price"] == 29.50


def test_clean_data_fills_missing_values():
    """Verify missing discounts and product prices are imputed."""
    df = make_sample_data()

    df.loc[2, "Unit Price"] = None

    result = clean_data(df)

    assert result.loc[2, "unit_price"] == 89.00
    assert result.loc[1, "discount"] == 0
    assert result.loc[2, "discount"] == 0


def test_calculate_revenue_preserves_negative_quantities():
    """Verify that returns reduce revenue."""
    df = make_sample_data()

    df.loc[0, "Quantity "] = "-2"

    cleaned = clean_data(df)
    result = calculate_revenue(cleaned)

    assert result.loc[0, "quantity"] == -2
    assert result.loc[0, "revenue"] == pytest.approx(-188.00)


def test_aggregate_revenue():
    """Verify that revenue is correctly aggregated by region."""
    df = make_sample_data()

    cleaned = clean_data(df)
    revenue_df = calculate_revenue(cleaned)
    result = aggregate_revenue(revenue_df)

    expected = {
        "North": 257.00,
        "South": 88.50,
    }

    actual = dict(zip(result["region"], result["revenue"]))

    assert actual == pytest.approx(expected)

def test_run_pipeline_end_to_end(tmp_path):
    """Verify that the pipeline reads, processes, and saves sales data."""
    input_path = tmp_path / "sales.csv"
    output_path = tmp_path / "revenue_by_region.csv"

    make_sample_data().to_csv(input_path, index=False)

    result = run_pipeline(input_path, output_path)

    assert output_path.exists()

    saved_result = pd.read_csv(output_path)

    expected = pd.DataFrame({
        "region": ["North", "South"],
        "revenue": [257.00, 88.50],
    })

    pd.testing.assert_frame_equal(
        saved_result,
        expected,
    )

    pd.testing.assert_frame_equal(
        result,
        expected,
    )