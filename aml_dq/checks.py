"""Data quality checks and a simple structuring (smurfing) rule, run in DuckDB.

Expected columns: txn_id, account_id, txn_date (DATE), amount, txn_type.
"""
import duckdb


def load_csv(path: str) -> duckdb.DuckDBPyConnection:
    """Load a transactions CSV into an in-memory DuckDB table called txns."""
    con = duckdb.connect()
    con.execute(
        "CREATE TABLE txns AS SELECT * FROM read_csv_auto(?, header=true)", [path]
    )
    return con


def data_quality_report(con: duckdb.DuckDBPyConnection) -> dict:
    """Count common data problems so they can be fixed before analysis."""
    q = lambda sql: con.execute(sql).fetchone()[0]
    return {
        "rows": q("SELECT COUNT(*) FROM txns"),
        "null_account_id": q("SELECT COUNT(*) FROM txns WHERE account_id IS NULL"),
        "null_amount": q("SELECT COUNT(*) FROM txns WHERE amount IS NULL"),
        "null_txn_date": q("SELECT COUNT(*) FROM txns WHERE txn_date IS NULL"),
        "non_positive_amount": q("SELECT COUNT(*) FROM txns WHERE amount <= 0"),
        "future_dated": q("SELECT COUNT(*) FROM txns WHERE txn_date > CURRENT_DATE"),
        "duplicate_txn_id": q(
            "SELECT COALESCE(SUM(c - 1), 0) FROM "
            "(SELECT COUNT(*) AS c FROM txns GROUP BY txn_id HAVING COUNT(*) > 1)"
        ),
    }


def structuring_flags(
    con: duckdb.DuckDBPyConnection,
    threshold: float = 10_000,
    margin: float = 0.10,
    min_deposits: int = 3,
    window_days: int = 14,
):
    """Flag accounts with several just-under-threshold cash deposits in a short window.

    A deposit is "near threshold" if it is in [threshold * (1 - margin), threshold).
    An account is flagged if at least `min_deposits` near-threshold deposits fall
    inside any `window_days` window and together reach the threshold.
    Returns rows of (account_id, deposits, total, window_start).
    """
    lo = threshold * (1 - margin)
    window_days = int(window_days)
    sql = f"""
    WITH d AS (
        SELECT DISTINCT txn_id, account_id, txn_date, amount
        FROM txns
        WHERE txn_type = 'cash_deposit'
          AND account_id IS NOT NULL AND txn_date IS NOT NULL
          AND amount >= {lo} AND amount < {threshold}
    ),
    windows AS (
        SELECT a.account_id, a.txn_date AS window_start,
               COUNT(*) AS deposits, SUM(b.amount) AS total
        FROM d a JOIN d b
          ON a.account_id = b.account_id
         AND b.txn_date >= a.txn_date
         AND b.txn_date <= a.txn_date + to_days({window_days})
        GROUP BY a.account_id, a.txn_date
        HAVING COUNT(*) >= {int(min_deposits)} AND SUM(b.amount) >= {threshold}
    )
    SELECT account_id, MAX(deposits) AS deposits,
           MAX(total) AS total, MIN(window_start) AS window_start
    FROM windows GROUP BY account_id ORDER BY total DESC
    """
    return con.execute(sql).fetchall()
