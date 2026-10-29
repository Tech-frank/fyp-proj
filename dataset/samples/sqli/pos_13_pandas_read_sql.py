import pandas as pd


def sales_for_region(engine, region):
    return pd.read_sql(f"SELECT month, revenue FROM sales WHERE region = '{region}'", engine)
