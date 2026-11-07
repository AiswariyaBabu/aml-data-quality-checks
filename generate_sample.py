"""Create a small synthetic transactions file with known problems and one structuring pattern."""
import csv
import random
from datetime import date, timedelta

random.seed(7)
rows = []
start = date(2025, 1, 1)
for i in range(1, 501):
    rows.append([f"T{i:04d}", f"A{random.randint(1, 40):03d}",
                 start + timedelta(days=random.randint(0, 180)),
                 round(random.uniform(20, 4000), 2),
                 random.choice(["cash_deposit", "transfer", "withdrawal"])])
# planted structuring: account A900 makes four 9,xxx cash deposits in 10 days
for k, amt in enumerate([9500, 9200, 9800, 9400]):
    rows.append([f"S{k:04d}", "A900", date(2025, 3, 1) + timedelta(days=k * 3), amt, "cash_deposit"])
# planted data problems
rows.append(["T0001", "A001", date(2025, 2, 1), 100.0, "transfer"])      # duplicate id
rows.append(["B0001", None, date(2025, 2, 2), 50.0, "transfer"])          # null account
rows.append(["B0002", "A002", date(2025, 2, 3), -25.0, "withdrawal"])     # negative amount

with open("data/sample_transactions.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["txn_id", "account_id", "txn_date", "amount", "txn_type"])
    w.writerows(rows)
print(f"wrote {len(rows)} rows")
