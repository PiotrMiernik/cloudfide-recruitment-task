from pathlib import Path

import pandas as pd

from solution import add_virtual_column


def load_data(file_path: str | Path) -> pd.DataFrame:
    """Load raw sales data from a CSV file."""
    return pd.read_csv(file_path, dtype=str)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate raw sales records."""

    df = df.copy()

    # 1. Remove technical rows.
    df = df[
        (df["Order ID"] != "Order ID")
        & (df["Order ID"] != "TOTAL")
    ].copy()

    # 2. Remove exact duplicates.
    df = df.drop_duplicates()

    # 3. Standardize column names.
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # 4. Normalize text values.
    df["region"] = df["region"].str.strip().str.title()
    df["product"] = df["product"].str.strip()

    # 5. Convert quantity to numeric.
    df["quantity"] = pd.to_numeric(
        df["quantity"].str.replace(" ", "", regex=False),
        errors="coerce",
    )

    # 6. Convert unit price to numeric.
    df["unit_price"] = pd.to_numeric(
        df["unit_price"].str.replace(",", ".", regex=False),
        errors="coerce",
    )

    # 7. Convert discount to numeric and fill missing values.
    df["discount"] = pd.to_numeric(
        df["discount"],
        errors="coerce",
    ).fillna(0)

    # 8. Fill missing prices using product-specific prices.
    # Validate product price consistency before imputation.
    price_counts = df.groupby("product")["unit_price"].nunique()

    if (price_counts > 1).any():
        raise ValueError(
            "Multiple unit prices found for the same product."
        )

    product_prices = df.groupby("product")["unit_price"].transform("median")

    df["unit_price"] = df["unit_price"].fillna(product_prices)

    # 9. Convert order dates.
    df["order_date"] = pd.to_datetime(
        df["order_date"],
        format="%Y-%m-%d",
        errors="coerce",
    )

    # 10. Validate cleaned data.
    required_columns = [
        "order_id",
        "region",
        "product",
        "quantity",
        "unit_price",
        "discount",
        "order_date",
    ]

    if df[required_columns].isna().any().any():
        raise ValueError("Cleaned data contains missing or invalid values.")

    if df.duplicated().any():
        raise ValueError("Cleaned data contains duplicate records.")

    return df

def calculate_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate gross and net revenue using add_virtual_column."""

    df = add_virtual_column(
        df,
        "quantity * unit_price",
        "gross_revenue",
    )

    df = add_virtual_column(
        df,
        "gross_revenue - discount",
        "revenue",
    )

    return df

def aggregate_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate total net revenue by region."""

    return (
        df.groupby("region", as_index=False)["revenue"]
        .sum()
        .sort_values("region")
        .reset_index(drop=True)
    )

def run_pipeline(
    input_path: str | Path = "sales.csv",
    output_path: str | Path = "revenue_by_region.csv",
) -> pd.DataFrame:
    """Run the sales ETL pipeline and save aggregated revenue."""

    raw_df = load_data(input_path)

    cleaned_df = clean_data(raw_df)

    revenue_df = calculate_revenue(cleaned_df)

    result_df = aggregate_revenue(revenue_df)

    result_df.to_csv(
        output_path,
        index=False,
        float_format="%.2f",
    )

    return result_df

if __name__ == "__main__":
    result = run_pipeline()

    print("\nREVENUE BY REGION")
    print(result.to_string(index=False))

    print("\nOutput saved to revenue_by_region.csv")


