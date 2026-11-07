import argparse

from .checks import data_quality_report, load_csv, structuring_flags


def main() -> None:
    p = argparse.ArgumentParser(description="AML data quality and structuring checks")
    p.add_argument("csv", help="path to a transactions CSV")
    p.add_argument("--threshold", type=float, default=10_000)
    p.add_argument("--window-days", type=int, default=14)
    p.add_argument("--min-deposits", type=int, default=3)
    args = p.parse_args()

    con = load_csv(args.csv)
    print("== Data quality ==")
    for name, value in data_quality_report(con).items():
        print(f"{name:22} {value}")

    flags = structuring_flags(
        con, args.threshold, min_deposits=args.min_deposits, window_days=args.window_days
    )
    print(f"\n== Possible structuring ({len(flags)} accounts) ==")
    for acct, n, total, start in flags:
        print(f"{acct}: {n} deposits, total {total:,.2f}, from {start}")


if __name__ == "__main__":
    main()
