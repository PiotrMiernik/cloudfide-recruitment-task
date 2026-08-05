""""Implementation of the virtual column recruitment task"""

import operator
import re
from collections.abc import Callable

import pandas as pd

LABEL_PATTERN = re.compile(r"^[A-Za-z_]+$")

ROLE_PATTERN = re.compile(r"^\s*([A-Za-z_]+)\s*([+\-*])\s*([A-Za-z_]+)\s*$")

SUPPORTED_OPERATIONS: dict[str, Callable] = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
}

def _is_valid_label(label: object) -> bool:
    """
    Check wheather a column label contains only letters and underscores.

    Args:
        label: Value to validate as a column label.

    Returns:
        True when the label is valid, otherwise False.
    """
    return isinstance(label, str) and LABEL_PATTERN.fullmatch(label) is not None

def add_virtual_column(
    df: pd.DataFrame,
    role: str,
    new_column: str,
) -> pd.DataFrame:
    """
    Add a calculated virtual column to a copyy of the input DataFrame.

    The role must contain exactly two existing column names separated by one
    supported arithmetic operator: addition, subtraction, or multiplication.

    The input DataFrame is not modified. An empty DataFrame is returned when
    the DataFrame, column labels, or role are invalid.

    Args:
        df: Input pandas DataFrame
        role: Arthmetic expression
        new_column: Name of the calculated column

    Returns: 
        A copy of the input DataFrame with the new, calculated column or an empty DataFrame when the input is invalid.
    """
    if not isinstance(df, pd.DataFrame):
        return pd.DataFrame()

    if not isinstance(role, str):
        return pd.DataFrame()

    if not _is_valid_label(new_column):
        return pd.DataFrame()

    if not all(_is_valid_label(column) for column in df.columns):
        return pd. DataFrame()

    role_match = ROLE_PATTERN.fullmatch(role)

    if role_match is None:
        return pd.DataFrame()

    left_column, operation_symbol, right_column = role_match.groups()

    if left_column not in df.columns or right_column not in df.columns:
        return pd.DataFrame()

    operation = SUPPORTED_OPERATIONS[operation_symbol]

    try:
        result_df = df.copy()
        result_df[new_column] = operation(
            result_df[left_column],
            result_df[right_column],
        )
    except (TypeError, ValueError):
        return pd.DataFrame()

    return result_df