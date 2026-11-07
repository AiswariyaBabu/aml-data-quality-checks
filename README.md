# AML Data Quality Checks

A small Python + DuckDB package that does two things on a transactions file:

1. **Data quality report**: nulls, duplicate transaction IDs, non-positive amounts, future-dated rows.
2. **Structuring flag**: accounts with several cash deposits just under a reporting threshold inside a short window (default: 3+ deposits between 9,000 and 10,000 within 14 days, totalling 10,000 or more).

It follows on from my [AML visualization project](https://github.com/AiswariyaBabu/AMLVisualization), which used DuckDB and Power Query on the 9.5M-row SAML-D dataset. This repo is the same idea as reusable, tested Python.

## Run it

```bash
python -m venv AMLEnv
source ./AMLEnv/bin/activate
pip install -r requirements.txt
python generate_sample.py                      # makes data/sample_transactions.csv
python -m aml_dq data/sample_transactions.csv  # prints the report
pytest                                         # runs the tests
```

Input columns: `txn_id, account_id, txn_date, amount, txn_type`. To try it on SAML-D, map its columns to these names first.

## Notes

- Rules are simple and fixed, meant for screening, not a replacement for a real AML system.
- SQL runs in DuckDB, so large CSVs do not need to fit in Excel or pandas memory.
