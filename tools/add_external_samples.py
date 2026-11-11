"""Append dataset/metadata_external.csv to dataset/metadata.csv (safe to run twice).

Run from the project root:  python tools/add_external_samples.py
Adds the `origin` column if metadata.csv doesn't have it yet. Rows whose
sample_id is already present are skipped, so your review marks are kept.
"""
import csv
from pathlib import Path

main = Path("dataset/metadata.csv")
extra = Path("dataset/metadata_external.csv")

with main.open(newline="", encoding="utf-8-sig") as fh:
    reader = csv.DictReader(fh)
    columns = list(reader.fieldnames)
    rows = list(reader)
with extra.open(newline="", encoding="utf-8-sig") as fh:
    new_reader = csv.DictReader(fh)
    new_rows = list(new_reader)
    for column in new_reader.fieldnames:
        if column not in columns:
            columns.append(column)

existing = {r["sample_id"] for r in rows}
added = [r for r in new_rows if r["sample_id"] not in existing]
with main.open("w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows + added)
print(f"added {len(added)} external samples; metadata.csv now has {len(rows) + len(added)} rows")
