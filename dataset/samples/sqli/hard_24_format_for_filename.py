def export_path(table_name, day):
    return "exports/{}_{}.csv".format(table_name, day.isoformat())
