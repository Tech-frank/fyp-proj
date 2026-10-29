import csv


def column_total(path, column):
    with open(path, newline="", encoding="utf-8") as fh:
        return sum(float(row[column]) for row in csv.DictReader(fh))
