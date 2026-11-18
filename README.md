# Cloudfide Recruitment Task

![Tests](https://github.com/PiotrMiernik/cloudfide-recruitment-task/actions/workflows/tests.yml/badge.svg)

Python implementation of a virtual column calculator and a sales ETL pipeline using pandas.

The project consists of two main components:

1. **Virtual Column Calculator** – creates calculated DataFrame columns using mathematical expressions.
2. **Sales ETL Pipeline** – loads, cleans, validates, and aggregates sales data to calculate total revenue by region.

The project includes automated unit and integration tests using pytest and continuous integration with GitHub Actions.

## 1. Virtual Column Calculator

The `add_virtual_column()` function is implemented in `solution.py`.

### Function signature

```python
def add_virtual_column(
    df: pd.DataFrame,
    role: str,
    new_column: str
) -> pd.DataFrame:
```

The function receives:

- A pandas DataFrame.
- A mathematical expression referencing two DataFrame columns.
- The name of a new calculated column.

It returns a copy of the original DataFrame with the calculated column.

### Supported operations

| Operator | Operation |
|---|---|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |

Example:

```python
import pandas as pd

from solution import add_virtual_column

sales = pd.DataFrame({
    "quantity": [10, 3],
    "price": [10, 1],
})

result = add_virtual_column(
    sales,
    "quantity * price",
    "total",
)

print(result)
```

Output:

```text
   quantity  price  total
0        10     10    100
1         3      1      3
```

### Validation rules

- Column labels may contain only letters and underscores.
- The expression must contain exactly two column names and one supported operator.
- Both referenced columns must exist in the input DataFrame.
- Additional whitespace in the expression is allowed.
- Invalid input returns an empty DataFrame.
- The input DataFrame is not modified.

The function intentionally supports one arithmetic operation per expression.

More complex calculations can be implemented by calling the function multiple times.

## 2. Sales ETL Pipeline

The pipeline is implemented in `pipeline.py`.

Its purpose is to calculate total net sales revenue for each region based on the provided `sales.csv` dataset.

### Pipeline architecture

```text
sales.csv
    |
    v
load_data()
    |
    v
clean_data()
    |
    |-- Remove technical rows
    |-- Remove duplicate records
    |-- Normalize column names
    |-- Standardize region names
    |-- Convert numeric fields
    |-- Handle missing values
    |-- Validate cleaned data
    |
    v
calculate_revenue()
    |
    |-- gross_revenue = quantity * unit_price
    |-- revenue = gross_revenue - discount
    |
    v
aggregate_revenue()
    |
    |-- GROUP BY region
    |-- SUM(revenue)
    |
    v
revenue_by_region.csv
```

### Pipeline functions

| Function | Responsibility |
|---|---|
| `load_data()` | Reads the source CSV file. |
| `clean_data()` | Cleans, standardizes, and validates sales records. |
| `calculate_revenue()` | Calculates gross and net revenue using `add_virtual_column()`. |
| `aggregate_revenue()` | Aggregates net revenue by region. |
| `run_pipeline()` | Orchestrates the ETL process and saves the output CSV. |

### Revenue calculation

Net revenue is calculated as:

```text
gross_revenue = quantity * unit_price
revenue = gross_revenue - discount
```

The pipeline calls `add_virtual_column()` twice because the function supports a single arithmetic operator per expression.

Missing discounts are treated as zero, as specified in the task requirements.

## 3. Data Quality Analysis

The original dataset contains **1,507 rows and 7 columns**.

Data profiling identified several quality issues, including duplicate records, inconsistent formatting, missing values, and negative quantities.

The cleaning process preserves recoverable records rather than dropping them unnecessarily.

### Identified data quality issues

| Data quality issue | Affected rows | Resolution |
|---|---:|---|
| Repeated CSV header | 1 | Removed the technical row. |
| Summary row (`TOTAL`) | 1 | Removed because it is not an individual sales transaction. |
| Exact duplicate records | 5 | Removed duplicate rows. |
| Inconsistent region names | 15 | Trimmed whitespace and standardized capitalization. |
| Quantities containing embedded spaces | 4 | Removed spaces and converted values to integers. |
| Unit prices using comma decimal separators | 7 | Replaced commas with decimal points. |
| Missing unit prices | 5 | Imputed using the product-specific price. |
| Missing discounts | 963 | Replaced missing values with zero. |
| Negative quantities | 6 | Preserved as potential returns or sales adjustments. |

Additionally:

- All 7 original column names were standardized to lowercase snake_case.
- The source file was initially loaded as strings to preserve inconsistent numeric formatting during cleaning.
- Invalid numeric values in the repeated header row were resolved by removing that technical row.
- The invalid or missing dates in the two technical rows were resolved by removing those rows.
- After cleaning, all required fields contain valid, non-null values.
- The final dataset contains no duplicate records.

**Important:** Issue counts describe individual data quality problems and may overlap. They should not be summed to calculate the number of removed records.

### Missing unit price handling

Five sales records contained missing unit prices.

Data profiling showed that each product had exactly one unique valid unit price in the provided dataset.

Therefore, missing prices were filled using the corresponding product's known price.

The pipeline also checks product price consistency before imputation.

If multiple distinct valid prices are detected for the same product, the pipeline raises a `ValueError` rather than choosing an arbitrary replacement.

This rule is specific to the provided dataset and should not be interpreted as a general assumption that product prices never change.

### Negative quantity handling

Six records contain negative quantities.

These records were preserved because they may represent product returns, refunds, or inventory-related sales adjustments.

Removing them would potentially overstate total revenue.

The six records contribute **-913.00** to the calculated net revenue.

This interpretation is an explicit business assumption because the dataset does not contain a separate transaction-type field.

The required revenue formula is applied consistently to positive and negative quantities.

### Data validation

The cleaning function checks that:

- All required columns are present in the cleaned dataset.
- Required values are not missing or invalid after conversion.
- Duplicate records have been removed.
- Product prices are consistent with the dataset-specific imputation assumption.

If validation fails, the pipeline raises an exception instead of silently producing an incomplete result.

### Final dataset

| Metric | Value |
|---|---:|
| Original records | 1,507 |
| Removed technical rows | 2 |
| Removed duplicate records | 5 |
| Final sales records | 1,500 |
| Regions | 5 |
| Missing values after cleaning | 0 |
| Duplicate records after cleaning | 0 |

## 4. Pipeline Results

The pipeline generates `revenue_by_region.csv`.

| Region | Total revenue |
|---|---:|
| Central | 515,824.67 |
| East | 442,219.91 |
| North | 665,897.52 |
| South | 504,036.04 |
| West | 442,268.89 |
| **Total** | **2,570,247.03** |

The output is sorted alphabetically by region.

Revenue values are exported with two decimal places.

The sum of regional revenues was verified against the total revenue calculated from the cleaned transaction-level dataset.

## 5. Project Structure

```text
.
├── .github/
│   └── workflows/
│       └── tests.yml
├── .gitignore
├── README.md
├── requirements.txt
├── solution.py
├── pipeline.py
├── sales.csv
├── revenue_by_region.csv
├── test_virtual_column.py
├── test_virtual_column_additional.py
└── test_pipeline.py
```

## 6. Installation

Clone the repository:

```bash
git clone https://github.com/PiotrMiernik/cloudfide-recruitment-task.git
cd cloudfide-recruitment-task
```

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Upgrade pip and install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 7. Running the Pipeline

Run the complete ETL pipeline:

```bash
python pipeline.py
```

The script reads `sales.csv`, processes the sales records, and creates:

```text
revenue_by_region.csv
```

The aggregated revenue by region is also displayed in the terminal.

The pipeline can be called programmatically with custom input and output paths:

```python
from pipeline import run_pipeline

result = run_pipeline(
    input_path="sales.csv",
    output_path="revenue_by_region.csv",
)

print(result)
```

## 8. Running Tests

Run the complete test suite with a single command:

```bash
python -m pytest -v
```

The project includes **18 automated tests**:

| Test module | Tests | Scope |
|---|---:|---|
| `test_virtual_column.py` | 6 | Tests provided with the recruitment task. |
| `test_virtual_column_additional.py` | 5 | Additional validation and edge-case tests. |
| `test_pipeline.py` | 7 | Data cleaning, revenue calculation, aggregation, and end-to-end pipeline testing. |
| **Total** | **18** | |

Run only the original virtual column tests:

```bash
python -m pytest test_virtual_column.py -v
```

Run the additional virtual column tests:

```bash
python -m pytest test_virtual_column_additional.py -v
```

Run the pipeline tests:

```bash
python -m pytest test_pipeline.py -v
```

The integration test uses pytest's `tmp_path` fixture to create temporary input and output files without modifying the original dataset.

## 9. Continuous Integration

GitHub Actions automatically runs the complete pytest test suite on pushes and pull requests to the `main` branch.

The workflow is defined in:

```text
.github/workflows/tests.yml
```

The workflow provides automated regression testing for both the virtual column calculator and the sales ETL pipeline.

## 10. Assumptions and Limitations

The following assumptions were made due to incomplete business context:

1. **Missing discounts:** An empty discount represents zero discount.
2. **Discount interpretation:** Discounts are absolute monetary amounts applied to the entire order line, not percentages.
3. **Negative quantities:** Negative quantities represent potential returns or sales adjustments and are included in revenue calculations.
4. **Missing prices:** Missing unit prices can be recovered from other records for the same product because each product has a single unique valid price in the provided dataset.
5. **Duplicate records:** Exact duplicate rows are treated as duplicate exports and removed.
6. **Technical rows:** The repeated header and `TOTAL` summary are not sales transactions.
7. **Revenue calculation:** The specified formula is applied without additional tax, currency conversion, or refund-specific adjustments.
8. **Numeric precision:** Calculations use pandas floating-point values. Output is formatted to two decimal places. For production financial systems, fixed-precision decimal arithmetic would generally be preferable.

The solution prioritizes readability, explicit data cleaning rules, testability, and reproducibility.