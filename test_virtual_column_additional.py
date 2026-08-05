"""Additional tests for add_virtual_column."""

import pandas as pd

from solution import add_virtual_column


def test_input_dataframe_is_not_modified():
    # Checks that the function returns a new DataFrame
    # without modifying the original input DataFrame.
    df = pd.DataFrame(
        {
            "quantity": [2, 3],
            "price": [10, 20],
        }
    )
    original_df = df.copy(deep=True)

    result = add_virtual_column(
        df,
        "quantity * price",
        "total",
    )

    assert df.equals(original_df)
    assert "total" not in df.columns
    assert result["total"].tolist() == [20, 60]


def test_returns_empty_dataframe_when_role_has_multiple_operators():
    # Checks that expressions containing more than one operator
    # are rejected as invalid.
    df = pd.DataFrame(
        {
            "quantity": [2],
            "price": [10],
            "tax": [1],
        }
    )

    result = add_virtual_column(
        df,
        "quantity * price + tax",
        "total",
    )

    assert result.empty


def test_returns_empty_dataframe_for_unsupported_operator():
    # Checks that an unsupported arithmetic operator
    # such as division returns an empty DataFrame.
    df = pd.DataFrame(
        {
            "quantity": [2],
            "price": [10],
        }
    )

    result = add_virtual_column(
        df,
        "price / quantity",
        "average",
    )

    assert result.empty


def test_returns_empty_dataframe_for_non_string_role():
    # Checks that the function safely rejects a role
    # that is not provided as a string.
    df = pd.DataFrame(
        {
            "quantity": [2],
            "price": [10],
        }
    )

    result = add_virtual_column(
        df,
        None,
        "total",
    )

    assert result.empty


def test_calculation_on_empty_dataframe_with_valid_columns():
    # Checks that a valid new column is added correctly
    # even when the input DataFrame contains no rows.
    df = pd.DataFrame(columns=["quantity", "price"])

    result = add_virtual_column(
        df,
        "quantity * price",
        "total",
    )

    assert list(result.columns) == ["quantity", "price", "total"]
    assert result.empty 