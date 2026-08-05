# Cloudfide Recruitment Task

![Tests](https://github.com/PiotrMiernik/cloudfide-recruitment-task/actions/workflows/tests.yml/badge.svg)

Implementation of the `add_virtual_column` function for creating a calculated
column in a pandas DataFrame.

## Task description

The function receives:

- a pandas DataFrame,
- a mathematical expression referencing two DataFrame columns,
- the name of a new calculated column.

It returns a copy of the original DataFrame with the calculated column.

## Supported operations

The function supports:

- addition: `+`
- subtraction: `-`
- multiplication: `*`

Example:

```python
import pandas as pd

from solution import add_virtual_column


sales = pd.DataFrame(
    {
        "quantity": [10, 3],
        "price": [10, 1],
    }
)

result = add_virtual_column(
    sales,
    "quantity * price",
    "total",
)

print(result)
```

Result:

```text
   quantity  price  total
0        10     10    100
1         3      1      3
```

## Validation rules

- Column labels may contain only letters and underscores.
- The expression must contain exactly two column names and one supported
  operator.
- Both referenced columns must exist in the input DataFrame.
- Additional whitespace in the expression is allowed.
- Invalid input returns an empty DataFrame.
- The input DataFrame is not modified.

## Project structure

```text
.
├── .github/
│   └── workflows/
│       └── tests.yml
├── .gitignore
├── README.md
├── requirements.txt
├── solution.py
├── test_virtual_column.py
└── test_virtual_column_additional.py
```

## Installation

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

Upgrade pip and install the required dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Running tests

Run all tests:

```bash
pytest -v
```

Run only the provided tests:

```bash
pytest test_virtual_column.py -v
```

Run the additional tests:

```bash
pytest test_virtual_column_additional.py -v
```

## Continuous integration

GitHub Actions runs the complete pytest test suite automatically on every push
and pull request to the `main` branch.