import duckdb

from aml_dq import data_quality_report, structuring_flags


def make_con(rows):
    con = duckdb.connect()
    con.execute(
        "CREATE TABLE txns (txn_id VARCHAR, account_id VARCHAR, txn_date DATE, "
        "amount DOUBLE, txn_type VARCHAR)"
    )
    con.executemany("INSERT INTO txns VALUES (?, ?, ?, ?, ?)", rows)
    return con


def test_quality_report_finds_problems():
    con = make_con([
        ("1", "A", "2025-01-01", 100, "transfer"),
        ("1", "A", "2025-01-01", 100, "transfer"),   # duplicate id
        ("2", None, "2025-01-02", 50, "transfer"),     # null account
        ("3", "B", "2025-01-03", -5, "withdrawal"),    # non-positive
    ])
    r = data_quality_report(con)
    assert r["rows"] == 4
    assert r["duplicate_txn_id"] == 1
    assert r["null_account_id"] == 1
    assert r["non_positive_amount"] == 1


def test_structuring_flagged_inside_window():
    con = make_con([
        ("1", "A", "2025-03-01", 9500, "cash_deposit"),
        ("2", "A", "2025-03-04", 9200, "cash_deposit"),
        ("3", "A", "2025-03-08", 9800, "cash_deposit"),
    ])
    flags = structuring_flags(con)
    assert [f[0] for f in flags] == ["A"]


def test_not_flagged_when_spread_out():
    con = make_con([
        ("1", "A", "2025-03-01", 9500, "cash_deposit"),
        ("2", "A", "2025-04-04", 9200, "cash_deposit"),
        ("3", "A", "2025-05-08", 9800, "cash_deposit"),
    ])
    assert structuring_flags(con) == []


def test_ignores_small_and_non_cash():
    con = make_con([
        ("1", "A", "2025-03-01", 500, "cash_deposit"),
        ("2", "A", "2025-03-02", 9500, "transfer"),
        ("3", "A", "2025-03-03", 9500, "transfer"),
    ])
    assert structuring_flags(con) == []
